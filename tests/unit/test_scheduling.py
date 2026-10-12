from datetime import UTC, datetime

import pytest

from nyc_mobility.ingestion.scheduling import resolve_year_month


def test_uses_override_when_given():
    assert resolve_year_month("2024-05", datetime(2024, 1, 1, tzinfo=UTC)) == "2024-05"


def test_uses_interval_start_when_no_override():
    assert resolve_year_month(None, datetime(2024, 3, 1, tzinfo=UTC)) == "2024-03"


def test_fails_when_neither_is_available():
    with pytest.raises(ValueError, match="year_month"):
        resolve_year_month(None, None)


def test_rejects_invalid_override():
    with pytest.raises(ValueError):
        resolve_year_month("2024-13", None)
