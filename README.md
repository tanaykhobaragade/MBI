# MBI - Market Breadth Indicator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)

Automated Market Breadth Indicator (MBI) for **NIFTY MIDSMALLCAP 400** - Daily NSE stock data processing and breadth analysis for swing trading.

## 📊 Overview

This project automates the calculation of market breadth metrics for the NIFTY MIDSMALLCAP 400 index. It fetches daily OHLCV data from NSE, calculates various breadth indicators, and outputs the results to CSV files that can be easily imported into Excel or Google Sheets.

### Key Features

- ✅ **Fully Automated**: GitHub Actions runs daily at 6 PM IST
- ✅ **No Infrastructure Required**: Runs entirely on GitHub's free tier
- ✅ **Device Agnostic**: Access CSV data from any device
- ✅ **Historical Data**: Maintains 1+ year of historical breadth data
- ✅ **Excel/Sheets Ready**: Direct import via raw GitHub URLs

## 📈 Metrics Calculated

| Metric | Description |
|--------|-------------|
| **Date** | Trading date |
| **52WH(%)** | % of stocks hitting new 52-week high |
| **52WL(%)** | % of stocks hitting new 52-week low |
| **4.5+(%)** | % of stocks up by 4.5%+ in a day |
| **4.5-(%)** | % of stocks down by 4.5%+ in a day |
| **10+(%)** | % of stocks above 10 SMA |
| **10-(%)** | % of stocks below 10 SMA |
| **20+(%)** | % of stocks above 20 SMA |
| **20-(%)** | % of stocks below 20 SMA |
| **50+(%)** | % of stocks above 50 SMA |
| **50-(%)** | % of stocks below 50 SMA |
| **200+(%)** | % of stocks above 200 SMA |
| **200-(%)** | % of stocks below 200 SMA |
| **4.5r** | Ratio: [4.5+(%) / 4.5-(%)] × 100 |
| **20sma** | Ratio: [20+(%) / 20-(%)] × 100 |
| **50sma** | Ratio: [50+(%) / 50-(%)] × 100 |

## 🏗️ Project Structure

```
MBI/
├── .github/
│   └── workflows/
│       ├── fetch_daily_data.yml      # Daily automation
│       └── initialize_historical.yml  # One-time setup
├── data/
│   ├── raw/                          # Per-stock CSV files
│   ├── processed/
│   │   └── market_breadth.csv        # Main output file
│   └── meta/
│       ├── nifty_midsmallcap400.csv  # Index constituents
│       └── nse_holidays.json         # Trading calendar
├── src/
│   ├── config.py                     # Configuration
│   ├── utils.py                      # Helper functions
│   ├── data_fetch.py                 # Data fetching
│   └── calculate_breadth.py          # MBI calculations
├── requirements.txt
├── README.md
└── LICENSE
```

## 🚀 Quick Start

### Import into Google Sheets

```
=IMPORTDATA("https://raw.githubusercontent.com/tanaykhobaragade/MBI/main/data/processed/market_breadth.csv")
```

### Import into Excel

1. **Data** → **Get Data** → **From Web**
2. Enter URL: `https://raw.githubusercontent.com/tanaykhobaragade/MBI/main/data/processed/market_breadth.csv`
3. Click **Load**

## 💻 Local Development

### Prerequisites

- Python 3.8+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/tanaykhobaragade/MBI.git
cd MBI

# Install dependencies
pip install -r requirements.txt

# Run data fetch
python src/data_fetch.py

# Calculate breadth metrics
python src/calculate_breadth.py
```

## 🔄 Automation Details

### Daily Workflow

1. **Trigger**: GitHub Actions at 6:00 PM IST (Mon-Fri)
2. **Check**: Is today a trading day?
3. **Fetch**: Download EOD data for all 400 stocks
4. **Calculate**: Compute all MBI metrics
5. **Update**: Commit updated CSVs to repository

### Data Sources

- **Stock Data**: NSE India official endpoints
- **Constituents**: NIFTY MIDSMALLCAP 400 index factsheet
- **Holidays**: NSE trading calendar

## 📊 Usage for Swing Trading

### Interpretation Guidelines

- **4.5r > 400**: Strong bullish momentum, breakouts working
- **20sma & 50sma > 150**: Strong uptrend confirmation
- **52WH > 52WL**: More stocks making new highs (bullish)
- **High 20+(%)**: Majority of stocks in short-term uptrend

### Risk Management

- Reduce position size when ratios are declining
- Avoid new positions when 4.5r < 100 (weak momentum)
- Use breadth divergence as early warning signal

## 🛠️ Configuration

Edit `src/config.py` to customize:

- SMA periods (default: 10, 20, 50, 200)
- Percentage thresholds (default: 4.5%)
- Data fetch intervals
- Index constituents

## 📝 Data Handling

### Corporate Actions

- **Splits/Bonuses**: Data sources provide adjusted prices
- **Verification**: Cross-checked with NSE corporate actions

### Holidays

- **NSE Calendar**: Automatically fetched and updated
- **Weekends**: Skipped automatically

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational and informational purposes only. It is not financial advice. Always do your own research before making investment decisions.

## 📧 Contact

Tanay Khobaragade - [@tanaykhobaragade](https://github.com/tanaykhobaragade)

Project Link: [https://github.com/tanaykhobaragade/MBI](https://github.com/tanaykhobaragade/MBI)

---

**Happy Trading! 📈**
