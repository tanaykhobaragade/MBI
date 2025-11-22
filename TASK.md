***

# **TASKS.md - MBI Project Implementation Guide**

**Project:** Automated Market Breadth Indicator for NIFTY MIDSMALLCAP 400  
**Tech Stack:** Python 3.12+, UV package manager, yFinance, GitHub Actions, GitHub Pages  
**Last Updated:** November 22, 2025

***

## 🎯 **PROJECT OVERVIEW**

Build a fully automated system to calculate and display Market Breadth Indicator (MBI) metrics for 400 stocks from the NIFTY MIDSMALLCAP 400 index. The system fetches daily EOD data, calculates 16 breadth metrics, and displays results via a GitHub Pages dashboard accessible from any device.

***

## ⚠️ **CRITICAL DECISIONS & CONSTRAINTS**

### **Data Source: yFinance (NOT Upstox API)**
**Reasoning:**
- ✅ **Zero cost** (Upstox requires ₹2000/month subscription)
- ✅ **No authentication hassles** (Upstox requires daily OAuth token refresh at 3:30 AM)
- ✅ **Auto-adjusted data** for stock splits & bonuses (Upstox requires manual adjustment)
- ✅ **Unlimited historical data** (Upstox limited to 1 year)
- ✅ **Perfect for GitHub Actions** automation (no login required)

**STRICT RULE:** Do NOT use Upstox API. Use yFinance exclusively.

### **Python Version: 3.12+**
- Use latest Python features
- Modern type hints with `from __future__ import annotations`
- Use `zoneinfo.ZoneInfo` instead of pytz where possible

### **Package Manager: UV**
- Use UV (not pip) for dependency management
- All dependencies in `pyproject.toml`
- Use `uv sync` to install dependencies

### **Timezone Handling: MANDATORY**
- **NSE operates in IST (UTC+5:30)**
- **yFinance uses UTC timestamps**
- **GitHub Actions runs in UTC**
- **RULE:** Always convert IST ↔ UTC explicitly. Never assume timezone.

***

## 📊 **THREE-TIER DATA STRUCTURE**

### **Type 1: Raw Data (Per Stock)**
**Location:** `data/raw/stocks/{SYMBOL}.csv`
```csv
Date,Open,High,Low,Close,Volume
2024-11-22,2515.00,2530.00,2505.00,2520.00,5000000
```

- One file per stock (400 files total)
- Auto-adjusted for splits/bonuses by yFinance
- Append daily, don't overwrite
- **Date must be in IST timezone**


### **Type 2: Date-wise Consolidated**

**Location:** `data/raw/daily/{YYYY-MM-DD}.csv`

```csv
Symbol,Open,High,Low,Close,Volume,SMA_10,SMA_20,SMA_50,SMA_200,High_52W,Low_52W
RELIANCE.NS,2515.00,2530.00,2505.00,2520.00,5000000,2510.50,2505.30,2480.20,2400.10,2600.00,2200.00
```

- All 400 stocks for one trading date
- Pre-calculated SMAs for performance
- Created after daily fetch completes


### **Type 3: Final MBI Data**

**Location:** `data/processed/market_breadth.csv`

```csv
Date,52WH(%),52WL(%),4.5+(%),4.5-(%),10+(%),10-(%),20+(%),20-(%),50+(%),50-(%),200+(%),200-(%),4.5r,20sma,50sma
```

- One row per trading day
- All 16 breadth metrics
- Used by GitHub Pages dashboard and Google Sheets

***

## 🏗️ **PROJECT STRUCTURE TO IMPLEMENT**

