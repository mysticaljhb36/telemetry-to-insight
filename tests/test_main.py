
import src.main as pipeline


def test_main_orchestration(monkeypatch):

    calls = []

    config = {"data": {"processed_parquet": "test.parquet"}}
    df = object()

    # Replace actual functions with lightweight test functions.
    monkeypatch.setattr(
        pipeline,
        "load_config",
        lambda: calls.append("load_config") or config,
    )

    monkeypatch.setattr(
        pipeline,
        "ingest_raw_data",
        lambda config: calls.append("ingest_raw_data"),
    )

    monkeypatch.setattr(
        pipeline,
        "create_development_data",
        lambda config: calls.append("create_development_data"),
    )

    monkeypatch.setattr(
        pipeline,
        "load_development_data",
        lambda config: calls.append("load_development_data") or df,
    )

    # Mock all validation functions.
    validation_functions = [
        "validate_schema",
        "validate_datatypes",
        "validate_nulls",
        "validate_duplicates",
        "validate_duplicate_timestamps",
        "inspect_digital_states",
        "validate_digital_states",
        "validate_timestamp_continuity",
    ]

    for name in validation_functions:
        monkeypatch.setattr(
            pipeline,
            name,
            lambda df, name=name: calls.append(name),
        )

    monkeypatch.setattr(
        pipeline,
        "preprocess_data",
        lambda config, df: calls.append("preprocess_data") or [1, 2, 3],
    )

    # Execute the orchestration.
    pipeline.main()

    # Verify the complete execution order.
    assert calls == [
        "load_config",
        "ingest_raw_data",
        "create_development_data",
        "load_development_data",
        "validate_schema",
        "validate_datatypes",
        "validate_nulls",
        "validate_duplicates",
        "validate_duplicate_timestamps",
        "inspect_digital_states",
        "validate_digital_states",
        "validate_timestamp_continuity",
        "preprocess_data",
    ]
