"""
Example script: Fetch data for a single stock

This script demonstrates how to fetch and display data for one stock.
Use this to test the fetching functionality before running full updates.
"""

from datetime import datetime, timedelta

from src.core.timezone_handler import get_current_ist_time
from src.core.logger import print_header, print_success, print_info, print_error
from src.fetchers.yfinance_fetcher import fetch_stock_data


def fetch_single_stock_example():
    """Fetch and display data for a single stock."""
    
    print_header("Single Stock Fetch Example")
    
    # Stock to fetch
    symbol = "RELIANCE.NS"
    
    # Date range (last 30 days)
    end_date = get_current_ist_time()
    start_date = end_date - timedelta(days=30)
    
    print_info(f"Fetching {symbol}")
    print_info(f"From: {start_date.date()}")
    print_info(f"To: {end_date.date()}")
    print("")
    
    # Fetch data
    try:
        df = fetch_stock_data(symbol, start_date, end_date)
        
        if df is not None and not df.empty:
            print_success(f"✓ Successfully fetched {len(df)} rows")
            print("")
            
            # Display first few rows
            print_info("First 5 rows:")
            print(df.head())
            print("")
            
            # Display last few rows
            print_info("Last 5 rows:")
            print(df.tail())
            print("")
            
            # Display statistics
            print_info("Statistics:")
            print(f"  Highest Close: ₹{df['Close'].max():.2f}")
            print(f"  Lowest Close: ₹{df['Close'].min():.2f}")
            print(f"  Average Volume: {df['Volume'].mean():.0f}")
            print(f"  Latest Close: ₹{df.iloc[-1]['Close']:.2f}")
            print(f"  Latest Date: {df.iloc[-1]['Date'].date()}")
            
            print("")
            print_success("✓ Fetch successful!")
            
        else:
            print_error("✗ No data received")
    
    except Exception as e:
        print_error(f"✗ Error: {str(e)}")


if __name__ == "__main__":
    fetch_single_stock_example()
