# MBI Command Reference

Quick reference for all MBI commands.

## Installation & Testing

### Test Installation
```bash
python test_installation.py
```
Verifies all dependencies and modules are properly installed.

## Main Commands

### Initialize Historical Data
```bash
python -m src.main init
```
**What it does:**
- Fetches 365 days of historical data
- Downloads data for all 400 stocks
- Creates consolidated files
- Calculates breadth metrics

**When to use:**
- First time setup
- After deleting data directory
- To rebuild entire dataset

**Time:** ~30-60 minutes

---

### Fetch Daily Data
```bash
python -m src.main daily
```
**What it does:**
- Fetches data for previous trading day
- Updates all stock files
- Creates daily consolidated file
- Calculates breadth metrics

**When to use:**
- Daily updates (manual)
- After market close (6 PM IST or later)

**Time:** ~2-5 minutes

---

### Incremental Update
```bash
python -m src.main update
```
**What it does:**
- Finds the last available date
- Fetches all missing dates up to today
- Updates consolidated files
- Recalculates metrics

**When to use:**
- After missing several days
- To catch up on data
- After errors/interruptions

**Time:** Depends on missing days

---

### Show Status
```bash
python -m src.main status
```
**What it does:**
- Shows number of stock files
- Shows number of daily files
- Displays data sizes
- Shows latest dates

**When to use:**
- Check data health
- Verify updates
- Quick overview

**Time:** <1 second

## Python Module Usage

You can also import and use modules directly:

### Import Example
```python
from src.fetchers.index_fetcher import get_symbols_list
from src.fetchers.yfinance_fetcher import fetch_stock_data
from src.processors.breadth_calculator import calculate_breadth_metrics

# Get list of symbols
symbols = get_symbols_list()
print(f"Found {len(symbols)} symbols")

# Fetch data for one stock
from datetime import datetime, timedelta
end = datetime.now()
start = end - timedelta(days=30)
df = fetch_stock_data("RELIANCE.NS", start, end)
```

## GitHub Actions (Automated)

### Daily Automation
Runs automatically at 6 PM IST (12:30 PM UTC) every weekday.

**Manual trigger:**
1. Go to GitHub Actions tab
2. Select "Fetch Daily Data"
3. Click "Run workflow"

### Historical Initialization
Manual trigger only.

**Steps:**
1. Go to GitHub Actions tab
2. Select "Initialize Historical Data"
3. Set `days_back` (default: 365)
4. Click "Run workflow"

## Common Workflows

### First Time Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Test installation
python test_installation.py

# 3. Initialize data
python -m src.main init

# 4. Check status
python -m src.main status
```

### Daily Routine (Manual)
```bash
# After market close (6 PM IST)
python -m src.main daily
```

### Weekly Check
```bash
# Update any missing days
python -m src.main update

# Verify status
python -m src.main status
```

### After Data Issues
```bash
# Re-initialize if needed
python -m src.main init

# Or update incrementally
python -m src.main update
```

## Advanced Usage

### Custom Date Range
Modify `src/core/config.py`:
```python
HISTORICAL_DAYS = 730  # 2 years instead of 1
```
Then run `python -m src.main init`

### Change SMA Periods
Modify `src/core/config.py`:
```python
SMA_PERIODS = [10, 20, 50, 100, 200]  # Add 100-day SMA
```

### Adjust Thresholds
Modify `src/core/config.py`:
```python
DAILY_CHANGE_THRESHOLD = 5.0  # Change from 4.5% to 5%
MIN_VALID_STOCKS = 300  # Require only 300 stocks instead of 350
```

## Output Files

### Primary Output
```
data/processed/market_breadth.csv
```
Contains all 16 metrics for each trading day.

### Individual Stocks
```
data/raw/stocks/{SYMBOL}.csv
```
Historical data for each stock.

### Daily Consolidated
```
data/raw/daily/{YYYY-MM-DD}.csv
```
All stocks for a specific date with SMAs.

### Metadata
```
data/meta/nifty_midsmallcap400.csv
data/meta/nse_holidays_2024.json
data/meta/corporate_actions.json
```

### Logs
```
logs/mbi_YYYYMMDD.log
```
Daily log files.

## Exit Codes

- `0` - Success
- `1` - Error (check logs)

## Environment Variables

None required. Configuration is in `src/core/config.py`.

## Logging

Logs are written to:
- Console (with colors via Rich)
- File: `logs/mbi_YYYYMMDD.log`

**Log levels:**
- INFO: Normal operations
- WARNING: Non-critical issues
- ERROR: Critical failures
- DEBUG: Detailed information (set in code)

## Performance Tips

1. **Initial fetch is slow**: First `init` takes time, be patient
2. **Daily updates are fast**: Only fetches new data
3. **Parallel processing**: Not currently implemented, but fetches are sequential
4. **Rate limits**: yFinance has rate limits, retries are automatic

## Troubleshooting Commands

### Check Python Version
```bash
python --version
# Should be 3.12 or higher
```

### Check Dependencies
```bash
pip list | grep -E "yfinance|pandas|numpy|rich"
```

### View Logs
```bash
# Windows PowerShell
Get-Content logs/mbi_*.log | Select-Object -Last 50

# Linux/Mac
tail -f logs/mbi_*.log
```

### Check Data Files
```bash
# Windows PowerShell
Get-ChildItem data/raw/stocks | Measure-Object

# Linux/Mac
ls -l data/raw/stocks | wc -l
```

## Quick Reference

| Command | Purpose | Time | Frequency |
|---------|---------|------|-----------|
| `init` | Initialize all data | 30-60 min | Once |
| `daily` | Fetch daily update | 2-5 min | Daily |
| `update` | Incremental update | Varies | As needed |
| `status` | Show data status | <1 sec | Anytime |

## Getting Help

```bash
# Show help
python -m src.main

# View logs
cat logs/mbi_*.log

# Check TASK.md for implementation details
# Check README.md for project overview
# Check SETUP.md for setup instructions
```

---

**Pro Tip**: Set up a cron job or Task Scheduler to run `python -m src.main daily` automatically every evening!
