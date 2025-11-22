"""Configuration constants for MBI project."""

from __future__ import annotations

from pathlib import Path
from zoneinfo import ZoneInfo

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_STOCKS_DIR = DATA_DIR / "raw" / "stocks"
RAW_DAILY_DIR = DATA_DIR / "raw" / "daily"
PROCESSED_DIR = DATA_DIR / "processed"
META_DIR = DATA_DIR / "meta"

# Timezones
IST = ZoneInfo("Asia/Kolkata")
UTC = ZoneInfo("UTC")

# SMA periods for calculation
SMA_PERIODS = [10, 20, 50, 200]

# Thresholds
DAILY_CHANGE_THRESHOLD = 4.5  # for 4.5+/- calculations
MIN_VALID_STOCKS = 350  # out of 400 stocks, minimum valid data required

# Historical data range
HISTORICAL_DAYS = 365

# Index configuration
INDEX_NAME = "NIFTY MIDSMALLCAP 400"

# Output columns for market breadth CSV
BREADTH_COLUMNS = [
    "Date",
    "52WH(%)",  # % of stocks at 52-week high
    "52WL(%)",  # % of stocks at 52-week low
    "4.5+(%)",  # % of stocks up more than 4.5%
    "4.5-(%)",  # % of stocks down more than 4.5%
    "10+(%)",   # % of stocks above 10-day SMA
    "10-(%)",   # % of stocks below 10-day SMA
    "20+(%)",   # % of stocks above 20-day SMA
    "20-(%)",   # % of stocks below 20-day SMA
    "50+(%)",   # % of stocks above 50-day SMA
    "50-(%)",   # % of stocks below 50-day SMA
    "200+(%)",  # % of stocks above 200-day SMA
    "200-(%)",  # % of stocks below 200-day SMA
    "4.5r",     # Ratio of 4.5+ to 4.5-
    "20sma",    # Sum of stocks above 20-day SMA
    "50sma",    # Sum of stocks above 50-day SMA
]

# yFinance configuration
YFINANCE_SUFFIX = ".NS"  # NSE suffix for yFinance
YFINANCE_AUTO_ADJUST = True  # Auto-adjust for splits and bonuses

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
RETRY_BACKOFF = 2  # exponential backoff multiplier

# Market hours (IST)
MARKET_OPEN_HOUR = 9
MARKET_OPEN_MINUTE = 15
MARKET_CLOSE_HOUR = 15
MARKET_CLOSE_MINUTE = 30

# Daily automation time (6 PM IST)
AUTOMATION_HOUR = 18
AUTOMATION_MINUTE = 0

# Data validation
MIN_VOLUME = 0  # Minimum volume for valid data
MIN_PRICE = 0.01  # Minimum price for valid data

# File formats
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# NSE endpoints (if needed)
NSE_BASE_URL = "https://www.nseindia.com"
NSE_INDICES_URL = f"{NSE_BASE_URL}/api/equity-stockIndices"
