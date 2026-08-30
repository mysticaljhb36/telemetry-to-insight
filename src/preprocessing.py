# src/preprocessing.py

from pathlib import Path

import pandas as pd
import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_config():
    """Load project configuration from YAML."""

    config_path = PROJECT_ROOT / "config" / "config.yaml"

    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def load_development_data(config):
    """Load the validated development dataset."""

    development_path = PROJECT_ROOT / config["data"]["development_parquet"]

    print("Loading development dataset...")

    df = pd.read_parquet(development_path)

    print(f"Dataset loaded: {len(df):,} rows")

    return df


def preprocess_data(config, df):
    """
    Prepare the validated MetroPT-3 dataset for analysis.

    Processing:
    - investigate and remove redundant source index column
    - convert timestamp to datetime
    - sort telemetry chronologically
    - persist analysis-ready Parquet
    """

    processed_path = PROJECT_ROOT / config["data"]["processed_parquet"]

    # ------------------------------------------------------
    # Remove redundant source index
    # ------------------------------------------------------
    
    if "Unnamed: 0" in df.columns:
        print("Removing redundant source index: Unnamed: 0")
        df = df.drop(columns=["Unnamed: 0"])

    # ------------------------------------------------------
    # Convert timestamp
    # ------------------------------------------------------

    print("Converting timestamp to datetime...")

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="raise"
    )
    
    print(df.head())
    print(f"\nProcessed data column names: {df.columns.tolist()}")

    # ------------------------------------------------------
    # Sort chronologically
    # ------------------------------------------------------

    df = df.sort_values("timestamp").reset_index(drop=True)

    # ------------------------------------------------------
    # Persist processed dataset
    # ------------------------------------------------------

    processed_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_parquet(
        processed_path,
        engine="pyarrow",
        index=False
    )

    print(f"\nProcessed dataset created: {processed_path}")


if __name__ == "__main__":

    config = load_config()

    df = load_development_data(config)

    preprocess_data(config, df)
    