```
MBI/
├── .github/workflows/
│   ├── fetch_daily_data.yml           # ⏰ Daily 6 PM IST automation
│   └── initialize_historical.yml       # 🔄 One-time historical fetch
├── data/
│   ├── raw/
│   │   ├── stocks/                    # 📁 400 individual stock CSVs
│   │   └── daily/                     # 📅 Date-wise consolidated
│   ├── processed/
│   │   └── market_breadth.csv         # 📊 Final MBI output
│   └── meta/
│       ├── nifty_midsmallcap400.csv   # 📋 Index constituents
│       └── nse_holidays_YYYY.json     # 🗓️ Holiday calendars
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                  # 🔧 All configuration constants
│   │   ├── timezone_handler.py        # ⏰ IST/UTC conversions
│   │   └── logger.py                  # 📝 Logging setup
│   ├── fetchers/
│   │   ├── __init__.py
│   │   ├── yfinance_fetcher.py       # 📥 Fetch stock data via yFinance
│   │   └── index_fetcher.py          # 📋 Fetch NIFTY constituents
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── data_validator.py         # ✅ Data quality checks
│   │   ├── date_consolidator.py      # 📅 Create date-wise CSVs
│   │   └── breadth_calculator.py     # 🧮 Calculate 16 MBI metrics
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── holiday_checker.py        # 🗓️ NSE holiday logic
│   │   ├── file_manager.py           # 💾 CSV operations
│   │   └── corporate_actions.py      # 📊 Split/bonus notes
│   └── main.py                        # 🚀 CLI entry point
├── docs/                              # 🌐 GitHub Pages dashboard
│   ├── index.html                     # Dashboard UI
│   └── assets/
│       ├── css/style.css
│       └── js/dashboard.js
├── tests/
│   ├── test_fetchers.py
│   ├── test_processors.py
│   └── test_utils.py
├── pyproject.toml                     # 📦 UV project config
├── .python-version                    # 🐍 Python 3.12
├── .gitignore
├── LICENSE
├── README.md
└── TASKS.md (this file)
```


***

## 🔨 **IMPLEMENTATION TASKS**

### **TASK 1: Setup Project Configuration**

#### **1.1 Create `pyproject.toml`**

```toml
[project]
name = "mbi"
version = "1.0.0"
description = "Automated Market Breadth Indicator for NIFTY MIDSMALLCAP 400"
requires-python = ">=3.12"
dependencies = [
    "yfinance>=0.2.66",
    "pandas>=2.2.0",
    "numpy>=1.26.0",
    "pytz>=2024.1",
    "holidays>=0.58",
    "requests>=2.32.0",
    "beautifulsoup4>=4.12.0",
    "lxml>=5.1.0",
    "pydantic>=2.7.0",
    "rich>=13.7.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.3.0",
    "mypy>=1.9.0",
]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.mypy]
python_version = "3.12"
strict = true
```


#### **1.2 Create `.python-version`**

```
3.12
```


#### **1.3 Update `requirements.txt`**

Replace current content with:

```
yfinance>=0.2.66
pandas>=2.2.0
numpy>=1.26.0
pytz>=2024.1
holidays>=0.58
requests>=2.32.0
beautifulsoup4>=4.12.0
lxml>=5.1.0
pydantic>=2.7.0
rich>=13.7.0
```


***

### **TASK 2: Core Modules**

#### **2.1 `src/core/config.py`**

**Requirements:**

- Define all constants (SMA periods, thresholds, paths)
- Use `pathlib.Path` for all file paths
- Timezone constants (IST, UTC)
- NSE endpoints if needed
- Minimum valid stocks = 350 out of 400

**Template:**

```python
from pathlib import Path
from zoneinfo import ZoneInfo

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_STOCKS_DIR = DATA_DIR / "raw" / "stocks"
RAW_DAILY_DIR = DATA_DIR / "raw" / "daily"
PROCESSED_DIR = DATA_DIR / "processed"
META_DIR = DATA_DIR / "meta"

# Timezones
IST = ZoneInfo("Asia/Kolkata")
UTC = ZoneInfo("UTC")

# SMA periods
SMA_PERIODS = [10, 20, 50, 200]

# Thresholds
DAILY_CHANGE_THRESHOLD = 4.5  # for 4.5+/- calculations
MIN_VALID_STOCKS = 350  # out of 400

# Historical data range
HISTORICAL_DAYS = 365

# Index name
INDEX_NAME = "NIFTY MIDSMALLCAP 400"

# Output columns
BREADTH_COLUMNS = [
    "Date", "52WH(%)", "52WL(%)", "4.5+(%)", "4.5-(%)",
    "10+(%)", "10-(%)", "20+(%)", "20-(%)", "50+(%)", "50-(%)",
    "200+(%)", "200-(%)", "4.5r", "20sma", "50sma"
]
```


#### **2.2 `src/core/timezone_handler.py`**

**Requirements:**

- Convert IST ↔ UTC
- Get current IST time
- Check if within market hours (9:15 AM - 3:30 PM IST)
- Get trading date range in IST

**Critical Functions:**

