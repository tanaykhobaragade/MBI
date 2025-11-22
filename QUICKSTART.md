# 🚀 MBI Quick Reference Card

## Installation (One Time)
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Test installation
python test_installation.py

# 3. Initialize data (takes 30-60 min)
python -m src.main init
```

## Daily Usage
```bash
# Fetch yesterday's data (takes 2-5 min)
python -m src.main daily
```

## Utilities
```bash
# Check if today is trading day
python check_trading_day.py

# Test fetching one stock
python example_fetch.py

# Update missing days
python -m src.main update

# Check status
python -m src.main status
```

## Output Files
- **Main:** `data/processed/market_breadth.csv` (16 metrics per day)
- **Stocks:** `data/raw/stocks/{SYMBOL}.csv` (400 files)
- **Daily:** `data/raw/daily/{YYYY-MM-DD}.csv`

## Key Features
✅ Zero cost (yFinance, no API keys)
✅ Auto-adjusted data (splits/bonuses)
✅ 16 breadth metrics calculated
✅ Timezone-aware (IST/UTC)
✅ Holiday detection (NSE)
✅ GitHub Actions automation

## Breadth Metrics (16)
1. 52WH(%) - % at 52-week high
2. 52WL(%) - % at 52-week low
3. 4.5+(%) - % up >4.5%
4. 4.5-(%) - % down >4.5%
5. 4.5r - Ratio
6-7. 10+/- - vs 10-day SMA
8-9. 20+/- - vs 20-day SMA
10-11. 50+/- - vs 50-day SMA
12-13. 200+/- - vs 200-day SMA
14. 20sma - Count above 20-SMA
15. 50sma - Count above 50-SMA
16. Date

## Automation (GitHub Actions)
- Runs daily at 6 PM IST
- Weekdays only
- Skips holidays automatically
- Manual trigger available

## Documentation
- **README.md** - Overview
- **SETUP.md** - Installation guide
- **COMMANDS.md** - All commands
- **SUMMARY.md** - Implementation details
- **TASK.md** - Specification

## Troubleshooting
```bash
# View logs
cat logs/mbi_*.log

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python version (need 3.12+)
python --version
```

## Configuration
Edit `src/core/config.py`:
- `HISTORICAL_DAYS = 365` - History range
- `SMA_PERIODS = [10, 20, 50, 200]` - SMAs
- `DAILY_CHANGE_THRESHOLD = 4.5` - 4.5+/-
- `MIN_VALID_STOCKS = 350` - Minimum stocks

## Common Issues
❌ **Import errors** → Install dependencies
❌ **No data fetched** → Check trading day
❌ **Rate limits** → Wait a few minutes (auto-retry)
❌ **Weekend run** → Skipped automatically

## Python Usage
```python
from src.fetchers.yfinance_fetcher import fetch_stock_data
from src.processors.breadth_calculator import calculate_breadth_metrics

# Fetch one stock
df = fetch_stock_data("RELIANCE.NS", start, end)

# Calculate metrics
metrics = calculate_breadth_metrics(df, date)
```

## Performance
- **Init:** 30-60 min (400 stocks × 365 days)
- **Daily:** 2-5 min (400 stocks × 1 day)
- **Update:** Depends on missing days
- **Status:** <1 sec

## Support
📖 Read documentation files
🐛 Check logs/ directory
💬 Open GitHub issue
🔧 Modify config.py for customization

---

**Version:** 1.0.0 | **Python:** 3.12+ | **License:** MIT

🎯 **Ready to use!** Start with: `python -m src.main init`
