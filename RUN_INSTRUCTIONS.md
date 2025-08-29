# Run Instructions for Stock Market Monitor

## Installation (First Time Only)

1. Open Command Prompt or PowerShell
2. Navigate to the project directory:
```bash
cd C:\Mini-project
```

3. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Running the Applications

### Option 1: GUI Version (Recommended)
Run the graphical user interface version with desktop notifications:
```bash
python stock_monitor_gui.py
```

### Option 2: Console Version
Run the command-line interface version:
```bash
python stock_monitor_configurable.py
```

## Step-by-Step Execution Order

### For First-Time Users:
1. **Install dependencies** (one-time setup)
2. **Run GUI version** for best experience:
   ```bash
   python stock_monitor_gui.py
   ```
3. Follow the on-screen instructions to add stocks and set thresholds

### For Advanced Users:
1. **Install dependencies** (if not already done)
2. **Run console version** for script-based operation:
   ```bash
   python stock_monitor_configurable.py
   ```
3. Follow the interactive prompts

## File Descriptions

- **stock_monitor_gui.py** - Main application with GUI and notifications
- **stock_monitor_configurable.py** - Console version with interactive setup
- **requirements.txt** - Python package dependencies
- **stock_config.json** - Configuration file (created automatically)
- **README.md** - Detailed documentation

## Quick Start Recommendation

Run this sequence:
```bash
cd C:\Mini-project
pip install -r requirements.txt
python stock_monitor_gui.py
```

The GUI version provides the most user-friendly experience with visual feedback and desktop notifications.
