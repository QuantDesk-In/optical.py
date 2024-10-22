import threading
from tkinter import messagebox

import numpy as np
import yfinance as yf


class DataFetcher:
    def __init__(self):
        # Dictionary to hold downloaded data for tickers
        self.data_cache = {}
        self.usdinr_rate = None  # Cache for the USD/INR rate
        self.lock = threading.Lock()  # To manage concurrent access to data cache

    def download_data(self, ticker, name):
        def fetch_data():
            # Check if the data for the ticker is already downloaded
            with self.lock:
                if ticker in self.data_cache:
                    return

            # If not, download the data
            data = yf.download(ticker, period="10y")
            if data.empty:
                messagebox.showerror("Data Error", f"Could not download {name} data.")
                return

            # Store the downloaded data in the cache
            with self.lock:
                self.data_cache[ticker] = data

        # Start a new thread to fetch the data
        thread = threading.Thread(target=fetch_data)
        thread.start()
        thread.join()  # Wait for the thread to finish if needed

        # Return cached data if available, or None if download failed
        with self.lock:
            return self.data_cache.get(ticker)

    def get_usdinr_rate(self):
        def fetch_usdinr():
            # If the rate is already cached, return it
            if self.usdinr_rate is not None:
                return

            # If not, download the current USD/INR exchange rate
            usdinr_data = yf.download("INR=X", period="1d")
            if usdinr_data.empty:
                messagebox.showerror("Data Error", "Could not fetch USD/INR rate.")
                return

            # Cache the fetched USD/INR rate
            self.usdinr_rate = usdinr_data["Adj Close"].iloc[-1]

        # Start a new thread to fetch the USD/INR rate
        thread = threading.Thread(target=fetch_usdinr)
        thread.start()
        thread.join()  # Wait for the thread to finish if needed

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

        result_text = f"{name}:\t{last_price:.0f}\n"
        for period, days in periods.items():
            lower_bound, upper_bound = self.calculate_std_ranges(data, days)
            if is_forex:
                lower_bound *= usdinr_rate
                upper_bound *= usdinr_rate
            result_text += f"{period}:\t{lower_bound:.0f} - {upper_bound:.0f}\n"

        return result_text
