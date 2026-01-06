"""Basic unit tests for TimeUtil class.

This module contains unit tests for the TimeUtil class, focusing on
specific examples and edge cases for time operations.
"""

from datetime import UTC, datetime

import pytest
from morado.common.utils.time import TimeUtil


class TestCurrentTime:
    """Tests for current time methods."""

    def test_now_utc_returns_datetime(self):
        """Test that now_utc() returns a datetime object."""
        result = TimeUtil.now_utc()
        assert isinstance(result, datetime)

    def test_now_utc_has_utc_timezone(self):
        """Test that now_utc() returns a UTC timezone-aware datetime."""
        result = TimeUtil.now_utc()
        assert result.tzinfo == UTC

    def test_now_utc_is_timezone_aware(self):
        """Test that now_utc() returns a timezone-aware datetime."""
        result = TimeUtil.now_utc()
        assert result.tzinfo is not None

    def test_now_local_returns_datetime(self):
        """Test that now_local() returns a datetime object."""
        result = TimeUtil.now_local()
        assert isinstance(result, datetime)

    def test_now_local_is_timezone_aware(self):
        """Test that now_local() returns a timezone-aware datetime."""
        result = TimeUtil.now_local()
        assert result.tzinfo is not None

    def test_now_local_has_local_timezone(self):
        """Test that now_local() returns a datetime with local timezone."""
        result = TimeUtil.now_local()
        # The timezone should be the system's local timezone
        # We can't test the exact timezone, but we can verify it's not None
        assert result.tzinfo is not None
        # The tzinfo should have a tzname method
        assert hasattr(result.tzinfo, 'tzname')

    def test_now_utc_and_local_are_close(self):
        """Test that now_utc() and now_local() return times close to each other."""
        utc_time = TimeUtil.now_utc()
        local_time = TimeUtil.now_local()

        # Convert both to UTC for comparison
        local_as_utc = local_time.astimezone(UTC)

        # They should be within 1 second of each other
        diff = abs((utc_time - local_as_utc).total_seconds())
        assert diff < 1.0

    def test_now_utc_multiple_calls_increase(self):
        """Test that multiple calls to now_utc() return increasing times."""
        time1 = TimeUtil.now_utc()
        time2 = TimeUtil.now_utc()

        # time2 should be >= time1 (allowing for same microsecond)
        assert time2 >= time1

    def test_now_local_multiple_calls_increase(self):
        """Test that multiple calls to now_local() return increasing times."""
        time1 = TimeUtil.now_local()
        time2 = TimeUtil.now_local()

        # time2 should be >= time1 (allowing for same microsecond)
        assert time2 >= time1


