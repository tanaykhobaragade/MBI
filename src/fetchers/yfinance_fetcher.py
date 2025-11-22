"""yFinance data fetcher with retry logic and timezone handling."""

from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import yfinance as yf

from src.core.config import (
    RAW_STOCKS_DIR,
    YFINANCE_SUFFIX,
    YFINANCE_AUTO_ADJUST,
    MAX_RETRIES,
    RETRY_DELAY,
    RETRY_BACKOFF,
)
from src.core.timezone_handler import convert_utc_to_ist, convert_ist_to_utc
from src.core.logger import get_logger


logger = get_logger(__name__)


def fetch_stock_data(
    symbol: str,
    start_date: datetime,
    end_date: datetime,
    retry_count: int = MAX_RETRIES,
) -> pd.DataFrame | None:
    """
    Fetch OHLCV data for a single stock using yFinance.
    
    Args:
        symbol: Stock symbol WITH .NS suffix (e.g., 'RELIANCE.NS')
        start_date: Start date in IST timezone
        end_date: End date in IST timezone
        retry_count: Number of retry attempts
        
    Returns:
        DataFrame with columns: Date, Open, High, Low, Close, Volume
        Dates converted to IST timezone
        Returns None if fetch fails after retries
        
    Note:
        - yFinance returns UTC timestamps, converted to IST
        - auto_adjust=True ensures split/bonus adjusted data
        - Handles weekends/holidays gracefully (yFinance returns empty)
    """
    # Ensure symbol has .NS suffix
    if not symbol.endswith(YFINANCE_SUFFIX):
        symbol = f"{symbol}{YFINANCE_SUFFIX}"
    
    # Convert IST dates to UTC for yFinance
    start_utc = convert_ist_to_utc(start_date)
    end_utc = convert_ist_to_utc(end_date)
    
    for attempt in range(retry_count):
        try:
            logger.debug(f"Fetching {symbol} (attempt {attempt + 1}/{retry_count})")
            
            # Fetch data from yFinance
            ticker = yf.Ticker(symbol)
            df = ticker.history(
                start=start_utc,
                end=end_utc,
                auto_adjust=YFINANCE_AUTO_ADJUST,
                actions=False,  # Don't need dividends/splits info
            )
            
            # Check if data is empty
            if df.empty:
                logger.warning(f"No data returned for {symbol}")
                return None
            
            # Reset index to get Date as column
            df = df.reset_index()
            
            # Convert UTC datetime to IST date
            df["Date"] = df["Date"].apply(lambda x: convert_utc_to_ist(x).date())
            
            # Select and rename columns
            df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]
            
            # Convert Date to datetime for consistency
            df["Date"] = pd.to_datetime(df["Date"])
            
            logger.debug(f"Successfully fetched {len(df)} rows for {symbol}")
            return df
            
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed for {symbol}: {str(e)}")
            
            if attempt < retry_count - 1:
                # Exponential backoff
                sleep_time = RETRY_DELAY * (RETRY_BACKOFF ** attempt)
                logger.debug(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                logger.error(f"All {retry_count} attempts failed for {symbol}")
                return None
    
    return None


def fetch_all_stocks_for_date(
    symbols: list[str],
    date: datetime,
) -> dict[str, pd.DataFrame]:
    """
    Fetch data for all stocks for a specific date.
    
    Args:
        symbols: List of stock symbols (with or without .NS suffix)
        date: Target date in IST timezone
        
    Returns:
        Dictionary of {symbol: dataframe} with successful fetches
        
    Note:
        This fetches data for the single date, but yFinance may return
        a range. The caller should filter for the specific date.
    """
    results = {}
    
    # Fetch data for a 3-day window around the target date
    # (to handle timezone edge cases)
    from datetime import timedelta
    start = date - timedelta(days=1)
    end = date + timedelta(days=1)
    
    for symbol in symbols:
        df = fetch_stock_data(symbol, start, end)
        if df is not None and not df.empty:
            # Filter for exact date
            df["Date"] = pd.to_datetime(df["Date"])
            target_date = pd.Timestamp(date.date()).normalize()
            df = df[df["Date"].dt.normalize() == target_date]
            if not df.empty:
                results[symbol] = df
    
    logger.info(f"Fetched data for {len(results)}/{len(symbols)} stocks for {date.date()}")
    return results


def save_stock_data(symbol: str, df: pd.DataFrame) -> None:
    """
    Save stock data to individual CSV file (overwrite mode).
    
    Args:
        symbol: Stock symbol (without .NS suffix for filename)
        df: DataFrame with columns: Date, Open, High, Low, Close, Volume
        
    Note:
        Creates the file if it doesn't exist.
        Overwrites if it exists.
    """
    # Remove .NS suffix for filename
    clean_symbol = symbol.replace(YFINANCE_SUFFIX, "")
    
    # Ensure directory exists
    RAW_STOCKS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save to CSV
    filepath = RAW_STOCKS_DIR / f"{clean_symbol}.csv"
    df.to_csv(filepath, index=False)
    logger.debug(f"Saved {len(df)} rows to {filepath}")


def append_stock_data(symbol: str, df: pd.DataFrame) -> None:
    """
    Append stock data to existing CSV file.
    
    Args:
        symbol: Stock symbol (without .NS suffix for filename)
        df: DataFrame with columns: Date, Open, High, Low, Close, Volume
        
    Note:
        Creates file if it doesn't exist.
        Appends and removes duplicates if it exists.
    """
    # Remove .NS suffix for filename
    clean_symbol = symbol.replace(YFINANCE_SUFFIX, "")
    
    # Ensure directory exists
    RAW_STOCKS_DIR.mkdir(parents=True, exist_ok=True)
    
    filepath = RAW_STOCKS_DIR / f"{clean_symbol}.csv"
    
    if filepath.exists():
        # Load existing data
        existing_df = pd.read_csv(filepath)
        existing_df["Date"] = pd.to_datetime(existing_df["Date"])
        
        # Concatenate with new data
        combined_df = pd.concat([existing_df, df], ignore_index=True)
        
        # Remove duplicates (keep last occurrence)
        combined_df = combined_df.drop_duplicates(subset=["Date"], keep="last")
        
        # Sort by date
        combined_df = combined_df.sort_values("Date")
        
        # Save
        combined_df.to_csv(filepath, index=False)
        logger.debug(f"Appended {len(df)} rows to {filepath} (total: {len(combined_df)})")
    else:
        # Just save the new data
        save_stock_data(symbol, df)


def load_stock_data(symbol: str) -> pd.DataFrame | None:
    """
    Load stock data from CSV file.
    
    Args:
        symbol: Stock symbol (without .NS suffix)
        
    Returns:
        DataFrame with stock data, or None if file doesn't exist
    """
    # Remove .NS suffix if present
    clean_symbol = symbol.replace(YFINANCE_SUFFIX, "")
    
    filepath = RAW_STOCKS_DIR / f"{clean_symbol}.csv"
    
    if not filepath.exists():
        logger.warning(f"No data file found for {symbol}")
        return None
    
    df = pd.read_csv(filepath, parse_dates=False)
    df["Date"] = pd.to_datetime(df["Date"]).dt.normalize()
    return df


def get_latest_date_for_symbol(symbol: str) -> datetime | None:
    """
    Get the latest date available for a symbol.
    
    Args:
        symbol: Stock symbol (without .NS suffix)
        
    Returns:
        Latest date as datetime, or None if no data exists
    """
    df = load_stock_data(symbol)
    if df is None or df.empty:
        return None
    
    return df["Date"].max()
