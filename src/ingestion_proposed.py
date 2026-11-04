# =============================================================================
# Data Ingestion (proposed revision)
# =============================================================================
"""
Ingestion utilities for the MetroPT-3 Telemetry-to-Insight project.

This module is responsible for:

1. Loading project configuration from YAML.
2. Downloading the public MetroPT-3 source archive when required.
3. Extracting the telemetry CSV from the archive.
4. Persisting the source telemetry as Parquet for local reuse.
5. Creating a configured development-period extract.

Reuse rules:

- Parquet files are written atomically (temporary file, then rename), so an
  interrupted run never leaves a partial dataset at the final path.
- The raw dataset is reused whenever it exists.
- The development extract is reused only when a metadata file written next
  to it records the same extraction period and raw source as the current
  configuration. Otherwise it is rebuilt.
- Empty development extracts are rejected rather than persisted.
"""

import io
import json
import logging
import os
import zipfile
from pathlib import Path

import pandas as pd
import requests
import yaml


# Create a module-specific logger so log records identify their source.
logger = logging.getLogger(__name__)

# Resolve the project root from the location of this module.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Format used by the MetroPT-3 source timestamps. The timestamp column is
# stored as a string, so filter bounds must use exactly this format for
# lexicographic comparison to match chronological order.
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


def load_config():
    """Load and return the project configuration from ``config/config.yaml``."""

    config_path = PROJECT_ROOT / "config" / "config.yaml"

    logger.info("Loading project configuration from %s.", config_path)

    try:
        with open(config_path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)

    except FileNotFoundError:
        logger.exception("Configuration file not found: %s", config_path)
        raise

    except yaml.YAMLError:
        logger.exception("Failed to parse YAML configuration: %s", config_path)
        raise

    logger.info("Project configuration loaded successfully.")

    return config


def _write_parquet_atomic(df, path):
    """
    Write ``df`` to ``path`` so the final file is either complete or absent.

    Data is written to a temporary file in the same directory and then moved
    into place with ``os.replace``, which is atomic on the same filesystem.
    """

    path = Path(path)
    tmp_path = path.with_name(path.name + ".tmp")

    try:
        df.to_parquet(tmp_path, engine="pyarrow", index=False)
        os.replace(tmp_path, path)

    except BaseException:
        # Remove any partial temporary file, including on KeyboardInterrupt.
        tmp_path.unlink(missing_ok=True)
        raise


def _normalise_timestamp(value, name):
    """
    Return ``value`` formatted as ``YYYY-MM-DD HH:MM:SS``.

    Accepts any value ``pd.Timestamp`` understands, including strings such as
    ``"2020-3-1"`` and ``datetime`` objects produced by unquoted YAML dates.
    """

    try:
        timestamp = pd.Timestamp(value)

    except (TypeError, ValueError) as error:
        raise ValueError(
            f"Invalid development {name}: {value!r}"
        ) from error

    if pd.isna(timestamp):
        raise ValueError(f"Invalid development {name}: {value!r}")

    return timestamp.strftime(TIMESTAMP_FORMAT)


def _metadata_path(development_path):
    """Return the metadata file path stored next to the development extract."""

    return development_path.with_name(development_path.name + ".meta.json")


def _read_metadata(metadata_path):
    """Return stored extract metadata, or ``None`` if missing or unreadable."""

    try:
        with open(metadata_path, "r", encoding="utf-8") as file:
            return json.load(file)

    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _write_metadata_atomic(metadata, metadata_path):
    """Write extract metadata atomically, mirroring the Parquet writer."""

    tmp_path = metadata_path.with_name(metadata_path.name + ".tmp")

    try:
        with open(tmp_path, "w", encoding="utf-8") as file:
            json.dump(metadata, file, indent=2)
        os.replace(tmp_path, metadata_path)

    except BaseException:
        tmp_path.unlink(missing_ok=True)
        raise


