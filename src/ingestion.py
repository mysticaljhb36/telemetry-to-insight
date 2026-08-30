# src/ingestion.py

from pathlib import Path
import io
import zipfile

import pandas as pd
import requests
import yaml


# Project root: telemetry-to-insight/
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_config():
    """Load project configuration from YAML."""

    config_path = PROJECT_ROOT / "config" / "config.yaml"

    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def ingest_raw_data(config):
    """
    Create the raw MetroPT-3 Parquet dataset if it does not
    already exist.

    If the raw Parquet exists, the ingestion step is skipped.
    """

    raw_path = PROJECT_ROOT / config["data"]["raw_parquet"]

    # ------------------------------------------------------
    # Idempotency check
    # ------------------------------------------------------

    if raw_path.exists():
        print(f"Raw dataset already exists: {raw_path}")
        print("Skipping download extract. File already esists!")
        return

    # Create raw directory if required
    raw_path.parent.mkdir(parents=True, exist_ok=True)

    url = config["source"]["dataset_url"] # Direct zip endpoint
    csv_filename = config["source"]["csv_filename"] 
    chunk_size = config["ingestion"]["download_chunk_size_bytes"]
    timeout = config["ingestion"]["request_timeout_seconds"]

    # ------------------------------------------------------
    # Download source ZIP
    # ------------------------------------------------------

    print("Downloading MetroPT-3 dataset...")

    zip_buffer = io.BytesIO()

    with requests.get(url, stream=True, timeout=timeout) as response:

        response.raise_for_status()

        for chunk in response.iter_content(chunk_size=chunk_size):

            if chunk:
                zip_buffer.write(chunk)

    # ------------------------------------------------------
    # Extract required CSV from Zip archive
    # ------------------------------------------------------

    print("Extracting telemetry CSV...")

    zip_buffer.seek(0)

    with zipfile.ZipFile(zip_buffer) as archive:

        with archive.open(csv_filename) as csv_file:
            df = pd.read_csv(csv_file)

    # ------------------------------------------------------
    # Convert raw dataset to Parquet and persist to raw_path
    # ------------------------------------------------------

    print("Writing raw telemetry to Parquet...")

    df.to_parquet(
        raw_path,
        engine="pyarrow",
        index=False
    )

    print(f"Raw dataset created: {raw_path}")



def create_development_data(config):
    """
    Create a controlled development extract from the raw
    MetroPT-3 Parquet dataset.

    No cleaning or preprocessing is performed here.
    """

    raw_path = PROJECT_ROOT / config["data"]["raw_parquet"]
    development_path = PROJECT_ROOT / config["data"]["development_parquet"]

    start_timestamp = config["development"]["start_timestamp"]
    end_timestamp = config["development"]["end_timestamp"]

    # ------------------------------------------------------
    # Idempotency check
    # ------------------------------------------------------

    if development_path.exists():
        print(f"Development dataset already exists: {development_path}")
        print("Skipping development extraction.")
        return

    # Create development directory if required
    development_path.parent.mkdir(parents=True, exist_ok=True)

    print("Creating development dataset...")

    # Read only the required time period from raw Parquet
    development_df = pd.read_parquet(
        raw_path,
        engine="pyarrow",
        filters=[
            ("timestamp", ">=", start_timestamp),
            ("timestamp", "<=", end_timestamp)
        ]
    )

    # Persist development extract
    development_df.to_parquet(
        development_path,
        engine="pyarrow",
        index=False
    )

    print(
        f"Development dataset created: "
        f"{len(development_df):,} rows"
    )

    print(f"Saved to: {development_path}")


if __name__ == "__main__":

    config = load_config()

    ingest_raw_data(config)
    
    create_development_data(config)