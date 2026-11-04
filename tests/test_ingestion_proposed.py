"""
Focused tests for ``src.ingestion_proposed``.

All tests run against a temporary project root. No network access is made
and no real project data is read or written.

Run from the project root with:

    python -m pytest tests/test_ingestion_proposed.py
"""

import datetime
import io
import json
import sys
import zipfile
from pathlib import Path
from unittest import mock

import pandas as pd
import pytest

# Make the project root importable when pytest is run from any directory.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import ingestion_proposed as ingestion  # noqa: E402


RAW_REL = "data/raw/raw.parquet"
DEV_REL = "data/development/dev.parquet"


# -----------------------------------------------------------------------------
# Fixtures and helpers
# -----------------------------------------------------------------------------

@pytest.fixture
def project_root(tmp_path, monkeypatch):
    """Point the module at an isolated temporary project root."""

    monkeypatch.setattr(ingestion, "PROJECT_ROOT", tmp_path)
    return tmp_path


def make_config(start="2020-03-01 00:00:00", end="2020-03-31 23:59:59"):
    return {
        "source": {
            "dataset_url": "https://example.invalid/data.zip",
            "csv_filename": "telemetry.csv",
        },
        "data": {
            "raw_parquet": RAW_REL,
            "development_parquet": DEV_REL,
        },
        "ingestion": {
            "download_chunk_size_bytes": 1024,
            "request_timeout_seconds": 5,
        },
        "development": {
            "start_timestamp": start,
            "end_timestamp": end,
        },
    }


def sample_df():
    """Raw-like frame with string timestamps, as produced by read_csv."""

    return pd.DataFrame(
        {
            "timestamp": [
                "2020-02-29 23:59:59",
                "2020-03-01 00:00:00",
                "2020-03-15 12:00:00",
                "2020-03-31 23:59:59",
                "2020-04-01 00:00:00",
            ],
            "TP2": [0.1, 0.2, 0.3, 0.4, 0.5],
        }
    )


def write_raw(root, df=None):
    path = root / RAW_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    (sample_df() if df is None else df).to_parquet(path, index=False)
    return path


def dev_paths(root):
    dev = root / DEV_REL
    return dev, dev.with_name(dev.name + ".meta.json")


# -----------------------------------------------------------------------------
# 1. Atomic Parquet writes
# -----------------------------------------------------------------------------

def test_atomic_write_creates_file_and_no_temp(tmp_path):
    target = tmp_path / "out.parquet"

    ingestion._write_parquet_atomic(sample_df(), target)

    assert target.exists()
    assert not (tmp_path / "out.parquet.tmp").exists()
    pd.testing.assert_frame_equal(pd.read_parquet(target), sample_df())


def test_atomic_write_failure_leaves_no_partial_file(tmp_path):
    target = tmp_path / "out.parquet"

    def partial_write(self, path, *args, **kwargs):
        Path(path).write_bytes(b"partial")
        raise OSError("disk full")

    with mock.patch.object(pd.DataFrame, "to_parquet", partial_write):
        with pytest.raises(OSError):
            ingestion._write_parquet_atomic(sample_df(), target)

    assert not target.exists()
    assert not (tmp_path / "out.parquet.tmp").exists()


def test_atomic_write_failure_preserves_existing_file(tmp_path):
    target = tmp_path / "out.parquet"
    original = sample_df().head(1)
    original.to_parquet(target, index=False)

    with mock.patch.object(
        pd.DataFrame, "to_parquet", side_effect=OSError("disk full")
    ):
        with pytest.raises(OSError):
            ingestion._write_parquet_atomic(sample_df(), target)

    pd.testing.assert_frame_equal(pd.read_parquet(target), original)


def test_ingest_raw_data_writes_parquet_via_mocked_download(project_root):
    csv_bytes = sample_df().to_csv(index=False).encode("utf-8")
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as archive:
        archive.writestr("telemetry.csv", csv_bytes)

    response = mock.MagicMock()
    response.iter_content.return_value = [zip_buffer.getvalue()]

    with mock.patch.object(ingestion.requests, "get") as mock_get:
        mock_get.return_value.__enter__.return_value = response
        ingestion.ingest_raw_data(make_config())

    raw_path = project_root / RAW_REL
    assert raw_path.exists()
    assert not raw_path.with_name(raw_path.name + ".tmp").exists()
    assert len(pd.read_parquet(raw_path)) == len(sample_df())


def test_ingest_raw_data_reuses_existing_file(project_root):
    write_raw(project_root)

    with mock.patch.object(ingestion.requests, "get") as mock_get:
        ingestion.ingest_raw_data(make_config())

    mock_get.assert_not_called()


# -----------------------------------------------------------------------------
# 2. Configuration-aware idempotency
# -----------------------------------------------------------------------------

