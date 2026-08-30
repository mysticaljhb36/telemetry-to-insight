# run.py

"""
End-to-end data preparation pipeline for the MetroPT-3
Telemetry-to-Insight project.

Pipeline stages:
1. Ingest the public MetroPT-3 source dataset.
2. Create the controlled development extract.
3. Validate the development telemetry.
4. Preprocess and persist the analysis-ready dataset.

Run from the project root with:

    python run.py
"""

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


def main():
    """Run the complete telemetry data preparation pipeline."""

    print("=" * 60)
    print("MetroPT-3 Telemetry-to-Insight Pipeline")
    print("=" * 60)

    # ------------------------------------------------------
    # Load configuration
    # ------------------------------------------------------

    config = load_config()

    # ------------------------------------------------------
    # Stage 1 - Ingestion
    # ------------------------------------------------------

    print("\n[1/4] INGESTION")
    print("-" * 60)

    ingest_raw_data(config)
    create_development_data(config)

    # ------------------------------------------------------
    # Stage 2 - Load development dataset
    # ------------------------------------------------------

    print("\n[2/4] LOAD DEVELOPMENT DATA")
    print("-" * 60)

    df = load_development_data(config)

    # ------------------------------------------------------
    # Stage 3 - Validation
    # ------------------------------------------------------

    print("\n[3/4] VALIDATION")
    print("-" * 60)

    validate_schema(config, df)
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

    print("\n[4/4] PREPROCESSING")
    print("-" * 60)

    preprocess_data(config, df)

    print("\n" + "=" * 60)
    print("Pipeline completed successfully.")
    print("=" * 60)


if __name__ == "__main__":
    main()