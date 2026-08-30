# =============================================================================
# Pipeline Orchestration
# =============================================================================
"""
End-to-end data preparation pipeline for the MetroPT-3
Telemetry-to-Insight project.

The pipeline performs four stages:

1. Ingest the public MetroPT-3 source dataset.
2. Create the configured development extract.
3. Validate the development telemetry.
4. Preprocess and persist the analysis-ready dataset.

Logging is configured centrally through ``src.logger`` and records pipeline
progress, warnings and failures to ``logs/pipeline.log``.

Run from the project root with:

    python run.py
"""

import logging

# Importing this module applies the application-wide logging configuration.
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


# Create a logger named after this module.
logger = logging.getLogger(__name__)


def main():
    """Run the complete telemetry data-preparation pipeline."""

    logger.info("MetroPT-3 Telemetry-to-Insight pipeline started.")

    try:
        # ------------------------------------------------------
        # Stage 1 - Load configuration
        # ------------------------------------------------------

        logger.info("Stage 1/4: Loading pipeline configuration.")

        config = load_config()

        # ------------------------------------------------------
        # Stage 2 - Ingestion
        # ------------------------------------------------------

        logger.info("Stage 2/4: Starting data ingestion.")

        ingest_raw_data(config)
        create_development_data(config)

        # ------------------------------------------------------
        # Stage 3 - Validation
        # ------------------------------------------------------

        logger.info("Stage 3/4: Loading and validating development telemetry.")

        df = load_development_data(config)

        validate_schema(df)
        validate_datatypes(df)
        validate_nulls(df)
        validate_duplicates(df)
        validate_duplicate_timestamps(df)
        inspect_digital_states(df)
        validate_digital_states(df)
        validate_timestamp_continuity(df)

        # ------------------------------------------------------
        # Stage 4 - Preprocessing
        # ------------------------------------------------------

        logger.info("Stage 4/4: Preprocessing telemetry dataset.")

        preprocess_data(config, df)

    except Exception:
        logger.exception(
            "MetroPT-3 Telemetry-to-Insight pipeline failed."
        )
        raise

    logger.info(
        "MetroPT-3 Telemetry-to-Insight pipeline completed successfully."
    )


if __name__ == "__main__":
    main()