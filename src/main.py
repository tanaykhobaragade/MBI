"""Main entry point for MBI data pipeline."""

from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path

from src.core.config import HISTORICAL_DAYS, MIN_VALID_STOCKS
from src.core.logger import (
    get_logger,
    print_header,
    print_success,
    print_error,
    print_info,
    print_separator,
)
from src.core.timezone_handler import get_current_ist_time, format_date_for_filename
from src.fetchers.index_fetcher import load_constituents, get_symbols_list
from src.fetchers.yfinance_fetcher import (
    fetch_stock_data,
    append_stock_data,
    get_latest_date_for_symbol,
)
from src.processors.date_consolidator import (
    create_daily_consolidated_file,
    get_latest_consolidated_date,
)
from src.processors.breadth_calculator import append_breadth_metrics, get_latest_breadth_date
from src.processors.data_validator import validate_consolidated_data
from src.utils.file_manager import ensure_directories
from src.utils.holiday_checker import is_trading_day, get_previous_trading_day


logger = get_logger(__name__)


def initialize_historical_data(days_back: int = HISTORICAL_DAYS) -> None:
    """
    Initialize historical data for all stocks.
    
    Args:
        days_back: Number of days of historical data to fetch
    """
    print_header("Initializing Historical Data")
    
    # Ensure directories exist
    ensure_directories()
    
    # Load index constituents
    print_info("Loading index constituents...")
    symbols = get_symbols_list()
    print_success(f"Loaded {len(symbols)} symbols")
    
    # Calculate date range
    end_date = get_current_ist_time()
    start_date = end_date - timedelta(days=days_back)
    
    print_info(f"Fetching data from {start_date.date()} to {end_date.date()}")
    print_separator()
    
    # Fetch data for each symbol
    success_count = 0
    failed_symbols = []
    
    for i, symbol in enumerate(symbols, 1):
        print_info(f"[{i}/{len(symbols)}] Fetching {symbol}...")
        
        try:
            df = fetch_stock_data(symbol, start_date, end_date)
            
            if df is not None and not df.empty:
                append_stock_data(symbol, df)
                success_count += 1
                print_success(f"✓ {symbol}: {len(df)} rows fetched")
            else:
                failed_symbols.append(symbol)
                print_error(f"✗ {symbol}: No data received")
        
        except Exception as e:
            failed_symbols.append(symbol)
            print_error(f"✗ {symbol}: {str(e)}")
            logger.error(f"Failed to fetch {symbol}: {str(e)}")
    
    print_separator()
    print_success(f"Historical data initialized: {success_count}/{len(symbols)} symbols")
    
    if failed_symbols:
        print_error(f"Failed symbols ({len(failed_symbols)}): {', '.join(failed_symbols[:10])}")
        if len(failed_symbols) > 10:
            print_info(f"... and {len(failed_symbols) - 10} more")
    
    # Now process all the data to create consolidated files and breadth metrics
    print_separator()
    print_header("Processing Historical Data")
    print_info("Creating consolidated files and calculating breadth metrics...")
    
    # Get all unique dates from stock files
    from src.utils.holiday_checker import get_trading_days_in_range
    trading_days = get_trading_days_in_range(start_date, end_date)
    
    processed_count = 0
    failed_count = 0
    
    for i, date in enumerate(trading_days, 1):
        try:
            print_info(f"[{i}/{len(trading_days)}] Processing {date.date()}...")
            
            # Create consolidated file
            create_daily_consolidated_file(date, symbols)
            
            # Calculate breadth metrics
            append_breadth_metrics(date)
            
            processed_count += 1
            
            if i % 10 == 0:  # Progress update every 10 days
                print_info(f"Progress: {i}/{len(trading_days)} days processed")
        
        except Exception as e:
            failed_count += 1
            logger.error(f"Failed to process {date.date()}: {str(e)}")
            if failed_count <= 5:  # Only show first 5 errors
                print_error(f"✗ {date.date()}: {str(e)}")
    
    print_separator()
    print_success(f"Processing complete: {processed_count}/{len(trading_days)} days processed")
    
    if failed_count > 0:
        print_error(f"Failed to process {failed_count} days (check logs for details)")


