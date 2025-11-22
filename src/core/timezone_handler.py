"""Timezone handling utilities for IST/UTC conversions."""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from src.core.config import IST, UTC, MARKET_OPEN_HOUR, MARKET_OPEN_MINUTE, MARKET_CLOSE_HOUR, MARKET_CLOSE_MINUTE


def get_current_ist_time() -> datetime:
    """
    Get current time in IST timezone.
    
    Returns:
        Current datetime in IST
    """
    return datetime.now(IST)


def convert_ist_to_utc(ist_dt: datetime) -> datetime:
    """
    Convert IST datetime to UTC for yFinance API calls.
    
    Args:
        ist_dt: Datetime in IST timezone (aware or naive)
        
    Returns:
        Datetime in UTC timezone
        
    Example:
        >>> ist_dt = datetime(2024, 11, 22, 15, 30, tzinfo=IST)
        >>> utc_dt = convert_ist_to_utc(ist_dt)
        >>> # Returns 2024-11-22 10:00 UTC
    """
    # If naive, assume IST
    if ist_dt.tzinfo is None:
        ist_dt = ist_dt.replace(tzinfo=IST)
    
    # Convert to UTC
    return ist_dt.astimezone(UTC)


def convert_utc_to_ist(utc_dt: datetime) -> datetime:
    """
    Convert UTC datetime to IST (for yFinance response parsing).
    
    Args:
        utc_dt: Datetime in UTC timezone (aware or naive)
        
    Returns:
        Datetime in IST timezone
        
    Example:
        >>> utc_dt = datetime(2024, 11, 22, 10, 0, tzinfo=UTC)
        >>> ist_dt = convert_utc_to_ist(utc_dt)
        >>> # Returns 2024-11-22 15:30 IST
    """
    # If naive, assume UTC
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=UTC)
    
    # Convert to IST
    return utc_dt.astimezone(IST)


def is_market_hours(dt: datetime | None = None) -> bool:
    """
    Check if NSE is currently open (9:15 AM - 3:30 PM IST).
    
    Args:
        dt: Datetime to check (default: current time)
        
    Returns:
        True if within market hours, False otherwise
        
    Note:
        Does not check for weekends or holidays, only time.
    """
    if dt is None:
        dt = get_current_ist_time()
    
    # Ensure timezone is IST
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=IST)
    else:
        dt = dt.astimezone(IST)
    
    # Market open: 9:15 AM
    market_open = dt.replace(hour=MARKET_OPEN_HOUR, minute=MARKET_OPEN_MINUTE, second=0, microsecond=0)
    
    # Market close: 3:30 PM
    market_close = dt.replace(hour=MARKET_CLOSE_HOUR, minute=MARKET_CLOSE_MINUTE, second=0, microsecond=0)
    
    return market_open <= dt <= market_close


def get_trading_date_range(days_back: int = 365) -> tuple[datetime, datetime]:
    """
    Get date range for historical fetch in IST.
    
    Args:
        days_back: Number of days to go back from today
        
    Returns:
        Tuple of (start_date, end_date) in IST timezone
        
    Example:
        >>> start, end = get_trading_date_range(365)
        >>> # Returns (one year ago at 00:00 IST, today at 23:59 IST)
    """
    end_date = get_current_ist_time().replace(hour=23, minute=59, second=59, microsecond=0)
    start_date = (end_date - timedelta(days=days_back)).replace(hour=0, minute=0, second=0, microsecond=0)
    
    return start_date, end_date


def get_previous_trading_date(dt: datetime | None = None) -> datetime:
    """
    Get the previous trading date (ignoring holidays).
    
    Args:
        dt: Reference datetime (default: current time)
        
    Returns:
        Previous date in IST timezone
        
    Note:
        This only goes back by 1 day. Holiday checking should be done separately.
    """
    if dt is None:
        dt = get_current_ist_time()
    
    # Ensure timezone is IST
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=IST)
    else:
        dt = dt.astimezone(IST)
    
    # Go back 1 day
    previous = dt - timedelta(days=1)
    return previous.replace(hour=0, minute=0, second=0, microsecond=0)


def normalize_to_date(dt: datetime) -> datetime:
    """
    Normalize datetime to date (00:00:00 IST).
    
    Args:
        dt: Datetime to normalize
        
    Returns:
        Datetime at 00:00:00 IST
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=IST)
    else:
        dt = dt.astimezone(IST)
    
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def format_date_for_filename(dt: datetime) -> str:
    """
    Format datetime for use in filenames (YYYY-MM-DD).
    
    Args:
        dt: Datetime to format
        
    Returns:
        Date string in YYYY-MM-DD format
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=IST)
    else:
        dt = dt.astimezone(IST)
    
    return dt.strftime("%Y-%m-%d")
