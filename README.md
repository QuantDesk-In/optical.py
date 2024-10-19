
# Optical - Option Calculator and Market Data Viewer

## Overview
**Optical** is a Tkinter-based desktop application designed for options traders and market analysts. The application provides two main features:
1. **Options Pricing and Implied Volatility Calculator**: Calculate option prices or implied volatility based on inputs like spot price, strike price, expiry date, and option type.
2. **Market Data Viewer**: Fetch and visualize market data for indices, stocks, and commodities. It displays candlestick charts with 30-day and 200-day exponential moving averages (EMA).

## Features
- **Options Calculator**: Calculate either the option price or implied volatility for CALL and PUT options.
- **Market Data Visualization**: Download and display candlestick charts for major indices, stocks, and commodities.
- **Save and Load Inputs**: Automatically saves user input data between sessions and loads them when the application is restarted.
- **Multiple Spot Prices**: Automatically generate option prices for a range of spot prices.

## Prerequisites
Before running the application, ensure you have the following:
- **Python** 3.x
- Required dependencies installed:
  - `tkinter`
  - `matplotlib`
  - `mplfinance`
  
## Installation

### Clone the Repository
```bash
git clone <repo-url>
cd optical
```

### Install Dependencies
To install the necessary Python libraries, execute:
```bash
pip install -r requirements.txt
```

### Build the Application with PyInstaller (for MacOS)
1. Install PyInstaller if you haven't already:
   ```bash
   pip install pyinstaller
   ```
2. Build the standalone Mac application:
   ```bash
   pyinstaller --onefile --windowed main.py
   ```
   The built application will be located in the `dist/` folder.

## Running the Application
To run the application directly from the terminal, execute the following command:
```bash
python main.py
```

## Usage

### Option Calculator Tab
1. **Input Spot Price**, **Strike Price**, **Expiry Date**, and select the **Option Type** (CALL/PUT).
2. Select whether to calculate **Option Price** or **Implied Volatility**.
3. Press **Calculate Option** to view the result based on the inputs provided.
4. To calculate option prices for multiple spot prices around the entered value, click **Multiple Spot Prices**.

### Market Data Tab
1. Select the desired **index**, **stock**, or **commodity** from the categorized buttons.
2. The application will fetch and display the candlestick data, along with 30-day and 200-day EMAs for better technical analysis.

## File Structure
```plaintext
optical/
│
├── main.py                  # Entry point of the application
├── ui.py                    # User interface code for Tkinter
├── calculations.py           # Contains the option pricing and volatility calculations
├── data_fetch.py             # Fetches market data from external sources
├── utils.py                  # Utility functions for input validation and UI toggles
├── requirements.txt          # Lists the required Python libraries
├── README.md                 # Project documentation (this file)
└── dist/                     # PyInstaller-generated standalone application folder
```

## License
This project is licensed under the **MIT License**.

## Support
For issues or contributions, please open a ticket in the project's repository.
