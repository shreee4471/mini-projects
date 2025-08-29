# Real-Time Stock Market Monitor with Alerts

A Python-based stock monitoring system that allows users to track stocks in real-time and receive alerts based on custom thresholds.

## Available Versions

### 1. GUI Version (Recommended)
**File:** `stock_monitor_gui.py`
- Graphical user interface
- Desktop notifications
- Easy configuration
- Real-time monitoring with visual feedback

### 2. Console Version
**File:** `stock_monitor_configurable.py`
- Command-line interface
- Interactive setup
- Basic monitoring functionality

## Features

- ✅ Monitor any stock symbol (US and International)
- ✅ Set custom buy/sell alert thresholds
- ✅ Configure monitoring interval (1-60 minutes)
- ✅ Real-time price updates
- ✅ Desktop notifications for alerts
- ✅ Alert notifications for:
  - Price crossing buy threshold
  - Price crossing sell threshold
  - Significant price movements (2%+)
- ✅ Configuration persistence (saves settings to file)
- ✅ Graphical user interface (GUI version)

## Supported Stock Symbols

- US Stocks: `AAPL`, `MSFT`, `GOOGL`, `TSLA`, etc.
- Indian Stocks: Use `.NS` suffix (e.g., `RELIANCE.NS`, `BANKNIFTY.NS`)
- International Stocks: Use appropriate exchange suffixes

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. Run the preferred version:

**GUI Version (Recommended):**
```bash
python stock_monitor_gui.py
```

**Console Version:**
```bash
python stock_monitor_configurable.py
```

## Usage (GUI Version)

1. **Add Stocks**: Enter stock symbol and set buy/sell thresholds
2. **Set Interval**: Choose monitoring frequency (1-60 minutes)
3. **Start Monitoring**: Click "Start Monitoring" button
4. **View Alerts**: See real-time updates in the output console
5. **Desktop Notifications**: Receive pop-up alerts for important events

## Configuration File

Settings are saved in `stock_config.json`:
```json
{
    "stocks": {
        "AAPL": {
            "buy_threshold": 150.0,
            "sell_threshold": 180.0
        }
    },
    "interval_minutes": 5
}
```

## Example Stock Symbols

- Apple: `AAPL`
- Microsoft: `MSFT`
- Google: `GOOGL`
- Tesla: `TSLA`
- Reliance (India): `RELIANCE.NS`
- Bank Nifty (India): `BANKNIFTY.NS`
- Infosys (India): `INFY.NS`
- Nifty 50 (India): `NSEI` or `^NSEI`

## Requirements

- Python 3.6+
- yfinance
- schedule
- plyer (for desktop notifications)
- tkinter (usually included with Python)

## Notes
-You can modify as your own needs 
-You can upgrade it. and showcase so that it is helpful for everyone
PEACE ✌ 


- The system uses Yahoo Finance API through yfinance library
- Prices are updated every minute (maximum frequency)
- For Indian stocks, always use appropriate exchange suffixes (.NS for NSE)
- Desktop notifications work on Windows, macOS, and Linux
- The GUI version provides the best user experience with real-time visual feedback

