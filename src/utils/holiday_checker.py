"""NSE holiday checker and trading day utilities."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

import holidays

from src.core.config import META_DIR, IST
from src.core.logger import get_logger


logger = get_logger(__name__)


def get_nse_holidays(year: int) -> list[datetime]:
    """
    Get NSE trading holidays for a given year.
    
    Args:
        year: Year to get holidays for
        
    Returns:
        List of holiday dates
        
    Note:
        Includes:
        - Indian national holidays
        - NSE-specific holidays
        - Weekends are NOT included (handled separately)
    """
    # Get Indian holidays
    india_holidays = holidays.India(years=year)
    
    holiday_list = []
    
    for date, name in sorted(india_holidays.items()):
        # Convert to datetime with IST timezone
        dt = datetime.combine(date, datetime.min.time()).replace(tzinfo=IST)
        holiday_list.append(dt)
        logger.debug(f"Holiday: {date} - {name}")
    
    # Additional NSE-specific holidays (Muhurat trading, special closures)
    # These need to be manually maintained
    nse_special_holidays = _get_nse_special_holidays(year)
    holiday_list.extend(nse_special_holidays)
    
    # Remove duplicates and sort
    holiday_list = sorted(list(set(holiday_list)))
    
    logger.info(f"Found {len(holiday_list)} holidays for {year}")
    
    return holiday_list


def _get_nse_special_holidays(year: int) -> list[datetime]:
    """
    Get NSE-specific special holidays.
    
    Args:
        year: Year to get holidays for
        
    Returns:
        List of special holiday dates
        
    Note:
        This is a manual list that needs to be updated annually.
        Check NSE website for current year's holidays.
    """
    special_holidays = []
    
    # Example: Muhurat trading (Diwali) - NSE open for 1 hour, but we treat as holiday
    # Add specific dates here as needed
    
    # For 2024-2025, add known special holidays
    if year == 2024:
        # Add Diwali special holidays if not already in India holidays
        pass
    
    if year == 2025:
        # Update with 2025 NSE holidays
        pass
    
    return special_holidays


def is_trading_day(date: datetime | None = None) -> bool:
    """
    Check if given date is a trading day.
    
    Args:
        date: Date to check (default: today in IST)
        
    Returns:
        True if trading day, False if weekend or holiday
    """
    if date is None:
        from src.core.timezone_handler import get_current_ist_time
        date = get_current_ist_time()
    
    # Ensure timezone is IST
    if date.tzinfo is None:
        date = date.replace(tzinfo=IST)
    
    # Check if weekend (Saturday=5, Sunday=6)
    if date.weekday() >= 5:
        logger.debug(f"{date.date()} is a weekend")
        return False
    
    # Check if holiday
    year = date.year
    holidays_list = get_nse_holidays(year)
    
    # Normalize date for comparison (remove time component)
    date_normalized = date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    for holiday in holidays_list:
        holiday_normalized = holiday.replace(hour=0, minute=0, second=0, microsecond=0)
        if date_normalized == holiday_normalized:
            logger.debug(f"{date.date()} is a holiday")
            return False
    
    return True


def get_next_trading_day(date: datetime | None = None) -> datetime:
    """
    Get the next trading day after given date.
    
    Args:
        date: Reference date (default: today)
        
    Returns:
        Next trading day
    """
    if date is None:
        from src.core.timezone_handler import get_current_ist_time
        date = get_current_ist_time()
    
    # Ensure timezone is IST
    if date.tzinfo is None:
        date = date.replace(tzinfo=IST)
    
    # Start from next day
    next_day = date + timedelta(days=1)
    
    # Keep incrementing until we find a trading day
    max_attempts = 30  # Safety limit
    attempts = 0
    
    while not is_trading_day(next_day) and attempts < max_attempts:
        next_day = next_day + timedelta(days=1)
        attempts += 1
    
    if attempts >= max_attempts:
        logger.error(f"Could not find next trading day after {date.date()}")
        return next_day
    
    return next_day.replace(hour=0, minute=0, second=0, microsecond=0)


def get_previous_trading_day(date: datetime | None = None) -> datetime:
    """
    Get the previous trading day before given date.
    
    Args:
        date: Reference date (default: today)
        
    Returns:
        Previous trading day
    """
    if date is None:
        from src.core.timezone_handler import get_current_ist_time
        date = get_current_ist_time()
    
    # Ensure timezone is IST
    if date.tzinfo is None:
        date = date.replace(tzinfo=IST)
    
    # Start from previous day
    prev_day = date - timedelta(days=1)
    
    # Keep decrementing until we find a trading day
    max_attempts = 30  # Safety limit
    attempts = 0
    
    while not is_trading_day(prev_day) and attempts < max_attempts:
        prev_day = prev_day - timedelta(days=1)
        attempts += 1
    
    if attempts >= max_attempts:
        logger.error(f"Could not find previous trading day before {date.date()}")
        return prev_day
    
    return prev_day.replace(hour=0, minute=0, second=0, microsecond=0)


def save_holidays_to_file(year: int) -> None:
    """
    Save holiday calendar to JSON file.
    
    Args:
        year: Year to save holidays for
    """
    META_DIR.mkdir(parents=True, exist_ok=True)
    
    holidays_list = get_nse_holidays(year)
    
    # Convert to serializable format
    holidays_data = {
        "year": year,
        "holidays": [dt.strftime("%Y-%m-%d") for dt in holidays_list],
    }
    
    filepath = META_DIR / f"nse_holidays_{year}.json"
    
    with open(filepath, "w") as f:
        json.dump(holidays_data, f, indent=2)
    
    logger.info(f"Saved {len(holidays_list)} holidays to {filepath}")


def load_holidays_from_file(year: int) -> list[datetime]:
    """
    Load holidays from JSON file.
    
    Args:
        year: Year to load holidays for
        
    Returns:
        List of holiday dates
        
    Note:
        Fetches from source if file doesn't exist.
    """
    filepath = META_DIR / f"nse_holidays_{year}.json"
    
    if not filepath.exists():
        logger.info(f"Holiday file not found for {year}, generating...")
        save_holidays_to_file(year)
    
    with open(filepath, "r") as f:
        data = json.load(f)
    
    # Convert strings back to datetime
    holidays_list = [
        datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=IST)
        for date_str in data["holidays"]
    ]
    
    return holidays_list


def get_trading_days_in_range(start_date: datetime, end_date: datetime) -> list[datetime]:
    """
    Get all trading days in a date range.
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        List of trading days
    """
    trading_days = []
    
    current = start_date
    while current <= end_date:
        if is_trading_day(current):
            trading_days.append(current)
        current = current + timedelta(days=1)
    
    return trading_days
