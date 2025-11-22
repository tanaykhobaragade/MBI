"""Corporate actions tracking and logging."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd

from src.core.config import META_DIR, IST
from src.core.logger import get_logger


logger = get_logger(__name__)


def check_corporate_actions(symbol: str, df: pd.DataFrame) -> list[dict]:
    """
    Check for potential corporate actions (splits, bonuses) in stock data.
    
    Args:
        symbol: Stock symbol
        df: Stock data DataFrame
        
    Returns:
        List of detected corporate actions
        
    Note:
        yFinance auto-adjusts data, so this detects significant price jumps
        that might indicate data issues or unadjusted events.
    """
    actions = []
    
    if len(df) < 2:
        return actions
    
    # Sort by date
    df = df.sort_values("Date")
    
    # Calculate daily price change percentage
    df["Price_Change"] = df["Close"].pct_change() * 100
    
    # Look for large price jumps (>20% in one day)
    # This shouldn't happen with adjusted data, but good to check
    large_changes = df[abs(df["Price_Change"]) > 20]
    
    for idx, row in large_changes.iterrows():
        action = {
            "symbol": symbol,
            "date": row["Date"].strftime("%Y-%m-%d"),
            "type": "potential_split_or_bonus",
            "price_change_pct": round(row["Price_Change"], 2),
            "close_price": row["Close"],
            "detected_at": datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S"),
        }
        actions.append(action)
        
        logger.warning(
            f"Potential corporate action detected for {symbol} on {row['Date'].date()}: "
            f"{row['Price_Change']:.2f}% price change"
        )
    
    return actions


def log_corporate_action(action: dict) -> None:
    """
    Log a corporate action to file.
    
    Args:
        action: Dictionary with action details
    """
    META_DIR.mkdir(parents=True, exist_ok=True)
    
    filepath = META_DIR / "corporate_actions.json"
    
    # Load existing actions
    if filepath.exists():
        with open(filepath, "r") as f:
            actions = json.load(f)
    else:
        actions = []
    
    # Add new action
    actions.append(action)
    
    # Save
    with open(filepath, "w") as f:
        json.dump(actions, f, indent=2)
    
    logger.info(f"Logged corporate action: {action}")


def get_recent_actions(days: int = 30) -> list[dict]:
    """
    Get corporate actions from the last N days.
    
    Args:
        days: Number of days to look back
        
    Returns:
        List of recent corporate actions
    """
    filepath = META_DIR / "corporate_actions.json"
    
    if not filepath.exists():
        return []
    
    with open(filepath, "r") as f:
        actions = json.load(f)
    
    # Filter by date
    cutoff = datetime.now(IST) - pd.Timedelta(days=days)
    
    recent = []
    for action in actions:
        action_date = datetime.strptime(action["date"], "%Y-%m-%d").replace(tzinfo=IST)
        if action_date >= cutoff:
            recent.append(action)
    
    return recent


def check_volume_anomaly(df: pd.DataFrame, threshold: float = 5.0) -> list[dict]:
    """
    Check for volume anomalies (unusually high volume).
    
    Args:
        df: Stock data DataFrame
        threshold: Multiple of average volume to consider anomaly
        
    Returns:
        List of detected volume anomalies
    """
    anomalies = []
    
    if len(df) < 20:  # Need enough data for average
        return anomalies
    
    # Calculate rolling average volume (20 days)
    df = df.sort_values("Date")
    df["Avg_Volume"] = df["Volume"].rolling(window=20, min_periods=1).mean()
    df["Volume_Ratio"] = df["Volume"] / df["Avg_Volume"]
    
    # Find anomalies
    high_volume = df[df["Volume_Ratio"] > threshold]
    
    for idx, row in high_volume.iterrows():
        anomaly = {
            "date": row["Date"].strftime("%Y-%m-%d"),
            "volume": int(row["Volume"]),
            "avg_volume": int(row["Avg_Volume"]),
            "ratio": round(row["Volume_Ratio"], 2),
        }
        anomalies.append(anomaly)
    
    return anomalies


def generate_data_quality_report(symbols: list[str]) -> dict:
    """
    Generate a data quality report for all symbols.
    
    Args:
        symbols: List of stock symbols
        
    Returns:
        Dictionary with quality metrics
    """
    from src.fetchers.yfinance_fetcher import load_stock_data
    
    report = {
        "total_symbols": len(symbols),
        "symbols_with_data": 0,
        "symbols_without_data": 0,
        "corporate_actions": 0,
        "data_issues": [],
    }
    
    for symbol in symbols:
        df = load_stock_data(symbol)
        
        if df is None or df.empty:
            report["symbols_without_data"] += 1
            report["data_issues"].append({
                "symbol": symbol,
                "issue": "No data available"
            })
        else:
            report["symbols_with_data"] += 1
            
            # Check for corporate actions
            actions = check_corporate_actions(symbol, df)
            report["corporate_actions"] += len(actions)
            
            if actions:
                for action in actions:
                    report["data_issues"].append({
                        "symbol": symbol,
                        "issue": f"Corporate action detected on {action['date']}"
                    })
    
    logger.info(f"Data quality report: {report['symbols_with_data']}/{report['total_symbols']} symbols have data")
    
    return report
