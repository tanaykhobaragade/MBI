# MBI Setup Guide

This guide will help you set up and run the MBI project.

## Prerequisites

- **Python 3.12 or higher**
- **Git** (for cloning the repository)
- **Internet connection** (for fetching data)

## Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/MBI.git
cd MBI
```

## Step 2: Install Python Dependencies

### Option A: Using UV (Recommended)

UV is a fast Python package manager.

**Install UV:**
```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/Mac
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Install dependencies:**
```bash
uv pip install -r requirements.txt
```

### Option B: Using pip

```bash
pip install -r requirements.txt
```

## Step 3: Verify Installation

Run the test script to ensure everything is set up correctly:

```bash
python test_installation.py
```

You should see all tests passing:
```
✓ Module Imports
✓ Dependencies
✓ Directory Structure
✓ Timezone Handling
✓ Holiday Checker

🎉 All tests passed! (5/5)
```

## Step 4: Initialize Data

### First Time Setup - Fetch Historical Data

This will fetch 365 days of historical data for all 400 stocks (takes ~30-60 minutes):

```bash
python -m src.main init
```

**What happens:**
1. Fetches NIFTY MIDSMALLCAP 400 constituents
2. Downloads 1 year of historical data for each stock
3. Saves data to `data/raw/stocks/`
4. Creates consolidated daily files
5. Calculates breadth metrics

## Step 5: Daily Operations

### Fetch Daily Data

To fetch data for the previous trading day:

```bash
python -m src.main daily
```

**What happens:**
1. Checks if previous day was a trading day
2. Fetches data for all 400 stocks
3. Updates individual stock files
4. Creates consolidated file for the date
5. Calculates and appends breadth metrics

### Incremental Update

To update from the last available date to today:

```bash
python -m src.main update
```

This is useful if you missed a few days and want to catch up.

### Check Status

To see the current state of your data:

```bash
python -m src.main status
```

Shows:
- Number of stock files
- Number of daily files
- Data sizes
- Latest dates

## Step 6: Set Up GitHub Actions (Optional)

For automated daily updates:

1. **Push your repository to GitHub**
   ```bash
   git add .
   git commit -m "Initial setup"
   git push origin main
   ```

2. **Enable GitHub Actions**
   - Go to your repository on GitHub
   - Click on "Actions" tab
   - Enable workflows if prompted

3. **Verify Workflows**
   - Check `.github/workflows/fetch_daily_data.yml`
   - This runs automatically at 6 PM IST every weekday

4. **Manual Trigger (if needed)**
   - Go to Actions tab
   - Select "Fetch Daily Data"
   - Click "Run workflow"

## Directory Structure After Setup

```
MBI/
├── data/
│   ├── raw/
│   │   ├── stocks/              # 400 CSV files (one per stock)
│   │   └── daily/               # Daily consolidated CSVs
│   ├── processed/
│   │   └── market_breadth.csv  # Final output
│   └── meta/
│       ├── nifty_midsmallcap400.csv
│       └── nse_holidays_2024.json
├── logs/
│   └── mbi_YYYYMMDD.log        # Daily logs
└── [other files]
```

## Output Files

### Main Output: `data/processed/market_breadth.csv`

This file contains all 16 breadth metrics for each trading day:

```csv
Date,52WH(%),52WL(%),4.5+(%),4.5-(%),10+(%),10-(%),20+(%),20-(%),50+(%),50-(%),200+(%),200-(%),4.5r,20sma,50sma
2024-11-22,5.25,2.50,15.75,8.50,60.25,39.75,55.50,44.50,48.75,51.25,42.00,58.00,1.85,221,195
```

### Individual Stock Files: `data/raw/stocks/{SYMBOL}.csv`

Each stock has its own CSV:

```csv
Date,Open,High,Low,Close,Volume
2024-11-22,2515.00,2530.00,2505.00,2520.00,5000000
```

## Troubleshooting

### Missing Dependencies

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Import Errors

Make sure you're running commands from the project root directory:

```bash
cd c:\Users\tanay\Documents\WorkSpace\MBI
python -m src.main status
```

### No Data Fetched

1. Check internet connection
2. Verify it's a trading day (not weekend/holiday)
3. Check logs in `logs/` directory

### yFinance Rate Limits

If you hit rate limits:
- Wait a few minutes
- The script has automatic retry logic with exponential backoff

### GitHub Actions Not Running

1. Check if workflows are enabled in repository settings
2. Verify the YAML files are in `.github/workflows/`
3. Check Actions tab for error logs

## Configuration

Edit `src/core/config.py` to customize:

```python
# Historical data range
HISTORICAL_DAYS = 365  # Change to fetch more/less history

# SMA periods
SMA_PERIODS = [10, 20, 50, 200]

# Daily change threshold
DAILY_CHANGE_THRESHOLD = 4.5  # for 4.5+/- metrics

# Minimum valid stocks
MIN_VALID_STOCKS = 350  # out of 400
```

## Usage Examples

### Example 1: Fresh Start

```bash
# Clone repo
git clone https://github.com/yourusername/MBI.git
cd MBI

# Install dependencies
pip install -r requirements.txt

# Test installation
python test_installation.py

# Initialize data
python -m src.main init

# Check status
python -m src.main status
```

### Example 2: Daily Update (Manual)

```bash
# Fetch daily data
python -m src.main daily

# Or update incrementally
python -m src.main update
```

### Example 3: Check Last 5 Days

```bash
# View the processed data
cat data/processed/market_breadth.csv | tail -n 5
```

## Next Steps

1. **Set up visualization**: Create charts from `market_breadth.csv`
2. **Google Sheets integration**: Import CSV to Google Sheets
3. **GitHub Pages dashboard**: Create HTML dashboard
4. **Alerts**: Set up notifications for specific conditions

## Support

- Check `TASK.md` for detailed technical documentation
- Review `README.md` for project overview
- Check logs in `logs/` directory for debugging
- Open an issue on GitHub for help

## Important Notes

- **Trading Days Only**: System automatically skips weekends and holidays
- **IST Timezone**: All dates are in Indian Standard Time
- **Auto-Adjusted Data**: yFinance provides split/bonus adjusted data
- **Incremental Updates**: Only fetches new data, not entire history each time
- **Data Validation**: Checks data quality before processing

---

**Ready to go!** Start with `python -m src.main init` to fetch your first batch of data.
