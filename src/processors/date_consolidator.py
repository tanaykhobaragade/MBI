"""Date-wise data consolidation and SMA calculations."""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import numpy as np

from src.core.config import RAW_STOCKS_DIR, RAW_DAILY_DIR, SMA_PERIODS, YFINANCE_SUFFIX
from src.core.logger import get_logger
from src.fetchers.yfinance_fetcher import load_stock_data


logger = get_logger(__name__)


def calculate_sma(df: pd.DataFrame, periods: list[int]) -> pd.DataFrame:
    """
    Calculate Simple Moving Averages for given periods.
    
    Args:
        df: Stock data with Date and Close columns
        periods: List of SMA periods (e.g., [10, 20, 50, 200])
        
    Returns:
        DataFrame with SMA columns added
    """
    df = df.copy()
    
    # Ensure sorted by date
    df = df.sort_values("Date")
    
    for period in periods:
        col_name = f"SMA_{period}"
        df[col_name] = df["Close"].rolling(window=period, min_periods=1).mean()
    
    return df


def calculate_52week_high_low(df: pd.DataFrame, reference_date: datetime) -> tuple[float, float]:
    """
    Calculate 52-week high and low for a specific date.
    
    Args:
        df: Stock data with Date, High, Low columns
        reference_date: Date to calculate from
        
    Returns:
        Tuple of (52_week_high, 52_week_low)
    """
    # Get data for last 252 trading days (approx 1 year)
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")
    
    # Convert reference_date to naive comparable format
    ref_ts = pd.Timestamp(reference_date.date()).normalize()
    df = df[df["Date"].dt.normalize() <= ref_ts]
    
    # Take last 252 rows
    df_year = df.tail(252)
    
    if df_year.empty:
        return np.nan, np.nan
    
    high_52w = df_year["High"].max()
    low_52w = df_year["Low"].min()
    
    return high_52w, low_52w


def consolidate_date(date: datetime, symbols: list[str]) -> pd.DataFrame:
    """
    Consolidate all stock data for a specific date.
    
    Args:
        date: Target date
        symbols: List of stock symbols
        
    Returns:
        DataFrame with all stocks' data for the date, including SMAs and 52W H/L
    """
    consolidated_data = []
    
    for symbol in symbols:
        # Load stock data
        df = load_stock_data(symbol)
        
        if df is None or df.empty:
            logger.debug(f"No data for {symbol}")
            continue
        
        # Calculate SMAs
        df = calculate_sma(df, SMA_PERIODS)
        
        # Ensure Date column is datetime
        df["Date"] = pd.to_datetime(df["Date"])
        
        # Filter for specific date
        target_date = pd.Timestamp(date.date()).normalize()
        df_date = df[df["Date"].dt.normalize() == target_date]
        
        if df_date.empty:
            logger.debug(f"No data for {symbol} on {date.date()}")
            continue
        
        # Get the row for this date
        row = df_date.iloc[0]
        
        # Calculate 52-week high/low
        high_52w, low_52w = calculate_52week_high_low(df, date)
        
        # Create consolidated row
        consolidated_row = {
            "Symbol": symbol.replace(YFINANCE_SUFFIX, ""),
            "Open": row["Open"],
            "High": row["High"],
            "Low": row["Low"],
            "Close": row["Close"],
            "Volume": row["Volume"],
            "High_52W": high_52w,
            "Low_52W": low_52w,
        }
        
        # Add SMAs
        for period in SMA_PERIODS:
            col_name = f"SMA_{period}"
            consolidated_row[col_name] = row[col_name] if col_name in row else np.nan
        
        consolidated_data.append(consolidated_row)
    
    if not consolidated_data:
        logger.warning(f"No data consolidated for {date.date()}")
        return pd.DataFrame()
    
    df_consolidated = pd.DataFrame(consolidated_data)
    logger.info(f"Consolidated {len(df_consolidated)} stocks for {date.date()}")
    
    return df_consolidated


def create_daily_consolidated_file(date: datetime, symbols: list[str]) -> None:
    """
    Create date-wise consolidated CSV file.
    
    Args:
        date: Target date
        symbols: List of stock symbols
    """
    # Consolidate data
    df = consolidate_date(date, symbols)
    
    if df.empty:
        logger.error(f"Cannot create consolidated file for {date.date()} - no data")
        return
    
    # Ensure directory exists
    RAW_DAILY_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save to CSV
    date_str = date.strftime("%Y-%m-%d")
    filepath = RAW_DAILY_DIR / f"{date_str}.csv"
    df.to_csv(filepath, index=False)
    
    logger.info(f"Created consolidated file: {filepath}")


def load_daily_consolidated(date: datetime) -> pd.DataFrame | None:
    """
    Load consolidated data for a specific date.
    
    Args:
        date: Target date
        
    Returns:
        DataFrame with consolidated data, or None if file doesn't exist
    """
    date_str = date.strftime("%Y-%m-%d")
    filepath = RAW_DAILY_DIR / f"{date_str}.csv"
    
    if not filepath.exists():
        logger.warning(f"Consolidated file not found for {date.date()}")
        return None
    
    df = pd.read_csv(filepath)
    return df


def get_latest_consolidated_date() -> datetime | None:
    """
    Get the latest date for which consolidated data exists.
    
    Returns:
        Latest date as datetime, or None if no files exist
    """
    if not RAW_DAILY_DIR.exists():
        return None
    
    csv_files = list(RAW_DAILY_DIR.glob("*.csv"))
    
    if not csv_files:
        return None
    
    # Extract dates from filenames
    dates = []
    for file in csv_files:
        try:
            date_str = file.stem  # filename without extension
            date = datetime.strptime(date_str, "%Y-%m-%d")
            dates.append(date)
        except ValueError:
            continue
    
    if not dates:
        return None
    
    return max(dates)
