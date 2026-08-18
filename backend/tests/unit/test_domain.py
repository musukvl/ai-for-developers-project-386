from datetime import UTC, datetime, timedelta

import pytest

from src.names import validate_name
from src.seed import expand_seed_range
from src.slots import expand_range, validate_horizon


def test_name_normalization() -> None:
    assert validate_name(" Sam-1 ") == "sam-1"
    with pytest.raises(ValueError):
        validate_name("Sam Smith")


def test_expands_half_hour_range() -> None:
    start = datetime(2026, 8, 20, 10, tzinfo=UTC)
    assert expand_range(start, start + timedelta(hours=1)) == [
        start,
        start + timedelta(minutes=30),
    ]


def test_rejects_off_boundary_and_horizon() -> None:
    now = datetime(2026, 8, 19, tzinfo=UTC)
    with pytest.raises(ValueError):
        expand_range(now.replace(minute=15), now + timedelta(hours=1))
    with pytest.raises(ValueError):
        validate_horizon(now, now + timedelta(days=29), now)


def test_seed_relative_days_expand_from_load_date() -> None:
    load_time = datetime(2026, 8, 19, 17, tzinfo=UTC)
    result = expand_seed_range({"day": 1, "start": "10:00", "end": "11:00"}, load_time)
    assert result == [
        datetime(2026, 8, 20, 10, tzinfo=UTC),
        datetime(2026, 8, 20, 10, 30, tzinfo=UTC),
    ]
