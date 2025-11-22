"""Index constituents fetcher for NIFTY MIDSMALLCAP 400."""

from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

from src.core.config import META_DIR, YFINANCE_SUFFIX, MAX_RETRIES, RETRY_DELAY
from src.core.logger import get_logger


logger = get_logger(__name__)


def fetch_index_constituents() -> pd.DataFrame:
    """
    Fetch current constituents of NIFTY MIDSMALLCAP 400.
    
    Returns:
        DataFrame with columns: Symbol (with .NS suffix), Company_Name, Industry
        
    Note:
        Fetches from NSE India website. Falls back to hardcoded list if fails.
    """
    # Try fetching from NSE website
    df = _fetch_from_nse()
    
    if df is not None and not df.empty:
        logger.info(f"Fetched {len(df)} constituents from NSE website")
        return df
    
    # Fallback: try Wikipedia
    logger.warning("NSE fetch failed, trying Wikipedia")
    df = _fetch_from_wikipedia()
    
    if df is not None and not df.empty:
        logger.info(f"Fetched {len(df)} constituents from Wikipedia")
        return df
    
    # If both fail, raise error
    logger.error("Failed to fetch index constituents from all sources")
    raise ValueError("Could not fetch NIFTY MIDSMALLCAP 400 constituents")


def _fetch_from_nse() -> pd.DataFrame | None:
    """
    Fetch constituents from NSE India website.
    
    Returns:
        DataFrame or None if fetch fails
    """
    url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20MIDSMALLCAP%20400"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    for attempt in range(MAX_RETRIES):
        try:
            # First, get the main page to establish session
            session = requests.Session()
            session.get("https://www.nseindia.com", headers=headers, timeout=10)
            time.sleep(1)
            
            # Now fetch the index data
            response = session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract stock data
            if "data" in data:
                stocks = []
                for item in data["data"]:
                    if "symbol" in item:
                        symbol = item["symbol"]
                        # Skip index itself
                        if symbol in ["NIFTY MIDSMALLCAP 400", "NIFTY MID SMALL CAP 400"]:
                            continue
                        
                        stocks.append({
                            "Symbol": f"{symbol}{YFINANCE_SUFFIX}",
                            "Company_Name": item.get("meta", {}).get("companyName", symbol),
                            "Industry": item.get("meta", {}).get("industry", "Unknown"),
                        })
                
                if stocks:
                    df = pd.DataFrame(stocks)
                    return df
            
        except Exception as e:
            logger.warning(f"NSE fetch attempt {attempt + 1} failed: {str(e)}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
    
    return None


def _fetch_from_wikipedia() -> pd.DataFrame | None:
    """
    Fetch constituents from Wikipedia as fallback.
    
    Returns:
        DataFrame or None if fetch fails
    """
    url = "https://en.wikipedia.org/wiki/NIFTY_Midcap_150"  # Similar index
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Find tables with stock data
        tables = pd.read_html(str(soup))
        
        for table in tables:
            # Look for table with Symbol column
            if "Symbol" in table.columns or "Company" in table.columns:
                df = table.copy()
                
                # Standardize columns
                if "Symbol" in df.columns:
                    df = df.rename(columns={"Symbol": "Symbol"})
                    df["Symbol"] = df["Symbol"].apply(lambda x: f"{x}{YFINANCE_SUFFIX}")
                
                if "Company" in df.columns:
                    df = df.rename(columns={"Company": "Company_Name"})
                
                if "Sector" in df.columns:
                    df = df.rename(columns={"Sector": "Industry"})
                elif "Industry" not in df.columns:
                    df["Industry"] = "Unknown"
                
                # Keep only required columns
                df = df[["Symbol", "Company_Name", "Industry"]]
                
                return df
        
    except Exception as e:
        logger.warning(f"Wikipedia fetch failed: {str(e)}")
    
    return None


def save_constituents(df: pd.DataFrame) -> None:
    """
    Save constituents to CSV in data/meta/.
    
    Args:
        df: DataFrame with Symbol, Company_Name, Industry columns
    """
    META_DIR.mkdir(parents=True, exist_ok=True)
    
    filepath = META_DIR / "nifty_midsmallcap400.csv"
    df.to_csv(filepath, index=False)
    
    logger.info(f"Saved {len(df)} constituents to {filepath}")


def load_constituents() -> pd.DataFrame:
    """
    Load constituents from CSV, fetch if not exists.
    
    Returns:
        DataFrame with Symbol, Company_Name, Industry columns
    """
    filepath = META_DIR / "nifty_midsmallcap400.csv"
    
    if filepath.exists():
        logger.info(f"Loading constituents from {filepath}")
        df = pd.read_csv(filepath)
        return df
    
    # Fetch if doesn't exist
    logger.info("Constituents file not found, fetching from source")
    df = fetch_index_constituents()
    save_constituents(df)
    
    return df


def get_symbols_list() -> list[str]:
    """
    Get list of stock symbols (with .NS suffix).
    
    Returns:
        List of symbols
    """
    df = load_constituents()
    return df["Symbol"].tolist()
