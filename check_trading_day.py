"""
Check if today is a trading day

Quick utility to check if NSE is open today.
"""

from src.core.timezone_handler import get_current_ist_time
from src.core.logger import print_header, print_success, print_error, print_info
from src.utils.holiday_checker import (
    is_trading_day,
    get_previous_trading_day,
    get_next_trading_day,
    get_nse_holidays,
)


def check_trading_day():
    """Check if today is a trading day."""
    
    print_header("NSE Trading Day Check")
    
    # Get current time in IST
    current = get_current_ist_time()
    
    print_info(f"Current Date: {current.strftime('%A, %B %d, %Y')}")
    print_info(f"Current Time: {current.strftime('%I:%M %p IST')}")
    print("")
    
    # Check if trading day
    if is_trading_day(current):
        print_success("✓ Today IS a trading day")
        
        # Check market hours
        from src.core.timezone_handler import is_market_hours
        if is_market_hours(current):
            print_info("  Market is currently OPEN (9:15 AM - 3:30 PM IST)")
        else:
            if current.hour < 9 or (current.hour == 9 and current.minute < 15):
                print_info("  Market has NOT opened yet")
            else:
                print_info("  Market has CLOSED for the day")
    else:
        print_error("✗ Today is NOT a trading day")
        
        # Check why
        if current.weekday() >= 5:
            day_name = current.strftime('%A')
            print_info(f"  Reason: Weekend ({day_name})")
        else:
            print_info("  Reason: NSE Holiday")
    
    print("")
    
    # Previous trading day
    prev_trading = get_previous_trading_day(current)
    print_info(f"Previous Trading Day: {prev_trading.strftime('%A, %B %d, %Y')}")
    
    # Next trading day
    next_trading = get_next_trading_day(current)
    print_info(f"Next Trading Day: {next_trading.strftime('%A, %B %d, %Y')}")
    
    print("")
    
    # Show holidays for current year
    year = current.year
    holidays = get_nse_holidays(year)
    
    print_info(f"NSE Holidays in {year}: {len(holidays)}")
    
    # Show upcoming holidays (next 3)
    upcoming = [h for h in holidays if h > current][:3]
    if upcoming:
        print_info("Upcoming holidays:")
        for holiday in upcoming:
            print(f"  - {holiday.strftime('%A, %B %d, %Y')}")
    else:
        print_info("No upcoming holidays this year")


if __name__ == "__main__":
    check_trading_day()