```python
def get_current_ist_time() -> datetime:
    """Get current time in IST"""
    
def convert_ist_to_utc(ist_dt: datetime) -> datetime:
    """Convert IST datetime to UTC for yFinance"""
    
def convert_utc_to_ist(utc_dt: datetime) -> datetime:
    """Convert UTC datetime to IST"""
    
def is_market_hours() -> bool:
    """Check if NSE is currently open (9:15 AM - 3:30 PM IST)"""
    
def get_trading_date_range(days_back: int = 365) -> tuple[datetime, datetime]:
    """Get date range for historical fetch in IST"""
```


#### **2.3 `src/core/logger.py`**

**Requirements:**

- Use `rich` for beautiful console output
- Different log levels for GitHub Actions vs local
- Include timestamps in IST
- Log to both console and file

***

### **TASK 3: Data Fetchers**

#### **3.1 `src/fetchers/yfinance_fetcher.py`**

**Requirements:**

- Fetch data using yFinance library
- **CRITICAL:** Use `.NS` suffix for NSE stocks (e.g., `RELIANCE.NS`)
- Use `auto_adjust=True` (default) for automatic split/bonus adjustment
- Handle rate limits gracefully
- Retry logic (3 attempts with exponential backoff)
- Convert UTC timestamps from yFinance to IST dates

**Key Functions:**

```python
def fetch_stock_data(
    symbol: str,
    start_date: datetime,
    end_date: datetime,
    retry_count: int = 3
) -> pd.DataFrame | None:
    """
    Fetch OHLCV data for a single stock using yFinance.
    
    Args:
        symbol: Stock symbol WITH .NS suffix (e.g., 'RELIANCE.NS')
        start_date: Start date in IST
        end_date: End date in IST
        retry_count: Number of retry attempts
        
    Returns:
        DataFrame with columns: Date, Open, High, Low, Close, Volume
        Dates converted to IST timezone
        Returns None if fetch fails
        
    IMPORTANT:
    - yFinance returns UTC timestamps, convert to IST
    - auto_adjust=True ensures split/bonus adjusted data
    - Handle weekends/holidays gracefully (yFinance returns empty)
    """

def fetch_all_stocks_for_date(
    symbols: list[str],
    date: datetime
) -> dict[str, pd.DataFrame]:
    """
    Fetch data for all stocks for a specific date.
    Returns dict of {symbol: dataframe}
    """

def save_stock_data(symbol: str, df: pd.DataFrame) -> None:
    """
    Save/append stock data to individual CSV file.
    Create file if doesn't exist, append if exists.
    """
```


#### **3.2 `src/fetchers/index_fetcher.py`**

**Requirements:**

- Fetch NIFTY MIDSMALLCAP 400 constituents
- Source: NSE website or Wikipedia
- Save to `data/meta/nifty_midsmallcap400.csv`
- Format: `Symbol,Company_Name,Industry`
- Add `.NS` suffix to all symbols for yFinance compatibility

**Function:**

```python
def fetch_index_constituents() -> pd.DataFrame:
    """
    Fetch current constituents of NIFTY MIDSMALLCAP 400.
    Returns DataFrame with Symbol (with .NS suffix), Company_Name, Industry
    """

def save_constituents(df: pd.DataFrame) -> None:
    """Save constituents to CSV in data/meta/"""

def load_constituents() -> pd.DataFrame:
    """Load constituents from CSV, fetch if not exists"""
```


***

### **TASK 4: Utilities**

#### **4.1 `src/utils/holiday_checker.py`**

**Requirements:**

- Use `holidays` library for Indian holidays
- NSE-specific holidays (Muhurat trading, etc.)
- Check if given date is trading day
- Save/load holiday calendar from JSON

**Functions:**

```python
def get_nse_holidays(year: int) -> list[datetime]:
    """
    Get NSE trading holidays for a given year.
    Includes:
    - Indian national holidays
    - NSE-specific holidays
    - Diwali Muhurat trading (partial holiday)
    """

def is_trading_day(date: datetime | None = None) -> bool:
    """
    Check if given date (default: today) is a trading day.
    Returns False for:
    - Weekends (Saturday, Sunday)
    - NSE holidays
    """

def save_holidays_to_file(year: int) -> None:
    """Save holiday calendar to data/meta/nse_holidays_{year}.json"""

def load_holidays_from_file(year: int) -> list[datetime]:
    """Load holidays from JSON, fetch if not

---