def ingest_raw_data(config):
    """
    Create the raw MetroPT-3 Parquet dataset when it does not already exist.

    The source ZIP archive is downloaded from the configured public endpoint,
    the required telemetry CSV is extracted in memory, and the resulting
    dataset is persisted locally as Parquet using an atomic write.

    If the raw Parquet file already exists, the existing dataset is reused.
    """

    raw_path = PROJECT_ROOT / config["data"]["raw_parquet"]

    # Reuse the existing raw dataset to avoid unnecessary network and
    # processing cost on repeated pipeline runs. Atomic writes guarantee
    # that an existing file is a complete one.
    if raw_path.exists():
        logger.info(
            "Raw dataset already exists. Reusing local file: %s",
            raw_path,
        )
        return

    # Ensure the configured raw-data directory exists before persistence.
    raw_path.parent.mkdir(parents=True, exist_ok=True)

    url = config["source"]["dataset_url"]
    csv_filename = config["source"]["csv_filename"]
    chunk_size = config["ingestion"]["download_chunk_size_bytes"]
    timeout = config["ingestion"]["request_timeout_seconds"]

    logger.info("Downloading MetroPT-3 source archive.")

    zip_buffer = io.BytesIO()

    try:
        with requests.get(
            url,
            stream=True,
            timeout=timeout,
            verify=False, # Temporary SSl bypass (unchanged from original)
        ) as response:

            response.raise_for_status()

            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    zip_buffer.write(chunk)

    except requests.RequestException:
        logger.exception(
            "Failed to download MetroPT-3 source archive from %s.",
            url,
        )
        raise

    logger.info("MetroPT-3 source archive downloaded successfully.")

    # Reset the in-memory buffer before reading the ZIP archive.
    zip_buffer.seek(0)

    logger.info("Extracting telemetry CSV from source archive.")

    try:
        with zipfile.ZipFile(zip_buffer) as archive:

            with archive.open(csv_filename) as csv_file:
                df = pd.read_csv(csv_file)

    except zipfile.BadZipFile:
        logger.exception(
            "Downloaded source archive is not a valid ZIP file."
        )
        raise

    except KeyError:
        logger.exception(
            "Telemetry CSV '%s' was not found in the source archive.",
            csv_filename,
        )
        raise

    logger.info(
        "Telemetry CSV extracted successfully: %s rows.",
        f"{len(df):,}",
    )

    logger.info("Persisting raw telemetry dataset to %s.", raw_path)

    _write_parquet_atomic(df, raw_path)

    logger.info(
        "Raw telemetry dataset created successfully: %s",
        raw_path,
    )


def create_development_data(config):
    """
    Create the configured development extract from the raw telemetry dataset.

    The development period is selected directly from the persisted raw
    Parquet dataset using the configured start and end timestamps, which are
    normalised to the source timestamp format before filtering.

    No cleaning, imputation or feature engineering is performed at this stage.

    The existing extract is reused only if its metadata file matches the
    current extraction period and raw source. Otherwise it is rebuilt.

    Raises:
        ValueError: If the configured timestamps are invalid, the start is
            after the end, or the configured period contains no rows.
        FileNotFoundError: If the raw dataset does not exist.
    """

    raw_path = PROJECT_ROOT / config["data"]["raw_parquet"]
    development_path = (
        PROJECT_ROOT / config["data"]["development_parquet"]
    )
    metadata_path = _metadata_path(development_path)

    start_timestamp = _normalise_timestamp(
        config["development"]["start_timestamp"], "start_timestamp"
    )
    end_timestamp = _normalise_timestamp(
        config["development"]["end_timestamp"], "end_timestamp"
    )

    # Fixed-width ISO-style strings compare in chronological order.
    if start_timestamp > end_timestamp:
        raise ValueError(
            "Development start_timestamp must not be after end_timestamp: "
            f"{start_timestamp} > {end_timestamp}"
        )

    # Describes the inputs that determine the extract's contents.
    expected_metadata = {
        "start_timestamp": start_timestamp,
        "end_timestamp": end_timestamp,
        "raw_parquet": config["data"]["raw_parquet"],
    }

    # Reuse an existing development extract only when it was built from the
    # same configuration, keeping repeated runs efficient and reproducible.
    if development_path.exists():

        if _read_metadata(metadata_path) == expected_metadata:
            logger.info(
                "Development dataset already exists for the configured "
                "period. Reusing local file: %s",
                development_path,
            )
            return

        logger.warning(
            "Development dataset at %s does not match the configured "
            "period (%s to %s) or has no metadata. Rebuilding.",
            development_path,
            start_timestamp,
            end_timestamp,
        )

    if not raw_path.exists():
        logger.error(
            "Raw dataset required for development extraction was not found: %s",
            raw_path,
        )
        raise FileNotFoundError(
            f"Raw dataset not found: {raw_path}"
        )

    # Ensure the configured development-data directory exists.
    development_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    logger.info(
        "Creating development dataset for configured period: %s to %s.",
        start_timestamp,
        end_timestamp,
    )

    development_df = pd.read_parquet(
        raw_path,
        engine="pyarrow",
        filters=[
            ("timestamp", ">=", start_timestamp),
            ("timestamp", "<=", end_timestamp),
        ],
    )

    # An empty extract would be cached and silently reused downstream.
    if development_df.empty:
        logger.error(
            "Development extraction returned no rows for %s to %s.",
            start_timestamp,
            end_timestamp,
        )
        raise ValueError(
            "Development extract is empty for configured period: "
            f"{start_timestamp} to {end_timestamp}"
        )

    # Remove stale metadata first. If the run stops between the Parquet and
    # metadata writes, the extract has no metadata and will be rebuilt,
    # rather than being reused under the previous period's metadata.
    metadata_path.unlink(missing_ok=True)

    _write_parquet_atomic(development_df, development_path)
    _write_metadata_atomic(expected_metadata, metadata_path)

    logger.info(
        "Development dataset created successfully: %s rows.",
        f"{len(development_df):,}",
    )

    logger.info(
        "Development dataset persisted to %s.",
        development_path,
    )


if __name__ == "__main__":

    config = load_config()

    #ingest_raw_data(config)

    create_development_data(config)
