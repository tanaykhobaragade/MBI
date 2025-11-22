"""Test script to verify MBI installation and basic functionality."""

from __future__ import annotations

import sys

from src.core.logger import print_header, print_success, print_error, print_info, print_separator


def test_imports() -> bool:
    """Test if all required modules can be imported."""
    print_info("Testing module imports...")
    
    try:
        # Core modules
        from src.core import config, timezone_handler, logger
        print_success("✓ Core modules imported")
        
        # Fetchers
        from src.fetchers import yfinance_fetcher, index_fetcher
        print_success("✓ Fetcher modules imported")
        
        # Processors
        from src.processors import data_validator, date_consolidator, breadth_calculator
        print_success("✓ Processor modules imported")
        
        # Utils
        from src.utils import holiday_checker, file_manager, corporate_actions
        print_success("✓ Utility modules imported")
        
        return True
    
    except ImportError as e:
        print_error(f"✗ Import failed: {str(e)}")
        return False


def test_dependencies() -> bool:
    """Test if all required dependencies are installed."""
    print_info("Testing dependencies...")
    
    dependencies = [
        ("yfinance", "yfinance"),
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("pytz", "pytz"),
        ("holidays", "holidays"),
        ("requests", "requests"),
        ("bs4", "beautifulsoup4"),
        ("lxml", "lxml"),
        ("pydantic", "pydantic"),
        ("rich", "rich"),
    ]
    
    all_installed = True
    
    for module_name, package_name in dependencies:
        try:
            __import__(module_name)
            print_success(f"✓ {package_name} installed")
        except ImportError:
            print_error(f"✗ {package_name} NOT installed")
            all_installed = False
    
    return all_installed


def test_directories() -> bool:
    """Test if all required directories exist."""
    print_info("Testing directory structure...")
    
    from src.core.config import RAW_STOCKS_DIR, RAW_DAILY_DIR, PROCESSED_DIR, META_DIR, PROJECT_ROOT
    
    directories = [
        ("Raw stocks", RAW_STOCKS_DIR),
        ("Raw daily", RAW_DAILY_DIR),
        ("Processed", PROCESSED_DIR),
        ("Meta", META_DIR),
        ("Logs", PROJECT_ROOT / "logs"),
    ]
    
    all_exist = True
    
    for name, path in directories:
        if path.exists():
            print_success(f"✓ {name} directory exists: {path}")
        else:
            print_error(f"✗ {name} directory missing: {path}")
            all_exist = False
    
    return all_exist


def test_timezone() -> bool:
    """Test timezone handling."""
    print_info("Testing timezone handling...")
    
    try:
        from src.core.timezone_handler import get_current_ist_time, convert_ist_to_utc, convert_utc_to_ist
        
        ist_time = get_current_ist_time()
        print_success(f"✓ Current IST time: {ist_time}")
        
        utc_time = convert_ist_to_utc(ist_time)
        print_success(f"✓ Converted to UTC: {utc_time}")
        
        back_to_ist = convert_utc_to_ist(utc_time)
        print_success(f"✓ Converted back to IST: {back_to_ist}")
        
        return True
    
    except Exception as e:
        print_error(f"✗ Timezone test failed: {str(e)}")
        return False


def test_holiday_checker() -> bool:
    """Test holiday checking."""
    print_info("Testing holiday checker...")
    
    try:
        from src.utils.holiday_checker import is_trading_day, get_nse_holidays
        from src.core.timezone_handler import get_current_ist_time
        
        current = get_current_ist_time()
        is_trading = is_trading_day(current)
        print_success(f"✓ Today ({current.date()}) is {'a trading day' if is_trading else 'NOT a trading day'}")
        
        holidays = get_nse_holidays(current.year)
        print_success(f"✓ Found {len(holidays)} holidays for {current.year}")
        
        return True
    
    except Exception as e:
        print_error(f"✗ Holiday checker test failed: {str(e)}")
        return False


def run_all_tests() -> None:
    """Run all tests."""
    print_header("MBI Installation Test")
    
    tests = [
        ("Module Imports", test_imports),
        ("Dependencies", test_dependencies),
        ("Directory Structure", test_directories),
        ("Timezone Handling", test_timezone),
        ("Holiday Checker", test_holiday_checker),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print_separator()
        print_header(test_name)
        result = test_func()
        results.append((test_name, result))
        print("")
    
    # Summary
    print_separator()
    print_header("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        if result:
            print_success(f"✓ {test_name}")
        else:
            print_error(f"✗ {test_name}")
    
    print_separator()
    
    if passed == total:
        print_success(f"\n🎉 All tests passed! ({passed}/{total})")
        print_info("\nYou can now run:")
        print_info("  python -m src.main init      # Initialize historical data")
        print_info("  python -m src.main daily     # Fetch daily data")
        print_info("  python -m src.main update    # Incremental update")
        print_info("  python -m src.main status    # Check status")
        sys.exit(0)
    else:
        print_error(f"\n❌ Some tests failed ({passed}/{total} passed)")
        print_info("\nPlease fix the issues above before running the main program.")
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
