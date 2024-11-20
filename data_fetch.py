import logging
import threading

import numpy as np
import yfinance as yf
from diskcache import Cache

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)


class DataFetcher:
    def __init__(self, cache_dir="/tmp/data_cache", cache_timeout=3600):
        self.cache = Cache(cache_dir)
        self.cache_timeout = cache_timeout
        self.lock = threading.Lock()  # To manage concurrent access to data cache

    def download_data(self, ticker, name):
        def fetch_data():
            try:
                with self.lock:
                    if ticker in self.cache:
                        logging.info(f"Cache hit for ticker: {ticker}")
                        return self.cache[ticker]

                logging.info(f"Downloading data for ticker: {ticker}")
                data = yf.download(ticker, period="10y")
                if data.empty:
                    logging.warning(f"No data found for ticker: {ticker}")
                    return None

                with self.lock:
                    self.cache.set(ticker, data, expire=self.cache_timeout)
                return data
            except Exception as e:
                logging.error(f"Error fetching data for {ticker}: {e}")
                return None

        thread = threading.Thread(target=fetch_data)
        thread.start()
        thread.join(timeout=5)  # Timeout of 5 seconds
        if thread.is_alive():
            logging.warning(f"Timeout occurred while fetching data for {ticker}")
            return None

        with self.lock:
            return self.cache.get(ticker)

    def get_usdinr_rate(self):
        def fetch_usdinr():
            try:
                with self.lock:
                    if "USDINR" in self.cache:
                        logging.info("Cache hit for USD/INR rate")
                        return self.cache["USDINR"]

                logging.info("Downloading USD/INR exchange rate")
                usdinr_data = yf.download("INR=X", period="1d")
                if usdinr_data.empty:
                    logging.warning("No data found for USD/INR rate")
                    return None

                usdinr_rate = usdinr_data["Adj Close"].iloc[-1]
                with self.lock:
                    self.cache.set("USDINR", usdinr_rate, expire=self.cache_timeout)
                return usdinr_rate
            except Exception as e:
                logging.error(f"Error fetching USD/INR rate: {e}")
                return None

        thread = threading.Thread(target=fetch_usdinr)
        thread.start()
        thread.join(timeout=5)  # Timeout of 5 seconds
        if thread.is_alive():
            logging.warning("Timeout occurred while fetching USD/INR rate")
            return None

        with self.lock:
            return self.cache.get("USDINR")

    def calculate_std_ranges(self, data, future_days):
        try:
            data["Returns"] = data["Adj Close"].pct_change()
            mean_return = np.mean(data["Returns"])
            std_dev = np.std(data["Returns"])
            last_close = data["Adj Close"].iloc[-1]

            projected_mean = mean_return * future_days
            projected_std_dev = std_dev * np.sqrt(future_days)

            lower_bound = round(
                (1 + projected_mean - projected_std_dev) * last_close, 0
            )
            upper_bound = round(
                (1 + projected_mean + projected_std_dev) * last_close, 0
            )
            projected_price = round((1 + projected_mean) * last_close, 0)

            return lower_bound, upper_bound, projected_price
        except Exception as e:
            logging.error(f"Error calculating standard deviation ranges: {e}")
            return None, None, None

    def calculate_std_for_ticker(self, ticker, name, is_forex=False, multiplier=1.0):
        data = self.download_data(ticker, name)
        if data is None:
            logging.warning(f"Data for ticker {ticker} could not be fetched")
            return None

        usdinr_rate = self.get_usdinr_rate() if is_forex else 1
        if is_forex and usdinr_rate is None:
            logging.warning("USD/INR rate could not be fetched")
            return None

        periods = {"1 Month": 21, "3 Months": 63, "1 Year": 252}
        last_price = (data["Adj Close"].iloc[-1] * usdinr_rate) / multiplier

        result_text = f"{name}:\t{last_price:.0f}\n"
        for period, days in periods.items():
            lower_bound, upper_bound, projected_price = self.calculate_std_ranges(
                data, days
            )
            if lower_bound is None:
                continue

            if is_forex:
                lower_bound *= usdinr_rate
                upper_bound *= usdinr_rate
                projected_price *= usdinr_rate
            if multiplier != 1.0:
                lower_bound /= multiplier
                upper_bound /= multiplier
                projected_price /= multiplier
            result_text += f"{period}:\t{lower_bound:.0f}  - {projected_price:.0f} - {upper_bound:.0f}\n"

        return result_text

    def clear_cache(self):
        with self.lock:
            logging.info("Clearing cache")
            self.cache.clear()