class TestConvenienceMethods:
    """Tests for convenience methods for time manipulation."""

    def test_add_to_now_utc(self):
        """Test adding duration to current UTC time."""
        before = TimeUtil.now_utc()
        result = TimeUtil.add_to_now(hours=2, minutes=30)
        TimeUtil.now_utc()

        # Result should be timezone-aware
        assert result.tzinfo is not None
        # Result should be about 2.5 hours after 'before'
        diff = (result - before).total_seconds()
        expected = 2 * 3600 + 30 * 60  # 2 hours 30 minutes in seconds
        assert abs(diff - expected) < 1  # Within 1 second tolerance

    def test_add_to_now_local(self):
        """Test adding duration to current local time."""
        before = TimeUtil.now_local()
        result = TimeUtil.add_to_now(utc=False, days=1, hours=3)
        TimeUtil.now_local()

        # Result should be timezone-aware
        assert result.tzinfo is not None
        # Result should be about 27 hours after 'before'
        diff = (result - before).total_seconds()
        expected = 27 * 3600  # 27 hours in seconds
        assert abs(diff - expected) < 1  # Within 1 second tolerance

    def test_subtract_from_now_utc(self):
        """Test subtracting duration from current UTC time."""
        before = TimeUtil.now_utc()
        result = TimeUtil.subtract_from_now(hours=1, minutes=15)
        TimeUtil.now_utc()

        # Result should be timezone-aware
        assert result.tzinfo is not None
        # Result should be about 1.25 hours before 'before'
        diff = (before - result).total_seconds()
        expected = 1 * 3600 + 15 * 60  # 1 hour 15 minutes in seconds
        assert abs(diff - expected) < 1  # Within 1 second tolerance

    def test_subtract_from_now_local(self):
        """Test subtracting duration from current local time."""
        before = TimeUtil.now_local()
        result = TimeUtil.subtract_from_now(utc=False, days=2)
        TimeUtil.now_local()

        # Result should be timezone-aware
        assert result.tzinfo is not None
        # Result should be about 2 days before 'before'
        diff = (before - result).total_seconds()
        expected = 2 * 24 * 3600  # 2 days in seconds
        assert abs(diff - expected) < 1  # Within 1 second tolerance

    def test_add_to_time_with_none_uses_current(self):
        """Test that add_to_time with None uses current time."""
        before = TimeUtil.now_utc()
        result = TimeUtil.add_to_time(None, hours=1)
        TimeUtil.now_utc()

        # Result should be between before+1h and after+1h
        assert result.tzinfo is not None
        diff = (result - before).total_seconds()
        expected = 3600  # 1 hour in seconds
        assert abs(diff - expected) < 1  # Within 1 second tolerance

    def test_add_to_time_with_specific_datetime(self):
        """Test adding duration to a specific datetime."""
        specific = datetime(2024, 1, 15, 10, 0, 0, tzinfo=UTC)
        result = TimeUtil.add_to_time(specific, hours=3, minutes=30)

        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 13
        assert result.minute == 30
        assert result.tzinfo == UTC

    def test_subtract_from_time_with_none_uses_current(self):
        """Test that subtract_from_time with None uses current time."""
        before = TimeUtil.now_utc()
        result = TimeUtil.subtract_from_time(None, hours=2)
        TimeUtil.now_utc()

        # Result should be about 2 hours before 'before'
        assert result.tzinfo is not None
        diff = (before - result).total_seconds()
        expected = 7200  # 2 hours in seconds
        assert abs(diff - expected) < 1  # Within 1 second tolerance

    def test_subtract_from_time_with_specific_datetime(self):
        """Test subtracting duration from a specific datetime."""
        specific = datetime(2024, 1, 15, 10, 0, 0, tzinfo=UTC)
        result = TimeUtil.subtract_from_time(specific, hours=3, minutes=30)

        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 6
        assert result.minute == 30
        assert result.tzinfo == UTC

    def test_add_to_time_with_local_time(self):
        """Test add_to_time with local time when dt is None."""
        before = TimeUtil.now_local()
        result = TimeUtil.add_to_time(None, utc=False, days=1)
        TimeUtil.now_local()

        # Result should be timezone-aware with local timezone
        assert result.tzinfo is not None
        diff = (result - before).total_seconds()
        expected = 24 * 3600  # 1 day in seconds
        assert abs(diff - expected) < 1  # Within 1 second tolerance

    def test_subtract_from_time_with_local_time(self):
        """Test subtract_from_time with local time when dt is None."""
        before = TimeUtil.now_local()
        result = TimeUtil.subtract_from_time(None, utc=False, weeks=1)
        TimeUtil.now_local()

        # Result should be timezone-aware with local timezone
        assert result.tzinfo is not None
        diff = (before - result).total_seconds()
        expected = 7 * 24 * 3600  # 1 week in seconds
        assert abs(diff - expected) < 1  # Within 1 second tolerance

    def test_add_to_time_with_invalid_type(self):
        """Test that add_to_time raises TypeError for invalid dt type."""
        with pytest.raises(TypeError):
            TimeUtil.add_to_time("not a datetime", hours=1)

    def test_subtract_from_time_with_invalid_type(self):
        """Test that subtract_from_time raises TypeError for invalid dt type."""
        with pytest.raises(TypeError):
            TimeUtil.subtract_from_time("not a datetime", hours=1)
