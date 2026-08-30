# =============================================================================
# Data Preprocessing
# =============================================================================
"""
Preprocessing utilities for the MetroPT-3 Telemetry-to-Insight project.

This module prepares validated development telemetry for analysis by:

1. Removing the known source index artefact ``Unnamed: 0`` when present.
2. Converting the timestamp column to pandas datetime.
3. Sorting telemetry chronologically.
4. Persisting the analysis-ready dataset as Parquet.

No imputation, interpolation or reconstruction of missing telemetry periods
is performed during preprocessing.
"""

import logging
from pathlib import Path

import pandas as pd


# Create a module-specific logger so log records identify their source.
logger = logging.getLogger(__name__)

# Resolve the project root from the location of this module.
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def preprocess_data(config, df):
    """
    Prepare validated MetroPT-3 telemetry for analysis and persist it.

    Args:
        config (dict): Project configuration containing the processed-data path.
        df (pandas.DataFrame): Validated development telemetry.

    Returns:
        pandas.DataFrame: The processed analysis-ready dataset.

    Raises:
        KeyError: If the required timestamp column is missing.
        ValueError: If timestamp conversion fails.
    """

    processed_path = (
        PROJECT_ROOT / config["data"]["processed_parquet"]
    )

    logger.info("Starting telemetry preprocessing.")

    # Work on a copy so preprocessing does not mutate the validated
    # development dataframe passed into the function.
    processed_df = df.copy()

    # Remove the known source-generated index artefact.
    if "Unnamed: 0" in processed_df.columns:

        logger.info(
            "Removing known source artefact: Unnamed: 0."
        )

        processed_df = processed_df.drop(
            columns=["Unnamed: 0"]
        )

    # Confirm the required timestamp field is available before conversion.
    if "timestamp" not in processed_df.columns:

        logger.error(
            "Preprocessing failed because the timestamp column is missing."
        )

        raise KeyError(
            "Required timestamp column not found."
        )

    logger.info("Converting telemetry timestamp to datetime.")

    processed_df["timestamp"] = pd.to_datetime(
        processed_df["timestamp"],
        errors="raise",
    )

    logger.info("Sorting telemetry chronologically.")

    processed_df = (
        processed_df
        .sort_values("timestamp")
        .reset_index(drop=True)
    )

    # Ensure the configured processed-data directory exists.
    processed_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    logger.info(
        "Persisting processed telemetry dataset to %s.",
        processed_path,
    )

    processed_df.to_parquet(
        processed_path,
        engine="pyarrow",
        index=False,
    )

    logger.info(
        "Telemetry preprocessing completed successfully: %s rows.",
        f"{len(processed_df):,}",
    )

    return processed_df