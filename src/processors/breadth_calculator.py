"""Market Breadth Indicator calculations."""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import numpy as np

from src.core.config import (
    PROCESSED_DIR,
    BREADTH_COLUMNS,
    DAILY_CHANGE_THRESHOLD,
)
from src.core.logger import get_logger
from src.processors.date_consolidator import load_daily_consolidated


logger = get_logger(__name__)


def calculate_breadth_metrics(df: pd.DataFrame, date: datetime) -> dict[str, float]:
    """
    Calculate all 16 breadth metrics for a given date.
    
    Args:
        df: Consolidated data for the date
        date: Target date
        
    Returns:
        Dictionary with all breadth metrics
    """
    total_stocks = len(df)
    
    if total_stocks == 0:
        logger.error("No stocks to calculate breadth metrics")
        return {}
    
    df = df.copy()
    metrics = {"Date": date.strftime("%Y-%m-%d")}
    
    # 1. 52-week High/Low percentages
    at_52w_high = (df["Close"] >= df["High_52W"]).sum()
    at_52w_low = (df["Close"] <= df["Low_52W"]).sum()
    
    metrics["52WH(%)"] = round((at_52w_high / total_stocks) * 100, 2)
    metrics["52WL(%)"] = round((at_52w_low / total_stocks) * 100, 2)
    
    # 2. Daily change 4.5+/- percentages
    # Prefer the previous close when available, otherwise fall back to open
    if "Prev_Close" in df.columns:
        base_price = df["Prev_Close"].replace(0, np.nan)
    else:
        base_price = df["Open"].replace(0, np.nan)
    
    df["Daily_Change_Pct"] = ((df["Close"] - base_price) / base_price) * 100
    fallback_mask = df["Daily_Change_Pct"].isna()
    if fallback_mask.any():
        fallback_base = df.loc[fallback_mask, "Open"].replace(0, np.nan)
        df.loc[fallback_mask, "Daily_Change_Pct"] = (
            (df.loc[fallback_mask, "Close"] - fallback_base) / fallback_base
        ) * 100
    
    up_4_5 = (df["Daily_Change_Pct"] > DAILY_CHANGE_THRESHOLD).sum()
    down_4_5 = (df["Daily_Change_Pct"] < -DAILY_CHANGE_THRESHOLD).sum()
    
    metrics["4.5+(%)"] = round((up_4_5 / total_stocks) * 100, 2)
    metrics["4.5-(%)"] = round((down_4_5 / total_stocks) * 100, 2)
    
    # 3. 4.5 ratio
    if down_4_5 > 0:
        metrics["4.5r"] = round(up_4_5 / down_4_5, 2)
    else:
        metrics["4.5r"] = 0.0 if up_4_5 == 0 else 99.99
    
    # 4. SMA-based percentages (10, 20, 50, 200)
    for period in [10, 20, 50, 200]:
        sma_col = f"SMA_{period}"
        
        if sma_col in df.columns:
            above_sma = (df["Close"] > df[sma_col]).sum()
            below_sma = (df["Close"] < df[sma_col]).sum()
            
            metrics[f"{period}+(%)"] = round((above_sma / total_stocks) * 100, 2)
            metrics[f"{period}-(%)"] = round((below_sma / total_stocks) * 100, 2)
        else:
            metrics[f"{period}+(%)"] = 0.0
            metrics[f"{period}-(%)"] = 0.0
    
    # 5. Sum of stocks above 20 and 50 SMA
    if "SMA_20" in df.columns:
        metrics["20sma"] = (df["Close"] > df["SMA_20"]).sum()
    else:
        metrics["20sma"] = 0
    
    if "SMA_50" in df.columns:
        metrics["50sma"] = (df["Close"] > df["SMA_50"]).sum()
    else:
        metrics["50sma"] = 0
    
    logger.info(f"Calculated breadth metrics for {date.strftime('%Y-%m-%d')}")
    
    return metrics


def calculate_all_metrics(start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """
    Calculate breadth metrics for a date range.
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        DataFrame with all breadth metrics for each date
    """
    all_metrics = []
    
    # Generate date range
    date_range = pd.date_range(start=start_date, end=end_date, freq="D")
    
    for date in date_range:
        # Load consolidated data for this date
        df = load_daily_consolidated(date)
        
        if df is None or df.empty:
            logger.debug(f"No data for {date.date()}, skipping")
            continue
        
        # Calculate metrics
        metrics = calculate_breadth_metrics(df, date)
        
        if metrics:
            all_metrics.append(metrics)
    
    if not all_metrics:
        logger.warning("No metrics calculated for the date range")
        return pd.DataFrame()
    
    # Create DataFrame
    df_metrics = pd.DataFrame(all_metrics)
    
    # Ensure correct column order
    df_metrics = df_metrics[BREADTH_COLUMNS]
    
    logger.info(f"Calculated metrics for {len(df_metrics)} dates")
    
    return df_metrics


def save_breadth_data(df: pd.DataFrame) -> None:
    """
    Save breadth metrics to processed CSV file.
    
    Args:
        df: DataFrame with breadth metrics
    """
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    filepath = PROCESSED_DIR / "market_breadth.csv"
    df.to_csv(filepath, index=False)
    
    logger.info(f"Saved breadth data to {filepath}")


def load_breadth_data() -> pd.DataFrame | None:
    """
    Load existing breadth metrics from CSV.
    
    Returns:
        DataFrame with breadth metrics, or None if file doesn't exist
    """
    filepath = PROCESSED_DIR / "market_breadth.csv"
    
    if not filepath.exists():
        logger.warning("Breadth data file not found")
        return None
    
    df = pd.read_csv(filepath)
    df["Date"] = pd.to_datetime(df["Date"])
    
    return df


def append_breadth_metrics(date: datetime) -> None:
    """
    Calculate and append breadth metrics for a single date.
    
    Args:
        date: Target date
    """
    # Load consolidated data
    df = load_daily_consolidated(date)
    
    if df is None or df.empty:
        logger.error(f"No consolidated data for {date.date()}")
        return
    
    # Calculate metrics
    metrics = calculate_breadth_metrics(df, date)
    
    if not metrics:
        logger.error(f"Failed to calculate metrics for {date.date()}")
        return
    
    # Load existing breadth data
    df_breadth = load_breadth_data()
    
    if df_breadth is None:
        # Create new DataFrame
        df_breadth = pd.DataFrame([metrics])
    else:
        # Remove existing entry for this date (if any)
        date_str = date.strftime("%Y-%m-%d")
        df_breadth = df_breadth[df_breadth["Date"] != date_str]
        
        # Append new metrics
        df_new = pd.DataFrame([metrics])
        df_breadth = pd.concat([df_breadth, df_new], ignore_index=True)
        
        # Sort by date
        df_breadth["Date"] = pd.to_datetime(df_breadth["Date"])
        df_breadth = df_breadth.sort_values("Date")
        df_breadth["Date"] = df_breadth["Date"].dt.strftime("%Y-%m-%d")
    
    # Ensure correct column order
    df_breadth = df_breadth[BREADTH_COLUMNS]
    
    # Save
    save_breadth_data(df_breadth)
    
    logger.info(f"Appended breadth metrics for {date.date()}")


def get_latest_breadth_date() -> datetime | None:
    """
    Get the latest date in the breadth data.
    
    Returns:
        Latest date as datetime, or None if no data exists
    """
    df = load_breadth_data()
    
    if df is None or df.empty:
        return None
    
    df["Date"] = pd.to_datetime(df["Date"])
    return df["Date"].max()
