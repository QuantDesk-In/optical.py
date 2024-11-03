
# Optical - Option Calculator and Market Data Viewer

## Overview
**Optical** is a Tkinter-based desktop application designed for options traders and market analysts. It provides two main features:

1. **Option Calculator**: Calculate option prices or implied volatility based on spot price, strike price, expiry date, and option type.
2. **Market Data Viewer**: Fetch and visualize market data for indices, stocks, and commodities with candlestick charts, including 30-day and 200-day exponential moving averages (EMA).

## Features
- **Options Calculator**: Calculate option price or implied volatility for CALL and PUT options.
- **Market Data Visualization**: Display candlestick charts for indices, stocks, and commodities.
- **Save and Load Inputs**: Automatically saves and reloads user input data.
- **Multiple Spot Prices**: Generate option prices for a range of spot prices.

## Prerequisites
Ensure you have the following:
- **Python** 3.x
- Required Python libraries listed in `requirements.txt`:
  - `tkinter`
  - `matplotlib`
  - `mplfinance`
  - `py_vollib`
  - `yfinance`
  - `diskcache`

## Installation

### Clone the Repository
```bash
git clone <repo-url>
cd optical.py
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Build the Application
1. Ensure `PyInstaller` is installed:
   ```bash
   pip install pyinstaller
   ```
2. Build the application using the `Makefile`:
   ```bash
   make dist
   ```
   The built application will be in the `dist/` directory.

## Running the Application
To run the application directly from the terminal:
```bash
python main.py
```

## Usage

### Option Calculator Tab
1. Enter **Spot Price**, **Strike Price**, **Expiry Date**, and select **Option Type** (CALL/PUT).
2. Choose whether to calculate **Option Price** or **Implied Volatility**.
3. Click **Calculate Option** to see the result.
4. Use **Multiple Spot Prices** to calculate prices for a range of spot values.

### Market Data Tab
1. Select an **index**, **stock**, or **commodity**.
2. The application fetches data and displays a candlestick chart with EMAs.

## File Structure
```plaintext
optical.py/
│
├── main.py                # Main entry point of the application
├── ui.py                  # User interface code
├── calculations.py        # Option pricing and volatility calculations
├── data_fetch.py          # Market data fetching logic
├── utils.py               # Utility functions
├── Makefile               # Build instructions
├── requirements.txt       # Required Python libraries
└── dist/                  # PyInstaller output folder for the standalone application
```

## License
This project is licensed under the **MIT License**.

## Support
For issues or contributions, open a ticket in the project's repository.
