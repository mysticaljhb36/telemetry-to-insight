# =============================================================================
# Data Ingestion
# =============================================================================
"""
Ingestion utilities for the MetroPT-3 Telemetry-to-Insight project.

This module is responsible for:

1. Loading project configuration from YAML.
2. Downloading the public MetroPT-3 source archive when required.
3. Extracting the telemetry CSV from the archive.
4. Persisting the source telemetry as Parquet for local reuse.
5. Creating a configured development-period extract.

The ingestion steps are idempotent: existing raw and development datasets
are reused rather than repeatedly downloaded or recreated.
"""

import io
import logging
import zipfile
from pathlib import Path

import pandas as pd
import requests
import yaml


# Create a module-specific logger so log records identify their source.
logger = logging.getLogger(__name__)

# Resolve the project root from the location of this module.
PROJECT_ROOT = Path(__file__).resolve().parent.parent


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


def ingest_raw_data(config):
    """
    Create the raw MetroPT-3 Parquet dataset when it does not already exist.

    The source ZIP archive is downloaded from the configured public endpoint,
    the required telemetry CSV is extracted in memory, and the resulting
    dataset is persisted locally as Parquet.

    If the raw Parquet file already exists, the existing dataset is reused.
    """

    raw_path = PROJECT_ROOT / config["data"]["raw_parquet"]

    # Reuse the existing raw dataset to avoid unnecessary network and
    # processing cost on repeated pipeline runs.
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

    df.to_parquet(
        raw_path,
        engine="pyarrow",
        index=False,
    )

    logger.info(
        "Raw telemetry dataset created successfully: %s",
        raw_path,
    )


def create_development_data(config):
    """
    Create the configured development extract from the raw telemetry dataset.

    The development period is selected directly from the persisted raw
    Parquet dataset using the configured start and end timestamps.

    No cleaning, imputation or feature engineering is performed at this stage.

    If the development Parquet file already exists, the existing dataset is
    reused.
    """

    raw_path = PROJECT_ROOT / config["data"]["raw_parquet"]
    development_path = (
        PROJECT_ROOT / config["data"]["development_parquet"]
    )

    start_timestamp = config["development"]["start_timestamp"]
    end_timestamp = config["development"]["end_timestamp"]

    # Reuse an existing development extract to keep repeated pipeline runs
    # efficient and reproducible.
    if development_path.exists():
        logger.info(
            "Development dataset already exists. Reusing local file: %s",
            development_path,
        )
        return

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

    development_df.to_parquet(
        development_path,
        engine="pyarrow",
        index=False,
    )

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

    ingest_raw_data(config)

    create_development_data(config)