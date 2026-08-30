# =============================================================================
# Data Validation
# =============================================================================
"""
Validation utilities for the MetroPT-3 Telemetry-to-Insight project.

This module validates the controlled development dataset before preprocessing.

Validation covers:

1. Dataset availability and loading.
2. Expected telemetry schema.
3. Column datatypes.
4. Missing values.
5. Duplicate rows.
6. Duplicate timestamps.
7. Observed digital-signal states.
8. Valid binary states for documented digital controls.
9. Timestamp continuity and telemetry gaps.

Structural and data-quality issues that could compromise downstream analysis
raise an exception and stop the pipeline.

Known source artefacts, such as ``Unnamed: 0``, are allowed at this stage
because they are intentionally removed during preprocessing.

Timestamp gaps are reported as warnings only. They represent genuine breaks
in the observed telemetry sequence and are retained rather than imputed or
reconstructed.
"""

import logging
from pathlib import Path

import pandas as pd


# Create a module-specific logger so log records identify their source.
logger = logging.getLogger(__name__)

# Resolve the project root from the location of this module.
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_development_data(config):
    """Load and return the configured development Parquet dataset."""

    development_path = (
        PROJECT_ROOT / config["data"]["development_parquet"]
    )

    if not development_path.exists():
        logger.error(
            "Development dataset not found: %s",
            development_path,
        )
        raise FileNotFoundError(
            f"Development dataset not found: {development_path}"
        )

    logger.info(
        "Loading development telemetry dataset from %s.",
        development_path,
    )

    df = pd.read_parquet(
        development_path,
        engine="pyarrow",
    )

    logger.info(
        "Development telemetry loaded successfully: %s rows.",
        f"{len(df):,}",
    )

    return df


def validate_schema(df):
    """
    Validate that the development dataset contains the expected telemetry
    columns.

    Known source artefacts are permitted before preprocessing and therefore
    do not cause schema validation to fail.

    Raises:
        ValueError: If expected telemetry columns are missing or genuinely
        unexpected columns are present.
    """

    expected_columns = [
        "timestamp",
        "TP2",
        "TP3",
        "H1",
        "DV_pressure",
        "Reservoirs",
        "Oil_temperature",
        "Motor_current",
        "COMP",
        "DV_eletric",
        "Towers",
        "MPG",
        "LPS",
        "Pressure_switch",
        "Oil_level",
        "Caudal_impulses",
    ]

    # Known source columns that are intentionally removed during
    # preprocessing and therefore do not represent schema failures.
    allowed_source_artifacts = [
        "Unnamed: 0",
    ]

    actual_columns = df.columns.tolist()

    missing_columns = [
        column
        for column in expected_columns
        if column not in actual_columns
    ]

    unexpected_columns = [
        column
        for column in actual_columns
        if column not in expected_columns
        and column not in allowed_source_artifacts
    ]

    source_artifacts = [
        column
        for column in actual_columns
        if column in allowed_source_artifacts
    ]

    logger.info(
        "Validating telemetry schema: %s expected telemetry columns, "
        "%s observed columns.",
        len(expected_columns),
        len(actual_columns),
    )

    if source_artifacts:
        logger.info(
            "Known source artefacts detected and retained for preprocessing: %s.",
            source_artifacts,
        )

    if missing_columns or unexpected_columns:

        logger.error(
            "Schema validation failed. Missing columns: %s. "
            "Unexpected columns: %s.",
            missing_columns,
            unexpected_columns,
        )

        raise ValueError(
            "Telemetry schema validation failed. "
            f"Missing columns: {missing_columns}; "
            f"Unexpected columns: {unexpected_columns}"
        )

    logger.info("Telemetry schema validation passed.")


def validate_datatypes(df):
    """
    Validate that the timestamp is string-like and telemetry columns
    contain numeric data.

    Raises:
        ValueError: If incompatible column datatypes are detected.
    """

    logger.info("Validating telemetry datatypes.")

    datatype_issues = {}

    # Timestamp remains text until preprocessing converts it to datetime.
    if not pd.api.types.is_string_dtype(df["timestamp"]):
        datatype_issues["timestamp"] = str(df["timestamp"].dtype)

    numeric_columns = [
        "TP2",
        "TP3",
        "H1",
        "DV_pressure",
        "Reservoirs",
        "Oil_temperature",
        "Motor_current",
        "COMP",
        "DV_eletric",
        "Towers",
        "MPG",
        "LPS",
        "Pressure_switch",
        "Oil_level",
        "Caudal_impulses",
    ]

    for column in numeric_columns:

        if not pd.api.types.is_numeric_dtype(df[column]):
            datatype_issues[column] = str(df[column].dtype)

    if datatype_issues:

        logger.error(
            "Datatype validation failed: %s",
            datatype_issues,
        )

        raise ValueError(
            f"Unexpected telemetry datatypes detected: {datatype_issues}"
        )

    logger.info("Telemetry datatype validation passed.")


