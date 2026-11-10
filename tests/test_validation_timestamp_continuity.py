"""
Focused tests for ``src.validation.validate_timestamp_continuity``.

The tests use small in-memory DataFrames. No project data is read.

Run from the project root with:

    python -m pytest tests/test_validation_timestamp_continuity.py
"""

import logging
import sys
from pathlib import Path

import pandas as pd
import numpy as np
import pytest

# Make the project root importable when pytest is run from any directory.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.validation import validate_timestamp_continuity  # noqa: E402


LOGGER_NAME = "src.validation"


@pytest.fixture
def df_with_gap():
    """Telemetry sampled every 10 seconds with a single 30-second gap."""

    timestamps = [
        "2020-02-01 00:00:00",
        "2020-02-01 00:00:10",
        "2020-02-01 00:00:20",
        "2020-02-01 00:00:30",
        "2020-02-01 00:01:00",  # 30-second gap; median interval is 10s.
        "2020-02-01 00:01:10",
        "2020-02-01 00:01:20",
    ]

    return pd.DataFrame({"timestamp": timestamps})


def _warnings(caplog):
    return [
        record
        for record in caplog.records
        if record.name == LOGGER_NAME and record.levelno == logging.WARNING
    ]


# -----------------------------------------------------------------------------
# Default behaviour
# -----------------------------------------------------------------------------


def test_default_multiplier_reports_gap_as_warning(df_with_gap, caplog):
    caplog.set_level(logging.INFO, logger=LOGGER_NAME)

    # A gap must be reported, not raised.
    assert validate_timestamp_continuity(df_with_gap) is None

    warnings = _warnings(caplog)
    assert len(warnings) == 1
    assert "1 gaps greater than 2 times" in warnings[0].getMessage()
    assert "0 days 00:00:30" in warnings[0].getMessage()


def test_default_multiplier_no_gap_logs_info(caplog):
    df = pd.DataFrame(
        {
            "timestamp": [
                "2020-02-01 00:00:00",
                "2020-02-01 00:00:10",
                "2020-02-01 00:00:20",
            ]
        }
    )
    caplog.set_level(logging.INFO, logger=LOGGER_NAME)

    validate_timestamp_continuity(df)

    assert not _warnings(caplog)
    assert "No telemetry gaps greater than 2 times" in caplog.text


def test_fewer_than_two_timestamps_warns(caplog):
    df = pd.DataFrame({"timestamp": ["2020-02-01 00:00:00"]})
    caplog.set_level(logging.INFO, logger=LOGGER_NAME)

    validate_timestamp_continuity(df)

    warnings = _warnings(caplog)
    assert len(warnings) == 1
    assert "could not be assessed" in warnings[0].getMessage()


# -----------------------------------------------------------------------------
# Custom thresholds
# -----------------------------------------------------------------------------


def test_higher_multiplier_suppresses_gap(df_with_gap, caplog):
    caplog.set_level(logging.INFO, logger=LOGGER_NAME)

    # A 30s gap is not strictly greater than 3 x 10s.
    validate_timestamp_continuity(df_with_gap, gap_multiplier=3)

    assert not _warnings(caplog)
    assert "No telemetry gaps greater than 3 times" in caplog.text


def test_lower_multiplier_reports_more_gaps(caplog):
    df = pd.DataFrame(
        {
            "timestamp": [
                "2020-02-01 00:00:00",
                "2020-02-01 00:00:10",
                "2020-02-01 00:00:20",
                "2020-02-01 00:00:35",  # 15s gap
                "2020-02-01 00:00:45",
                "2020-02-01 00:00:55",
                "2020-02-01 00:01:25",  # 30s gap
            ]
        }
    )
    caplog.set_level(logging.INFO, logger=LOGGER_NAME)

    validate_timestamp_continuity(df, gap_multiplier=1.2)

    warnings = _warnings(caplog)
    assert len(warnings) == 1
    assert "2 gaps greater than 1.2 times" in warnings[0].getMessage()


# -----------------------------------------------------------------------------
# Invalid multipliers
# -----------------------------------------------------------------------------


@pytest.mark.parametrize(
    "invalid_multiplier",
    [
        0,
        -1,
        -0.5,
        float("nan"),
        float("inf"),
        float("-inf"),
        "2",
        None,
        True,
    ],
)
def test_invalid_multiplier_raises(df_with_gap, invalid_multiplier):
    with pytest.raises(ValueError, match="gap_multiplier"):
        validate_timestamp_continuity(
            df_with_gap,
            gap_multiplier=invalid_multiplier,
        )


@pytest.mark.parametrize(
    "multiplier",
    [
        np.float32(2.0),
        np.float64(2.0),
        np.int64(2),
    ],
)
def test_numpy_numeric_multipliers_are_accepted(
    df_with_gap, multiplier
):
    validate_timestamp_continuity(
        df_with_gap,
        gap_multiplier=multiplier,
    )