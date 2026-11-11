
# =============================================================================
# MetroPT-3 Pipeline Orchestration
# =============================================================================
"""
Main entry point for the MetroPT-3 Telemetry-to-Insight pipeline.

Coordinates ingestion, validation and preprocessing using
the existing project modules.
"""

import logging

# Initialise central logging configuration.
import src.logger

from src.ingestion import (
    load_config,
    ingest_raw_data,
    create_development_data,
)

from src.validation import (
    load_development_data,
    validate_schema,
    validate_datatypes,
    validate_nulls,
    validate_duplicates,
    validate_duplicate_timestamps,
    inspect_digital_states,
    validate_digital_states,
    validate_timestamp_continuity,
)

from src.preprocessing import preprocess_data


logger = logging.getLogger(__name__)


def main():
    """Execute the MetroPT-3 data-processing pipeline."""

    logger.info("Starting MetroPT-3 telemetry pipeline.")

    # 1. Load configuration
    config = load_config()

    # 2. Ingest raw data and create development extract
    ingest_raw_data(config)
    create_development_data(config)

    # 3. Load development data
    df = load_development_data(config)

    # 4. Validate data
    validate_schema(df)
    validate_datatypes(df)
    validate_nulls(df)
    validate_duplicates(df)
    validate_duplicate_timestamps(df)
    inspect_digital_states(df)
    validate_digital_states(df)
    validate_timestamp_continuity(df)

    # 5. Preprocess and persist the processed dataset
    processed_df = preprocess_data(config, df)

    logger.info(
        "MetroPT-3 pipeline completed successfully: %s rows.",
        f"{len(processed_df):,}",
    )


if __name__ == "__main__":
    main()
