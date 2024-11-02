import os
import threading
from datetime import datetime, timedelta

import numpy as np
import yfinance as yf
from diskcache import Cache


class DataFetcher:
    def __init__(self, cache_dir="/tmp/data_cache", cache_timeout=3600):
        # Directory and timeout for diskcache
        self.cache = Cache(cache_dir)
        self.cache_timeout = cache_timeout
        self.lock = threading.Lock()  # To manage concurrent access to data cache

    def download_data(self, ticker, name):
        def fetch_data():
            # Check if the data for the ticker is already in the cache
            with self.lock:
                if ticker in self.cache:
                    return self.cache[ticker]

            # Download the data if not in cache
            data = yf.download(ticker, period="10y")
            if data.empty:
                return None

            # Store the downloaded data in the cache
            with self.lock:
                self.cache.set(ticker, data, expire=self.cache_timeout)
            return data

        # Start a new thread to fetch the data
        thread = threading.Thread(target=fetch_data)
        thread.start()
        thread.join()  # Wait for the thread to finish if needed

        # Return cached data if available, or None if download failed
        with self.lock:
            return self.cache.get(ticker)

    def get_usdinr_rate(self):
        def fetch_usdinr():
            # Check if the USD/INR rate is in the cache
            if "USDINR" in self.cache:
                return self.cache["USDINR"]

            # Download the current USD/INR exchange rate if not in cache
            usdinr_data = yf.download("INR=X", period="1d")
            if usdinr_data.empty:
                return None

            # Cache the fetched USD/INR rate
            usdinr_rate = usdinr_data["Adj Close"].iloc[-1]
            self.cache.set("USDINR", usdinr_rate, expire=self.cache_timeout)
            return usdinr_rate

        # Start a new thread to fetch the USD/INR rate
        thread = threading.Thread(target=fetch_usdinr)
        thread.start()
        thread.join()  # Wait for the thread to finish if needed

        return self.cache.get("USDINR")

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

    def calculate_std_for_ticker(self, ticker, name, is_forex=False, multiplier=1.0):
        # Use cached data or download if not available
        data = self.download_data(ticker, name)
        if data is None:
            return None

        # Get the cached USD/INR rate or fetch it if not available
        usdinr_rate = self.get_usdinr_rate() if is_forex else 1
        if usdinr_rate is None:
            return None

        periods = {"1 Month": 21, "3 Months": 63, "6 Months": 126, "1 Year": 252}
        last_price = (data["Adj Close"].iloc[-1] * usdinr_rate) / multiplier

        result_text = f"{name}:\t{last_price:.0f}\n"
        for period, days in periods.items():
            lower_bound, upper_bound = self.calculate_std_ranges(data, days)
            if is_forex:
                lower_bound *= usdinr_rate
                upper_bound *= usdinr_rate
            if multiplier != 1.0:
                lower_bound /= multiplier
                upper_bound /= multiplier
            result_text += f"{period}:\t{lower_bound:.0f} - {upper_bound:.0f}\n"

        return result_text
