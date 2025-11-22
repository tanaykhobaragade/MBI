# MBI - Market Breadth Indicator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/uv-package%20manager-purple)](https://github.com/astral-sh/uv)
[![yfinance](https://img.shields.io/badge/Data-yFinance-orange)](https://github.com/ranaroussi/yfinance)

**Automated Market Breadth Indicator (MBI) for NIFTY MIDSMALLCAP 400** - Daily NSE stock data processing and breadth analysis for swing trading decisions.

🔗 **Live Dashboard**: [https://tanaykhobaragade.github.io/MBI/](https://tanaykhobaragade.github.io/MBI/)

---

## 📊 Overview

This project automates the calculation of market breadth metrics for the **NIFTY MIDSMALLCAP 400 index** (400 stocks). It fetches daily OHLCV data via **yFinance**, calculates 16 breadth indicators, and outputs results accessible from any device via **GitHub Pages** or direct CSV import.

### ✨ Key Features

- ✅ **Fully Automated**: GitHub Actions runs daily at 6 PM IST
- ✅ **Zero Cost**: No API charges, runs on GitHub's free tier  
- ✅ **Modern Stack**: Python 3.12+ with UV package manager
- ✅ **Auto-Adjusted Data**: Stock splits & bonuses handled automatically
- ✅ **Device Agnostic**: Access via web dashboard, Excel, or Google Sheets
- ✅ **Timezone-Safe**: Proper IST/UTC handling throughout
- ✅ **Historical Data**: Maintains 1+ year of breadth history

---

## 📈 Metrics Calculated

| Metric | Description |
|--------|-------------|
| **Date** | Trading date (IST) |
| **52WH(%)** | % of stocks hitting new 52-week high |
| **52WL(%)** | % of stocks hitting new 52-week low |
| **4.5+(%)** | % of stocks up by 4.5%+ today |
| **4.5-(%)** | % of stocks down by 4.5%+ today |
| **10+(%)** | % of stocks above 10-day SMA |
| **10-(%)** | % of stocks below 10-day SMA |
| **20+(%)** | % of stocks above 20-day SMA |
| **20-(%)** | % of stocks below 20-day SMA |
| **50+(%)** | % of stocks above 50-day SMA |
| **50-(%)** | % of stocks below 50-day SMA |
| **200+(%)** | % of stocks above 200-day SMA |
| **200-(%)** | % of stocks below 200-day SMA |
| **4.5r** | Momentum Ratio: `[4.5+(%) / 4.5-(%)] × 100` |
| **20sma** | Trend Ratio: `[20+(%) / 20-(%)] × 100` |
| **50sma** | Trend Ratio: `[50+(%) / 50-(%)] × 100` |

---

## 🏗️ Project Structure

```
MBI/
├── .github/workflows/
│   ├── fetch_daily_data.yml           # Daily 6 PM IST automation
│   └── initialize_historical.yml      # One-time historical data fetch
├── data/
│   ├── raw/
│   │   ├── stocks/                    # Individual stock CSVs (400 files)
│   │   └── daily/                     # Date-wise consolidated data
│   ├── processed/
│   │   └── market_breadth.csv         # Final MBI output
│   └── meta/
│       ├── nifty_midsmallcap400.csv   # Index constituents
│       └── nse_holidays_YYYY.json     # Holiday calendars
├── src/
│   ├── core/                          # Config, timezone, logging
│   ├── fetchers/                      # yFinance data fetching
│   ├── processors/                    # Data validation & MBI calculation
│   └── utils/                         # Holidays, file ops, helpers
├── docs/                              # GitHub Pages dashboard
│   ├── index.html
│   └── assets/
├── pyproject.toml                     # UV project configuration
├── .python-version                    # Python 3.12
└── README.md
```

---

## 🚀 Quick Start

### Access Data (No Installation Required)

#### 📊 **Option 1: Live Dashboard**
Visit: **[https://tanaykhobaragade.github.io/MBI/](https://tanaykhobaragade.github.io/MBI/)**

#### 📑 **Option 2: Google Sheets Import**
```
=IMPORTDATA("https://raw.githubusercontent.com/tanaykhobaragade/MBI/main/data/processed/market_breadth.csv")
```

#### 📊 **Option 3: Excel Import**
1. **Data** → **Get Data** → **From Web**
2. Enter URL: `https://raw.githubusercontent.com/tanaykhobaragade/MBI/main/data/processed/market_breadth.csv`
3. Click **Load**

---

## 💻 Local Development

### Prerequisites
- **Python 3.12+**
- **UV package manager** (recommended) or pip
- **Git**

### Installation with UV

```bash
# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone repository
git clone https://github.com/tanaykhobaragade/MBI.git
cd MBI

# Create virtual environment and install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows
```

### Installation with pip (alternative)

```bash
git clone https://github.com/tanaykhobaragade/MBI.git
cd MBI

python -m venv .venv
source .venv/bin/activate

pip install -e .
```

### Running Locally

```bash
# Fetch today's data
python src/main.py fetch-daily

# Initialize historical data (one-time)
python src/main.py init-historical --days 365

# Calculate breadth for a specific date
python src/main.py calculate-breadth --date 2024-11-22

# Run tests
uv run pytest
```

---

## 🔄 Automation Workflow

### Daily Update Process (6 PM IST)

```
GitHub Actions Trigger (Mon-Fri)
         ↓
   Check: Is Trading Day?
     (Skip weekends/holidays)
         ↓  Yes
   Convert IST → UTC
         ↓
   Fetch EOD Data (yFinance)
     • 400 stocks
     • Auto-adjusted for splits
         ↓
   Save to data/raw/stocks/
         ↓
   Consolidate → data/raw/daily/
         ↓
   Calculate 16 MBI Metrics
         ↓
   Append → market_breadth.csv
         ↓
   Commit & Push to GitHub
         ↓
   GitHub Pages Auto-Deploy
```

---

## 🛡️ Data Quality & Reliability

### ✅ Stock Splits & Bonuses
- **Automatically handled** by yFinance
- Historical prices are pre-adjusted
- No manual intervention required

### ✅ Timezone Management
- **NSE**: Operates in IST (UTC+5:30)
- **yFinance**: Uses UTC timestamps
- **Our Solution**: Proper IST ↔ UTC conversion throughout

### ✅ Holiday Handling
- **NSE trading calendar** integration
- **Automatic skip** of weekends and holidays
- **Updated annually** from NSE official sources

### ✅ Data Validation
- Minimum 350/400 stocks with valid data
- Anomaly detection for suspicious price jumps
- Volume consistency checks

---

## 📊 Trading Interpretation Guidelines

### Momentum Signals
- **4.5r > 400**: Strong bullish momentum, breakouts working well
- **4.5r > 200**: Moderate bullish momentum
- **4.5r < 100**: Weak momentum, avoid new positions

### Trend Strength
- **20sma & 50sma > 150**: Strong uptrend confirmation
- **20sma & 50sma < 80**: Weak trend or downtrend

### Market Health
- **52WH(%) > 52WL(%)**: More stocks making new highs (bullish)
- **High 20+(%)**: Majority in short-term uptrend
- **High 200+(%)**: Long-term bullish market structure

### Risk Management
- Reduce position size when breadth ratios declining
- Avoid new trades when 4.5r < 100
- Use breadth divergence as early warning signal

---

## 🔧 Configuration

Edit `src/core/config.py` to customize:

```python
# SMA periods
SMA_PERIODS = [10, 20, 50, 200]

# Percentage threshold for daily movers
DAILY_CHANGE_THRESHOLD = 4.5

# Historical data range
HISTORICAL_DAYS = 365

# Minimum valid stocks required
MIN_VALID_STOCKS = 350  # out of 400
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

This tool is for **educational and informational purposes only**. It is **not financial advice**. Always:
- Do your own research before trading
- Understand the risks involved in stock trading
- Consult with a financial advisor for investment decisions
- Past market breadth does not guarantee future results

---

## 🙏 Acknowledgments

- **yFinance**: For reliable, auto-adjusted stock data
- **GitHub Actions**: For free automation infrastructure  
- **GitHub Pages**: For free dashboard hosting
- **NSE India**: For market data and indices

---

## 📧 Contact

**Tanay Khobaragade**  
GitHub: [@tanaykhobaragade](https://github.com/tanaykhobaragade)  
Project: [https://github.com/tanaykhobaragade/MBI](https://github.com/tanaykhobaragade/MBI)

---

**Happy Swing Trading! 📈**