def validate_nulls(df):
    """
    Validate that the development dataset contains no missing values.

    Raises:
        ValueError: If null values are detected.
    """

    logger.info("Validating null values.")

    null_counts = df.isnull().sum()
    null_columns = null_counts[null_counts > 0]

    if not null_columns.empty:

        null_summary = {
            column: int(count)
            for column, count in null_columns.items()
        }

        logger.error(
            "Null-value validation failed: %s",
            null_summary,
        )

        raise ValueError(
            f"Null values detected: {null_summary}"
        )

    logger.info("Null-value validation passed.")


def validate_duplicates(df):
    """
    Validate that the development dataset contains no duplicate rows.

    Raises:
        ValueError: If duplicate rows are detected.
    """

    logger.info("Validating duplicate rows.")

    duplicate_count = int(df.duplicated().sum())

    if duplicate_count > 0:

        logger.error(
            "Duplicate-row validation failed: %s duplicate rows detected.",
            f"{duplicate_count:,}",
        )

        raise ValueError(
            f"Duplicate rows detected: {duplicate_count:,}"
        )

    logger.info("Duplicate-row validation passed.")


def validate_duplicate_timestamps(df):
    """
    Validate that each telemetry observation has a unique timestamp.

    Raises:
        ValueError: If duplicate timestamps are detected.
    """

    logger.info("Validating duplicate timestamps.")

    duplicate_timestamp_count = int(
        df["timestamp"].duplicated().sum()
    )

    if duplicate_timestamp_count > 0:

        logger.error(
            "Duplicate-timestamp validation failed: %s duplicates detected.",
            f"{duplicate_timestamp_count:,}",
        )

        raise ValueError(
            "Duplicate timestamps detected: "
            f"{duplicate_timestamp_count:,}"
        )

    logger.info("Duplicate-timestamp validation passed.")


def inspect_digital_states(df):
    """
    Record the observed states of documented digital telemetry signals.

    This inspection provides visibility into the source data before binary
    domain rules are applied. It does not modify the dataset.
    """

    digital_columns = [
        "COMP",
        "DV_eletric",
        "Towers",
        "MPG",
        "LPS",
        "Pressure_switch",
        "Oil_level",
        "Caudal_impulses",
    ]

    logger.info("Inspecting observed digital-signal states.")

    for column in digital_columns:

        observed_states = sorted(
            df[column].dropna().unique().tolist()
        )

        logger.info(
            "%s observed states: %s",
            column,
            observed_states,
        )


def validate_digital_states(df):
    """
    Validate documented digital control signals as binary states.

    ``Caudal_impulses`` is inspected but is not hard-validated as binary
    because its documented meaning is pulse-counting rather than a simple
    binary control state.

    Raises:
        ValueError: If values other than 0 or 1 are detected in documented
        binary control signals.
    """

    digital_columns = [
        "COMP",
        "DV_eletric",
        "Towers",
        "MPG",
        "LPS",
        "Pressure_switch",
        "Oil_level",
    ]

    logger.info("Validating digital control-signal states.")

    invalid_states = {}

    for column in digital_columns:

        invalid_values = (
            df.loc[
                ~df[column].isin([0.0, 1.0]),
                column,
            ]
            .unique()
            .tolist()
        )

        if invalid_values:
            invalid_states[column] = invalid_values

    if invalid_states:

        logger.error(
            "Digital-state validation failed: %s",
            invalid_states,
        )

        raise ValueError(
            f"Unexpected digital states detected: {invalid_states}"
        )

    logger.info("Digital-state validation passed.")


def validate_timestamp_continuity(df):
    """
    Inspect telemetry sampling intervals and report significant time gaps.

    The median observed sampling interval is used as the typical telemetry
    interval. Gaps greater than twice this interval are reported for
    traceability but do not fail the pipeline because missing periods are
    retained rather than reconstructed.
    """

    logger.info("Validating timestamp continuity.")

    timestamps = pd.to_datetime(
        df["timestamp"],
        errors="raise",
    ).sort_values()

    time_gaps = timestamps.diff().dropna()

    if time_gaps.empty:
        logger.warning(
            "Timestamp continuity could not be assessed because fewer than "
            "two timestamps were available."
        )
        return

    minimum_interval = time_gaps.min()
    median_interval = time_gaps.median()
    maximum_interval = time_gaps.max()

    logger.info(
        "Observed telemetry intervals - minimum: %s, median: %s, maximum: %s.",
        minimum_interval,
        median_interval,
        maximum_interval,
    )

    # Gaps greater than twice the typical observed interval are retained
    # and reported rather than filled or reconstructed.
    large_gaps = time_gaps[
        time_gaps > (median_interval * 2)
    ]

    if large_gaps.empty:

        logger.info(
            "No telemetry gaps greater than twice the median interval "
            "were detected."
        )

    else:

        logger.warning(
            "Telemetry continuity check identified %s gaps greater than "
            "twice the median sampling interval. Largest gap: %s.",
            f"{len(large_gaps):,}",
            large_gaps.max(),
        )


if __name__ == "__main__":

    # Standalone execution reuses the central project configuration loader.
    from src.ingestion import load_config

    config = load_config()

    df = load_development_data(config)

    validate_schema(df)
    validate_datatypes(df)
    validate_nulls(df)
    validate_duplicates(df)
    validate_duplicate_timestamps(df)
    inspect_digital_states(df)
    validate_digital_states(df)
    validate_timestamp_continuity(df)