def fetch_daily_data(target_date: datetime | None = None) -> None:
    """
    Fetch daily data for all stocks and calculate breadth metrics.
    
    Args:
        target_date: Date to fetch data for (default: previous trading day)
    """
    print_header("Fetching Daily Data")
    
    # Ensure directories exist
    ensure_directories()
    
    # Determine target date
    if target_date is None:
        target_date = get_previous_trading_day()
    
    print_info(f"Target date: {target_date.date()}")
    
    # Check if it's a trading day
    if not is_trading_day(target_date):
        print_error(f"{target_date.date()} is not a trading day")
        return
    
    # Load symbols
    symbols = get_symbols_list()
    print_info(f"Fetching data for {len(symbols)} symbols")
    print_separator()
    
    # Fetch data for each symbol
    success_count = 0
    failed_symbols = []
    
    # Fetch data for a 3-day window around target date
    start_date = target_date - timedelta(days=1)
    end_date = target_date + timedelta(days=1)
    
    for i, symbol in enumerate(symbols, 1):
        try:
            df = fetch_stock_data(symbol, start_date, end_date)
            
            if df is not None and not df.empty:
                append_stock_data(symbol, df)
                success_count += 1
                
                if i % 50 == 0:  # Progress update every 50 symbols
                    print_info(f"Progress: {i}/{len(symbols)} symbols processed")
            else:
                failed_symbols.append(symbol)
        
        except Exception as e:
            failed_symbols.append(symbol)
            logger.error(f"Failed to fetch {symbol}: {str(e)}")
    
    print_separator()
    print_success(f"Daily data fetched: {success_count}/{len(symbols)} symbols")
    
    if failed_symbols:
        print_error(f"Failed symbols ({len(failed_symbols)}): {', '.join(failed_symbols[:10])}")
    
    # Check if we have enough data
    if success_count < MIN_VALID_STOCKS:
        print_error(f"Insufficient data: {success_count}/{MIN_VALID_STOCKS} minimum required")
        return
    
    # Create consolidated file
    print_info("Creating consolidated daily file...")
    try:
        create_daily_consolidated_file(target_date, symbols)
        print_success("Consolidated file created")
    except Exception as e:
        print_error(f"Failed to create consolidated file: {str(e)}")
        logger.error(f"Consolidation error: {str(e)}")
        return
    
    # Calculate breadth metrics
    print_info("Calculating breadth metrics...")
    try:
        append_breadth_metrics(target_date)
        print_success("Breadth metrics calculated and saved")
    except Exception as e:
        print_error(f"Failed to calculate breadth metrics: {str(e)}")
        logger.error(f"Breadth calculation error: {str(e)}")


def update_incremental() -> None:
    """
    Update data incrementally from last available date to today.
    """
    print_header("Incremental Update")
    
    # Get latest date in breadth data
    latest_date = get_latest_breadth_date()
    
    if latest_date is None:
        print_info("No existing data found, running full historical initialization")
        initialize_historical_data()
        return
    
    print_info(f"Latest data available: {latest_date.date()}")
    
    # Get current date
    current_date = get_current_ist_time()
    
    # Get previous trading day
    target_date = get_previous_trading_day(current_date)
    
    print_info(f"Target date: {target_date.date()}")
    
    # If we already have data for target date, nothing to do
    if latest_date.date() >= target_date.date():
        print_success("Data is already up to date!")
        return
    
    # Fetch missing dates
    date = latest_date + timedelta(days=1)
    
    while date <= target_date:
        if is_trading_day(date):
            print_separator()
            print_info(f"Processing {date.date()}...")
            fetch_daily_data(date)
        
        date = date + timedelta(days=1)
    
    print_separator()
    print_success("Incremental update complete!")


def show_status() -> None:
    """
    Show current status of data.
    """
    print_header("MBI Data Status")
    
    from src.utils.file_manager import count_files, get_directory_size_human
    from src.core.config import RAW_STOCKS_DIR, RAW_DAILY_DIR, PROCESSED_DIR
    
    # Count files
    stock_files = count_files(RAW_STOCKS_DIR, "*.csv")
    daily_files = count_files(RAW_DAILY_DIR, "*.csv")
    
    print_info(f"Individual stock files: {stock_files}")
    print_info(f"Daily consolidated files: {daily_files}")
    
    # Get sizes
    stocks_size = get_directory_size_human(RAW_STOCKS_DIR)
    daily_size = get_directory_size_human(RAW_DAILY_DIR)
    processed_size = get_directory_size_human(PROCESSED_DIR)
    
    print_info(f"Stock data size: {stocks_size}")
    print_info(f"Daily data size: {daily_size}")
    print_info(f"Processed data size: {processed_size}")
    
    # Latest dates
    latest_consolidated = get_latest_consolidated_date()
    latest_breadth = get_latest_breadth_date()
    
    if latest_consolidated:
        print_info(f"Latest consolidated date: {latest_consolidated.date()}")
    
    if latest_breadth:
        print_info(f"Latest breadth data: {latest_breadth.date()}")
    
    print_separator()


def main() -> None:
    """
    Main CLI entry point.
    """
    if len(sys.argv) < 2:
        print("Usage: python -m src.main <command>")
        print("\nCommands:")
        print("  init              - Initialize historical data")
        print("  daily             - Fetch daily data for previous trading day")
        print("  update            - Incremental update from last date")
        print("  status            - Show data status")
        print("\nExamples:")
        print("  python -m src.main init")
        print("  python -m src.main daily")
        print("  python -m src.main update")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    try:
        if command == "init":
            initialize_historical_data()
        elif command == "daily":
            fetch_daily_data()
        elif command == "update":
            update_incremental()
        elif command == "status":
            show_status()
        else:
            print_error(f"Unknown command: {command}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print_error("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error: {str(e)}")
        logger.exception("Unhandled exception")
        sys.exit(1)


if __name__ == "__main__":
    main()