def test_development_extract_written_with_metadata(project_root):
    write_raw(project_root)

    ingestion.create_development_data(make_config())

    dev, meta = dev_paths(project_root)
    result = pd.read_parquet(dev)

    # Inclusive bounds: first and last March rows kept, neighbours excluded.
    assert result["timestamp"].tolist() == [
        "2020-03-01 00:00:00",
        "2020-03-15 12:00:00",
        "2020-03-31 23:59:59",
    ]
    assert json.loads(meta.read_text(encoding="utf-8")) == {
        "start_timestamp": "2020-03-01 00:00:00",
        "end_timestamp": "2020-03-31 23:59:59",
        "raw_parquet": RAW_REL,
    }


def test_development_extract_reused_when_config_unchanged(project_root):
    write_raw(project_root)
    ingestion.create_development_data(make_config())

    with mock.patch.object(ingestion.pd, "read_parquet") as mock_read:
        ingestion.create_development_data(make_config())

    mock_read.assert_not_called()


def test_development_extract_rebuilt_when_period_changes(project_root):
    write_raw(project_root)
    ingestion.create_development_data(make_config())

    new_config = make_config(
        start="2020-03-15 00:00:00", end="2020-04-01 00:00:00"
    )
    ingestion.create_development_data(new_config)

    dev, meta = dev_paths(project_root)
    assert pd.read_parquet(dev)["timestamp"].tolist() == [
        "2020-03-15 12:00:00",
        "2020-03-31 23:59:59",
        "2020-04-01 00:00:00",
    ]
    assert json.loads(meta.read_text(encoding="utf-8"))["start_timestamp"] == (
        "2020-03-15 00:00:00"
    )


def test_development_extract_without_metadata_is_rebuilt(project_root):
    """Extracts created by the original module have no metadata file."""

    write_raw(project_root)
    dev, meta = dev_paths(project_root)
    dev.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"timestamp": ["legacy"], "TP2": [0.0]}).to_parquet(
        dev, index=False
    )

    ingestion.create_development_data(make_config())

    assert "legacy" not in pd.read_parquet(dev)["timestamp"].tolist()
    assert meta.exists()


def test_corrupt_metadata_triggers_rebuild(project_root):
    write_raw(project_root)
    ingestion.create_development_data(make_config())
    dev, meta = dev_paths(project_root)
    meta.write_text("{not json", encoding="utf-8")

    ingestion.create_development_data(make_config())

    assert json.loads(meta.read_text(encoding="utf-8"))["end_timestamp"] == (
        "2020-03-31 23:59:59"
    )


def test_stale_metadata_removed_if_rebuild_interrupted(project_root):
    """A failed rebuild must not leave old metadata describing new data."""

    write_raw(project_root)
    ingestion.create_development_data(make_config())
    dev, meta = dev_paths(project_root)

    with mock.patch.object(
        ingestion, "_write_metadata_atomic", side_effect=OSError("crash")
    ):
        with pytest.raises(OSError):
            ingestion.create_development_data(
                make_config(start="2020-03-15 00:00:00")
            )

    assert dev.exists()
    assert not meta.exists()


# -----------------------------------------------------------------------------
# 3. Empty development extracts
# -----------------------------------------------------------------------------

def test_empty_extract_raises_and_is_not_persisted(project_root):
    write_raw(project_root)

    with pytest.raises(ValueError, match="empty"):
        ingestion.create_development_data(
            make_config(start="2021-01-01", end="2021-01-31")
        )

    dev, meta = dev_paths(project_root)
    assert not dev.exists()
    assert not meta.exists()


def test_missing_raw_dataset_raises(project_root):
    with pytest.raises(FileNotFoundError):
        ingestion.create_development_data(make_config())


# -----------------------------------------------------------------------------
# 4. Timestamp normalisation
# -----------------------------------------------------------------------------

@pytest.mark.parametrize(
    "value, expected",
    [
        ("2020-03-01 00:00:00", "2020-03-01 00:00:00"),
        ("2020-3-1", "2020-03-01 00:00:00"),
        ("2020-03-01T08:05:09", "2020-03-01 08:05:09"),
        (datetime.date(2020, 3, 1), "2020-03-01 00:00:00"),
        (datetime.datetime(2020, 3, 1, 8, 5, 9), "2020-03-01 08:05:09"),
    ],
)
def test_normalise_timestamp(value, expected):
    assert ingestion._normalise_timestamp(value, "start_timestamp") == expected


@pytest.mark.parametrize("value", ["not a date", "", None])
def test_normalise_timestamp_rejects_invalid(value):
    with pytest.raises(ValueError, match="start_timestamp"):
        ingestion._normalise_timestamp(value, "start_timestamp")


def test_non_padded_config_filters_correctly(project_root):
    """Unpadded bounds would compare wrongly as raw strings."""

    write_raw(project_root)

    ingestion.create_development_data(
        make_config(start="2020-3-1", end="2020-3-31 23:59:59")
    )

    dev, _ = dev_paths(project_root)
    assert len(pd.read_parquet(dev)) == 3


def test_start_after_end_raises(project_root):
    write_raw(project_root)

    with pytest.raises(ValueError, match="must not be after"):
        ingestion.create_development_data(
            make_config(start="2020-04-01", end="2020-03-01")
        )
