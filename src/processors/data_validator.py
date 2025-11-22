"""Data validation utilities."""

from __future__ import annotations

import pandas as pd

from src.core.config import MIN_PRICE, MIN_VOLUME, MIN_VALID_STOCKS
from src.core.logger import get_logger


logger = get_logger(__name__)


def validate_stock_data(df: pd.DataFrame, symbol: str) -> tuple[bool, list[str]]:
    """
    Validate stock data for quality issues.
    
    Args:
        df: Stock data DataFrame
        symbol: Stock symbol for logging
        
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    
    # Check if DataFrame is empty
    if df is None or df.empty:
        issues.append("DataFrame is empty")
        return False, issues
    
    # Check required columns
    required_cols = ["Date", "Open", "High", "Low", "Close", "Volume"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        issues.append(f"Missing columns: {missing_cols}")
        return False, issues
    
    # Check for null values
    null_counts = df[required_cols].isnull().sum()
    if null_counts.any():
        for col, count in null_counts.items():
            if count > 0:
                issues.append(f"{col} has {count} null values")
    
    # Check for negative prices
    price_cols = ["Open", "High", "Low", "Close"]
    for col in price_cols:
        negative_count = (df[col] < MIN_PRICE).sum()
        if negative_count > 0:
            issues.append(f"{col} has {negative_count} negative/zero values")
    
    # Check for negative volume
    negative_volume = (df["Volume"] < MIN_VOLUME).sum()
    if negative_volume > 0:
        issues.append(f"Volume has {negative_volume} negative values")
    
    # Check High >= Low
    invalid_hl = (df["High"] < df["Low"]).sum()
    if invalid_hl > 0:
        issues.append(f"{invalid_hl} rows have High < Low")
    
    # Check Close within High/Low range
    invalid_close = ((df["Close"] > df["High"]) | (df["Close"] < df["Low"])).sum()
    if invalid_close > 0:
        issues.append(f"{invalid_close} rows have Close outside High/Low range")
    
    # Check for duplicate dates
    duplicate_dates = df["Date"].duplicated().sum()
    if duplicate_dates > 0:
        issues.append(f"{duplicate_dates} duplicate dates found")
    
    is_valid = len(issues) == 0
    
    if not is_valid:
        logger.warning(f"Validation issues for {symbol}: {', '.join(issues)}")
    
    return is_valid, issues


def validate_consolidated_data(df: pd.DataFrame, date: str, total_symbols: int) -> tuple[bool, str]:
    """
    Validate consolidated daily data.
    
    Args:
        df: Consolidated data DataFrame
        date: Date being validated
        total_symbols: Total number of symbols expected
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if df is None or df.empty:
        return False, "DataFrame is empty"
    
    # Check if we have enough stocks
    if len(df) < MIN_VALID_STOCKS:
        return False, f"Only {len(df)}/{total_symbols} stocks available (minimum: {MIN_VALID_STOCKS})"
    
    # Check required columns
    required_cols = ["Symbol", "Open", "High", "Low", "Close", "Volume"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        return False, f"Missing columns: {missing_cols}"
    
    logger.info(f"Validation passed for {date}: {len(df)}/{total_symbols} stocks available")
    return True, ""


def check_data_quality(df: pd.DataFrame) -> dict[str, int]:
    """
    Check data quality and return statistics.
    
    Args:
        df: DataFrame to check
        
    Returns:
        Dictionary with quality metrics
    """
    stats = {
        "total_rows": len(df),
        "null_values": df.isnull().sum().sum(),
        "duplicate_dates": df["Date"].duplicated().sum() if "Date" in df.columns else 0,
        "zero_volume": (df["Volume"] == 0).sum() if "Volume" in df.columns else 0,
    }
    
    if "Close" in df.columns:
        stats["min_price"] = df["Close"].min()
        stats["max_price"] = df["Close"].max()
    
    return stats


def remove_invalid_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove invalid rows from DataFrame.
    
    Args:
        df: Stock data DataFrame
        
    Returns:
        Cleaned DataFrame
    """
    original_len = len(df)
    
    # Remove rows with null values
    df = df.dropna()
    
    # Remove rows with negative/zero prices
    price_cols = ["Open", "High", "Low", "Close"]
    for col in price_cols:
        df = df[df[col] > MIN_PRICE]
    
    # Remove rows with High < Low
    df = df[df["High"] >= df["Low"]]
    
    # Remove rows with Close outside High/Low
    df = df[(df["Close"] >= df["Low"]) & (df["Close"] <= df["High"])]
    
    # Remove duplicate dates (keep last)
    df = df.drop_duplicates(subset=["Date"], keep="last")
    
    removed = original_len - len(df)
    if removed > 0:
        logger.info(f"Removed {removed} invalid rows")
    
    return df
