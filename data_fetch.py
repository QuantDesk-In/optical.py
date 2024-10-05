import yfinance as yf
import numpy as np
from tkinter import messagebox


class DataFetcher:
    def __init__(self):
        # Dictionary to hold downloaded data for tickers
        self.data_cache = {}
        self.usdinr_rate = None  # Cache for the USD/INR rate

    def download_data(self, ticker, name):
        # Check if the data for the ticker is already downloaded
        if ticker in self.data_cache:
            return self.data_cache[ticker]

        # If not, download the data and store it in the cache
        data = yf.download(ticker, period="10y")
        if data.empty:
            messagebox.showerror("Data Error", f"Could not download {name} data.")
            return None

        # Store the downloaded data in the cache
        self.data_cache[ticker] = data
        return data

    def get_usdinr_rate(self):
        # If the rate is already cached, return it
        if self.usdinr_rate is not None:
            return self.usdinr_rate

        # If not, download the current USD/INR exchange rate
        usdinr_data = yf.download("INR=X", period="1d")
        if usdinr_data.empty:
            messagebox.showerror("Data Error", "Could not fetch USD/INR rate.")
            return None

        # Cache the fetched USD/INR rate
        self.usdinr_rate = usdinr_data["Adj Close"].iloc[-1]
        return self.usdinr_rate

    def calculate_std_ranges(self, data, future_days):
        data["Returns"] = data["Adj Close"].pct_change()
        mean_return = np.mean(data["Returns"])
        std_dev = np.std(data["Returns"])
        last_close = data["Adj Close"].iloc[-1]

        projected_mean = mean_return * future_days
        projected_std_dev = std_dev * np.sqrt(future_days)

        lower_bound = round((1 + projected_mean - projected_std_dev) * last_close, 0)
        upper_bound = round((1 + projected_mean + projected_std_dev) * last_close, 0)

        return lower_bound, upper_bound

    def calculate_std_for_ticker(self, ticker, name, is_forex=False):
        # Use cached data or download if not available
        data = self.download_data(ticker, name)
        if data is None:
            return None

        # Get the cached USD/INR rate or fetch it if not available
        usdinr_rate = self.get_usdinr_rate() if is_forex else 1
        if usdinr_rate is None:
            return None

        periods = {"1 Month": 21, "3 Months": 63, "6 Months": 126, "1 Year": 252}
        last_price = data["Adj Close"].iloc[-1] * usdinr_rate

        result_text = f"{name} Current:\t{last_price:.0f}\n"
        for period, days in periods.items():
            lower_bound, upper_bound = self.calculate_std_ranges(data, days)
            if is_forex:
                lower_bound *= usdinr_rate
                upper_bound *= usdinr_rate
            result_text += f"{period}:\t{lower_bound:.0f} - {upper_bound:.0f}\n"

        return result_text
