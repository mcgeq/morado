"""Time utility class for common time operations.

This module provides the TimeUtil class with static methods for working with
timestamps, including getting current time in different timezones, formatting,
parsing, and time calculations.

All methods work with timezone-aware datetime objects to ensure correctness
across different timezones and daylight saving time transitions.

Example:
    from morado.common.utils.time import TimeUtil

    # Get current time
    utc_now = TimeUtil.now_utc()
    local_now = TimeUtil.now_local()
"""

from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from .exceptions import TimeParseError


class TimeUtil:
    """Time utility class for common time operations.

    This class provides static methods for working with timestamps, including:
    - Getting current time in UTC or local timezone
    - Formatting and parsing timestamps
    - Time calculations and timezone conversions

    All methods return timezone-aware datetime objects to ensure correctness.
    """

    @staticmethod
    def now_utc() -> datetime:
        """Get the current timestamp in UTC timezone.

        Returns a timezone-aware datetime object representing the current
        moment in Coordinated Universal Time (UTC).

        Returns:
            datetime: Current timestamp with UTC timezone.

        Example:
            >>> from morado.common.utils.time import TimeUtil
            >>> utc_time = TimeUtil.now_utc()
            >>> utc_time.tzinfo == timezone.utc
            True
            >>> # Use for logging, database timestamps, or API responses
            >>> print(f"Server time: {utc_time}")
            Server time: 2024-01-15 14:30:45.123456+00:00

        Note:
            UTC is recommended for storing timestamps in databases and logs
            as it avoids ambiguity from daylight saving time transitions.
        """
        return datetime.now(UTC)

    @staticmethod
    def now_local() -> datetime:
        """Get the current timestamp in the system's local timezone.

        Returns a timezone-aware datetime object representing the current
        moment in the system's configured local timezone. This respects
        daylight saving time rules for the local timezone.

        Returns:
            datetime: Current timestamp with local timezone.

        Example:
            >>> from morado.common.utils.time import TimeUtil
            >>> local_time = TimeUtil.now_local()
            >>> local_time.tzinfo is not None
            True
            >>> # Use for displaying time to users in their local timezone
            >>> print(f"Your local time: {local_time}")
            Your local time: 2024-01-15 09:30:45.123456-05:00

        Note:
            The local timezone is determined by the system configuration.
            For displaying time to users in different timezones, consider
            using convert_timezone() instead.
        """
        # Get the current time as a timezone-aware datetime in local timezone
        # datetime.now().astimezone() returns the local timezone on all platforms
        return datetime.now().astimezone()

    @staticmethod
    def to_iso8601(dt: datetime) -> str:
        """Format a datetime as an ISO 8601 string.

        Converts a timezone-aware datetime object to an ISO 8601 formatted
        string. This format is widely used in APIs and data interchange.

        Args:
            dt: A timezone-aware datetime object to format.

        Returns:
            str: ISO 8601 formatted string (e.g., "2024-01-15T14:30:45.123456+00:00").

        Raises:
            ValueError: If the datetime is naive (lacks timezone information).
            TypeError: If dt is not a datetime object.

        Example:
            >>> from morado.common.utils.time import TimeUtil
            >>> from datetime import datetime, timezone
            >>> dt = datetime(2024, 1, 15, 14, 30, 45, tzinfo=timezone.utc)
            >>> TimeUtil.to_iso8601(dt)
            '2024-01-15T14:30:45+00:00'
            >>> # Use for API responses or data serialization
            >>> utc_now = TimeUtil.now_utc()
            >>> iso_string = TimeUtil.to_iso8601(utc_now)

        Note:
            The datetime must be timezone-aware. Use now_utc() or now_local()
            to get timezone-aware datetime objects, or use dt.replace(tzinfo=...)
            to add timezone information to naive datetimes.
        """
        if not isinstance(dt, datetime):
            msg = f"Expected datetime object, got {type(dt).__name__}"
            raise TypeError(msg)

        if dt.tzinfo is None:
            raise ValueError(
                "Cannot format naive datetime. Use timezone-aware datetime objects. "
                "Consider using TimeUtil.now_utc() or adding timezone with "
                "dt.replace(tzinfo=timezone.utc)"
            )

        return dt.isoformat()

    @staticmethod
    def format_time(dt: datetime, format_string: str) -> str:
        """Format a datetime with a custom format string.

        Converts a timezone-aware datetime object to a string using a custom
        format string. Uses Python's strftime format codes.

        Args:
            dt: A timezone-aware datetime object to format.
            format_string: Format string using strftime codes (e.g., "%Y-%m-%d %H:%M:%S").

        Returns:
            str: Formatted time string.

        Raises:
            ValueError: If the datetime is naive (lacks timezone information).
            TypeError: If dt is not a datetime object or format_string is not a string.

        Example:
            >>> from morado.common.utils.time import TimeUtil
            >>> from datetime import datetime, timezone
            >>> dt = datetime(2024, 1, 15, 14, 30, 45, tzinfo=timezone.utc)
            >>> TimeUtil.format_time(dt, "%Y-%m-%d %H:%M:%S")
            '2024-01-15 14:30:45'
            >>> TimeUtil.format_time(dt, "%B %d, %Y at %I:%M %p")
            'January 15, 2024 at 02:30 PM'

        Note:
            Common format codes:
            - %Y: 4-digit year
            - %m: 2-digit month
            - %d: 2-digit day
            - %H: 24-hour hour
            - %M: minute
            - %S: second
            - %z: UTC offset
            - %Z: timezone name
        """
        if not isinstance(dt, datetime):
            msg = f"Expected datetime object, got {type(dt).__name__}"
            raise TypeError(msg)

        if not isinstance(format_string, str):
            msg = f"Expected string format, got {type(format_string).__name__}"
            raise TypeError(
                msg
            )

        if dt.tzinfo is None:
            raise ValueError(
                "Cannot format naive datetime. Use timezone-aware datetime objects. "
                "Consider using TimeUtil.now_utc() or adding timezone with "
                "dt.replace(tzinfo=timezone.utc)"
            )

        return dt.strftime(format_string)

    @staticmethod
    def parse_iso8601(time_string: str) -> datetime:
        """Parse an ISO 8601 formatted string into a datetime object.

        Converts an ISO 8601 formatted string to a timezone-aware datetime object.
        Supports various ISO 8601 formats including with/without microseconds and
        different timezone representations.

        Args:
            time_string: ISO 8601 formatted string to parse.

        Returns:
            datetime: Timezone-aware datetime object.

        Raises:
            TimeParseError: If the string cannot be parsed as ISO 8601.
            TypeError: If time_string is not a string.

        Example:
            >>> from morado.common.utils.time import TimeUtil
            >>> dt = TimeUtil.parse_iso8601("2024-01-15T14:30:45+00:00")
            >>> dt.year
            2024
            >>> dt.tzinfo is not None
            True
            >>> # Round-trip example
            >>> original = TimeUtil.now_utc()
            >>> iso_string = TimeUtil.to_iso8601(original)
            >>> parsed = TimeUtil.parse_iso8601(iso_string)
            >>> # original and parsed represent the same moment in time

        Note:
            Supports formats like:
            - "2024-01-15T14:30:45+00:00"
            - "2024-01-15T14:30:45.123456+00:00"
            - "2024-01-15T14:30:45Z"
        """
        if not isinstance(time_string, str):
            msg = f"Expected string, got {type(time_string).__name__}"
            raise TypeError(msg)

        try:
            dt = datetime.fromisoformat(time_string)

            # Ensure the result is timezone-aware
            if dt.tzinfo is None:
                raise TimeParseError(
                    time_string,
                    message=f"Parsed datetime from '{time_string}' is not timezone-aware. "
                    f"ISO 8601 strings must include timezone information (e.g., '+00:00' or 'Z')",
                )

            return dt
        except ValueError as e:
            raise TimeParseError(
                time_string,
                message=f"Failed to parse ISO 8601 time string '{time_string}': {e!s}",
            )

    @staticmethod
    def parse_time(time_string: str, format_string: str) -> datetime:
        """Parse a custom formatted time string into a datetime object.

        Converts a time string to a datetime object using a custom format string.
        Uses Python's strptime format codes.

        Args:
            time_string: Time string to parse.
            format_string: Format string using strptime codes (e.g., "%Y-%m-%d %H:%M:%S").

        Returns:
            datetime: Parsed datetime object. If the format string includes timezone
                     information (%z or %Z), returns timezone-aware datetime.
                     Otherwise, returns naive datetime.

        Raises:
            TimeParseError: If the string cannot be parsed with the given format.
            TypeError: If arguments are not strings.

        Example:
            >>> from morado.common.utils.time import TimeUtil
            >>> dt = TimeUtil.parse_time("2024-01-15 14:30:45", "%Y-%m-%d %H:%M:%S")
            >>> dt.year
            2024
            >>> # With timezone
            >>> dt_tz = TimeUtil.parse_time("2024-01-15 14:30:45 +0000", "%Y-%m-%d %H:%M:%S %z")
            >>> dt_tz.tzinfo is not None
            True
            >>> # Round-trip example
            >>> original = TimeUtil.now_utc()
            >>> fmt = "%Y-%m-%d %H:%M:%S %z"
            >>> formatted = TimeUtil.format_time(original, fmt)
            >>> parsed = TimeUtil.parse_time(formatted, fmt)

        Note:
            Common format codes:
            - %Y: 4-digit year
            - %m: 2-digit month
            - %d: 2-digit day
            - %H: 24-hour hour
            - %M: minute
            - %S: second
            - %z: UTC offset (+0000)
            - %Z: timezone name

            For timezone-aware parsing, include %z or %Z in the format string.
        """
        if not isinstance(time_string, str):
            msg = f"Expected string for time_string, got {type(time_string).__name__}"
            raise TypeError(
                msg
            )

        if not isinstance(format_string, str):
            msg = f"Expected string for format_string, got {type(format_string).__name__}"
            raise TypeError(
                msg
            )

        try:
            return datetime.strptime(time_string, format_string)
        except ValueError as e:
            raise TimeParseError(
                time_string,
                format_string,
                message=f"Failed to parse time string '{time_string}' with format '{format_string}': {e!s}",
            )

    @staticmethod
    def time_difference(dt1: datetime, dt2: datetime) -> timedelta:
        """Calculate the time difference between two timestamps.

        Computes the duration between two datetime objects, returning a timedelta
        representing dt2 - dt1. Both datetimes must be timezone-aware to ensure
        accurate calculations across timezone boundaries.

        Args:
            dt1: First timezone-aware datetime object.
            dt2: Second timezone-aware datetime object.

        Returns:
            timedelta: Time difference (dt2 - dt1). Positive if dt2 is later than dt1,
                      negative if dt2 is earlier than dt1.

        Raises:
            ValueError: If either datetime is naive (lacks timezone information).
            TypeError: If either argument is not a datetime object.

        Example:
            >>> from morado.common.utils.time import TimeUtil
            >>> from datetime import datetime, timezone, timedelta
            >>> dt1 = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
            >>> dt2 = datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc)
            >>> diff = TimeUtil.time_difference(dt1, dt2)
            >>> diff.total_seconds()
            16200.0
            >>> diff.total_seconds() / 3600  # Hours
            4.5
            >>> # Verify symmetry: dt1 + (dt2 - dt1) == dt2
            >>> dt1 + TimeUtil.time_difference(dt1, dt2) == dt2
            True

        Note:
            The result is always a timedelta object, which can be used with
            add_duration() and subtract_duration() for time calculations.
            Both datetimes are converted to UTC internally for accurate comparison.
        """
        if not isinstance(dt1, datetime):
            msg = f"Expected datetime for dt1, got {type(dt1).__name__}"
            raise TypeError(msg)

        if not isinstance(dt2, datetime):
            msg = f"Expected datetime for dt2, got {type(dt2).__name__}"
            raise TypeError(msg)

        if dt1.tzinfo is None:
            raise ValueError(
                "dt1 is naive (lacks timezone information). Use timezone-aware datetime objects. "
                "Consider using TimeUtil.now_utc() or adding timezone with "
                "dt.replace(tzinfo=timezone.utc)"
            )

        if dt2.tzinfo is None:
            raise ValueError(
                "dt2 is naive (lacks timezone information). Use timezone-aware datetime objects. "
                "Consider using TimeUtil.now_utc() or adding timezone with "
                "dt.replace(tzinfo=timezone.utc)"
            )

        return dt2 - dt1

    @staticmethod
    def add_duration(dt: datetime, **kwargs) -> datetime:
        """Add a time duration to a timestamp.

        Adds a duration to a timezone-aware datetime object. The duration can be
        specified using keyword arguments that are passed to timedelta (days, hours,
        minutes, seconds, microseconds, milliseconds, weeks).

        Args:
            dt: A timezone-aware datetime object.
            **kwargs: Duration components (days, hours, minutes, seconds, etc.)
                     passed to timedelta constructor.

        Returns:
            datetime: New timezone-aware datetime with the duration added.

        Raises:
            ValueError: If the datetime is naive (lacks timezone information).
            TypeError: If dt is not a datetime object or kwargs are invalid for timedelta.

        Example:
            >>> from morado.common.utils.time import TimeUtil
            >>> from datetime import datetime, timezone
            >>> dt = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
            >>> # Add 2 hours and 30 minutes
            >>> new_dt = TimeUtil.add_duration(dt, hours=2, minutes=30)
            >>> new_dt.hour
            12
            >>> new_dt.minute
            30
            >>> # Add multiple units
            >>> future = TimeUtil.add_duration(dt, days=7, hours=3, minutes=15)
            >>> # Verify that adding then subtracting returns original
            >>> result = TimeUtil.subtract_duration(
            ...     TimeUtil.add_duration(dt, hours=5), hours=5
            ... )
            >>> result == dt
            True

        Note:
            The timezone information is preserved in the result.
            For DST transitions, the result respects the timezone rules.
            Supported kwargs: days, seconds, microseconds, milliseconds,
            minutes, hours, weeks.
        """
        if not isinstance(dt, datetime):
            msg = f"Expected datetime object, got {type(dt).__name__}"
            raise TypeError(msg)

        if dt.tzinfo is None:
            raise ValueError(
                "Cannot add duration to naive datetime. Use timezone-aware datetime objects. "
                "Consider using TimeUtil.now_utc() or adding timezone with "
                "dt.replace(tzinfo=timezone.utc)"
            )

        try:
            duration = timedelta(**kwargs)
        except TypeError as e:
            msg = f"Invalid duration arguments: {e!s}"
            raise TypeError(msg)

        return dt + duration

    @staticmethod
    def subtract_duration(dt: datetime, **kwargs) -> datetime:
        """Subtract a time duration from a timestamp.

        Subtracts a duration from a timezone-aware datetime object. The duration can be
        specified using keyword arguments that are passed to timedelta (days, hours,
        minutes, seconds, microseconds, milliseconds, weeks).

        Args:
            dt: A timezone-aware datetime object.
            **kwargs: Duration components (days, hours, minutes, seconds, etc.)
                     passed to timedelta constructor.

        Returns:
            datetime: New timezone-aware datetime with the duration subtracted.

        Raises:
            ValueError: If the datetime is naive (lacks timezone information).
            TypeError: If dt is not a datetime object or kwargs are invalid for timedelta.

        Example:
            >>> from morado.common.utils.time import TimeUtil
            >>> from datetime import datetime, timezone
            >>> dt = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
            >>> # Subtract 2 hours and 30 minutes
            >>> new_dt = TimeUtil.subtract_duration(dt, hours=2, minutes=30)
            >>> new_dt.hour
            7
            >>> new_dt.minute
            30
            >>> # Subtract multiple units
            >>> past = TimeUtil.subtract_duration(dt, days=7, hours=3, minutes=15)
            >>> # Verify inverse relationship
            >>> result = TimeUtil.add_duration(
            ...     TimeUtil.subtract_duration(dt, days=1), days=1
            ... )
            >>> result == dt
            True

        Note:
            The timezone information is preserved in the result.
            For DST transitions, the result respects the timezone rules.
            Supported kwargs: days, seconds, microseconds, milliseconds,
            minutes, hours, weeks.
        """
        if not isinstance(dt, datetime):
            msg = f"Expected datetime object, got {type(dt).__name__}"
            raise TypeError(msg)

        if dt.tzinfo is None:
            raise ValueError(
                "Cannot subtract duration from naive datetime. Use timezone-aware datetime objects. "
                "Consider using TimeUtil.now_utc() or adding timezone with "
                "dt.replace(tzinfo=timezone.utc)"
            )

        try:
            duration = timedelta(**kwargs)
        except TypeError as e:
            msg = f"Invalid duration arguments: {e!s}"
            raise TypeError(msg)

        return dt - duration

    @staticmethod
    def add_to_now(utc: bool = True, **kwargs) -> datetime:
        """Add a duration to the current time.

        Convenience method that adds a duration to the current timestamp.
        By default uses UTC time, but can use local time if specified.

        Args:
            utc: If True, uses UTC time; if False, uses local time. Default is True.
            **kwargs: Duration components (days, hours, minutes, seconds, years, months, weeks)
                     passed to timedelta constructor.

        Returns:
            datetime: New timezone-aware datetime representing current time plus duration.

        Example:
            >>> from morado.common.utils.time import TimeUtil
            >>> # Get time 2 hours from now (UTC)
            >>> future = TimeUtil.add_to_now(hours=2)
            >>> # Get time 3 days and 5 hours from now (local time)
            >>> future_local = TimeUtil.add_to_now(utc=False, days=3, hours=5)
            >>> # Get time 1 week from now
            >>> next_week = TimeUtil.add_to_now(weeks=1)
            >>> # Get time 30 minutes from now
            >>> in_30_min = TimeUtil.add_to_now(minutes=30)

        Note:
            This is equivalent to:
            TimeUtil.add_duration(TimeUtil.now_utc(), **kwargs)
            or
            TimeUtil.add_duration(TimeUtil.now_local(), **kwargs)
        """
        base_time = TimeUtil.now_utc() if utc else TimeUtil.now_local()
        return TimeUtil.add_duration(base_time, **kwargs)

    @staticmethod
    def subtract_from_now(utc: bool = True, **kwargs) -> datetime:
        """Subtract a duration from the current time.

        Convenience method that subtracts a duration from the current timestamp.
        By default uses UTC time, but can use local time if specified.

        Args:
            utc: If True, uses UTC time; if False, uses local time. Default is True.
            **kwargs: Duration components (days, hours, minutes, seconds, years, months, weeks)
                     passed to timedelta constructor.

        Returns:
            datetime: New timezone-aware datetime representing current time minus duration.

        Example:
            >>> from morado.common.utils.time import TimeUtil
            >>> # Get time 2 hours ago (UTC)
            >>> past = TimeUtil.subtract_from_now(hours=2)
            >>> # Get time 3 days and 5 hours ago (local time)
            >>> past_local = TimeUtil.subtract_from_now(utc=False, days=3, hours=5)
            >>> # Get time 1 week ago
            >>> last_week = TimeUtil.subtract_from_now(weeks=1)
            >>> # Get time 30 minutes ago
            >>> half_hour_ago = TimeUtil.subtract_from_now(minutes=30)

        Note:
            This is equivalent to:
            TimeUtil.subtract_duration(TimeUtil.now_utc(), **kwargs)
            or
            TimeUtil.subtract_duration(TimeUtil.now_local(), **kwargs)
        """
        base_time = TimeUtil.now_utc() if utc else TimeUtil.now_local()
        return TimeUtil.subtract_duration(base_time, **kwargs)

    @staticmethod
    def add_to_time(dt: datetime | None = None, utc: bool = True, **kwargs) -> datetime:
        """Add a duration to a specified time or current time.

        Flexible method that adds a duration to either a specified datetime or
        the current time. If no datetime is provided, uses current time (UTC or local).

        Args:
            dt: Optional timezone-aware datetime object. If None, uses current time.
            utc: If dt is None and utc is True, uses UTC time; if False, uses local time.
                 Ignored if dt is provided. Default is True.
            **kwargs: Duration components (days, hours, minutes, seconds, years, months, weeks)
                     passed to timedelta constructor.

        Returns:
            datetime: New timezone-aware datetime with the duration added.

        Raises:
            ValueError: If dt is provided but is naive (lacks timezone information).
            TypeError: If dt is not a datetime object or None.

        Example:
            >>> from morado.common.utils.time import TimeUtil
            >>> from datetime import datetime, timezone
            >>> # Add to current time (UTC)
            >>> future = TimeUtil.add_to_time(hours=2)
            >>> # Add to current local time
            >>> future_local = TimeUtil.add_to_time(utc=False, days=1)
            >>> # Add to specific time
            >>> specific = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
            >>> result = TimeUtil.add_to_time(specific, hours=3, minutes=30)
            >>> result.hour
            13
            >>> result.minute
            30

        Note:
            This method combines the functionality of add_duration() and add_to_now()
            for maximum flexibility.
        """
        if dt is None:
            base_time = TimeUtil.now_utc() if utc else TimeUtil.now_local()
        else:
            if not isinstance(dt, datetime):
                msg = f"Expected datetime object or None, got {type(dt).__name__}"
                raise TypeError(
                    msg
                )
            base_time = dt

        return TimeUtil.add_duration(base_time, **kwargs)

    @staticmethod
    def subtract_from_time(
        dt: datetime | None = None, utc: bool = True, **kwargs
    ) -> datetime:
        """Subtract a duration from a specified time or current time.

        Flexible method that subtracts a duration from either a specified datetime or
        the current time. If no datetime is provided, uses current time (UTC or local).

        Args:
            dt: Optional timezone-aware datetime object. If None, uses current time.
            utc: If dt is None and utc is True, uses UTC time; if False, uses local time.
                 Ignored if dt is provided. Default is True.
            **kwargs: Duration components (days, hours, minutes, seconds, years, months, weeks)
                     passed to timedelta constructor.

        Returns:
            datetime: New timezone-aware datetime with the duration subtracted.

        Raises:
            ValueError: If dt is provided but is naive (lacks timezone information).
            TypeError: If dt is not a datetime object or None.

        Example:
            >>> from morado.common.utils.time import TimeUtil
            >>> from datetime import datetime, timezone
            >>> # Subtract from current time (UTC)
            >>> past = TimeUtil.subtract_from_time(hours=2)
            >>> # Subtract from current local time
            >>> past_local = TimeUtil.subtract_from_time(utc=False, days=1)
            >>> # Subtract from specific time
            >>> specific = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
            >>> result = TimeUtil.subtract_from_time(specific, hours=3, minutes=30)
            >>> result.hour
            6
            >>> result.minute
            30

        Note:
            This method combines the functionality of subtract_duration() and
            subtract_from_now() for maximum flexibility.
        """
        if dt is None:
            base_time = TimeUtil.now_utc() if utc else TimeUtil.now_local()
        else:
            if not isinstance(dt, datetime):
                msg = f"Expected datetime object or None, got {type(dt).__name__}"
                raise TypeError(
                    msg
                )
            base_time = dt

        return TimeUtil.subtract_duration(base_time, **kwargs)

    @staticmethod
    def convert_timezone(dt: datetime, target_tz: str | ZoneInfo) -> datetime:
        """Convert a timestamp to a target timezone.

        Converts a timezone-aware datetime to a different timezone. The conversion
        preserves the absolute point in time (the UTC equivalent remains the same),
        only changing the timezone representation. Handles daylight saving time
        transitions correctly.

        Args:
            dt: A timezone-aware datetime object to convert.
            target_tz: Target timezone as a string (e.g., "America/New_York", "UTC")
                      or a ZoneInfo object.

        Returns:
            datetime: New datetime object in the target timezone representing the
                     same absolute point in time.

        Raises:
            ValueError: If the datetime is naive (lacks timezone information) or
                       if the timezone name is invalid.
            TypeError: If dt is not a datetime object or target_tz is not a string or ZoneInfo.

        Example:
            >>> from morado.common.utils.time import TimeUtil
            >>> from datetime import datetime, timezone
            >>> # Create a UTC time
            >>> utc_dt = datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc)
            >>> # Convert to New York time
            >>> ny_dt = TimeUtil.convert_timezone(utc_dt, "America/New_York")
            >>> ny_dt.hour  # 5 hours behind UTC (EST)
            9
            >>> # Verify absolute time is preserved
            >>> utc_dt.timestamp() == ny_dt.timestamp()
            True
            >>> # Convert to Tokyo time
            >>> tokyo_dt = TimeUtil.convert_timezone(utc_dt, "Asia/Tokyo")
            >>> tokyo_dt.hour  # 9 hours ahead of UTC
            23
            >>> # Round-trip conversion
            >>> back_to_utc = TimeUtil.convert_timezone(ny_dt, "UTC")
            >>> back_to_utc == utc_dt
            True

        Note:
            Common timezone names:
            - "UTC" or "GMT"
            - "America/New_York", "America/Los_Angeles", "America/Chicago"
            - "Europe/London", "Europe/Paris", "Europe/Berlin"
            - "Asia/Tokyo", "Asia/Shanghai", "Asia/Kolkata"

            The conversion automatically handles daylight saving time transitions.
            Use ZoneInfo.available_timezones() to see all available timezone names.
        """
        if not isinstance(dt, datetime):
            msg = f"Expected datetime object, got {type(dt).__name__}"
            raise TypeError(msg)

        if dt.tzinfo is None:
            raise ValueError(
                "Cannot convert naive datetime. Use timezone-aware datetime objects. "
                "Consider using TimeUtil.now_utc() or adding timezone with "
                "dt.replace(tzinfo=timezone.utc)"
            )

        # Convert target_tz to ZoneInfo if it's a string
        if isinstance(target_tz, str):
            try:
                target_zone = ZoneInfo(target_tz)
            except Exception as e:
                # Provide helpful error message with suggestions
                msg = (
                    f"Invalid timezone name '{target_tz}': {e!s}. "
                    f"Use standard timezone names like 'UTC', 'America/New_York', "
                    f"'Europe/London', 'Asia/Tokyo', etc. "
                    f"See ZoneInfo.available_timezones() for all available names."
                )
                raise ValueError(
                    msg
                )
        elif isinstance(target_tz, ZoneInfo):
            target_zone = target_tz
        else:
            msg = f"Expected string or ZoneInfo for target_tz, got {type(target_tz).__name__}"
            raise TypeError(
                msg
            )

        # Convert to target timezone
        return dt.astimezone(target_zone)
