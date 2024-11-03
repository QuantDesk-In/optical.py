import json
import os
import tkinter as tk
from tkinter import simpledialog, ttk

import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from calculations import OptionCalculator
from data_fetch import DataFetcher
from utils import toggle_inputs, validate_inputs


class OptionCalculatorTab:
    TMP_FILE = "/tmp/optical.inputs"

    def __init__(self, parent):
        self.calculator = OptionCalculator()
        self.parent = parent
        self.option_type_var = tk.StringVar()
        self.calculation_mode = tk.StringVar(value="volatility")
        self.create_tab()

    def create_tab(self):
        """Create the Option Calculator tab."""
        self.frame = ttk.Frame(self.parent)
        self.parent.add(self.frame, text="Option Calculator")

        input_frame = self.create_input_frame(self.frame)
        calc_settings_frame = self.create_calc_settings_frame(self.frame)
        action_frame = self.create_action_frame(self.frame)

    def create_input_frame(self, parent):
        """Creates the input frame for the Option Calculator tab."""
        frame = ttk.LabelFrame(parent, text="Input Data")
        frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        self.create_label_entry(frame, "Spot Price:", 0, "spot_entry")
        self.create_label_entry(frame, "Strike Price:", 1, "strike_entry")
        self.create_label_entry(frame, "Expiry Date (YYYY-MM-DD):", 2, "expiry_entry")

        ttk.Label(frame, text="Option Type (CALL/PUT):").grid(
            row=3, column=0, sticky="w", padx=10, pady=10
        )
        option_type_menu = ttk.Combobox(
            frame,
            textvariable=self.option_type_var,
            state="readonly",
            values=["CALL", "PUT"],
        )
        option_type_menu.grid(row=3, column=1, padx=10, pady=10)
        option_type_menu.current(0)

        return frame

    def create_calc_settings_frame(self, parent):
        """Creates the calculation settings frame for the Option Calculator tab."""
        frame = ttk.LabelFrame(parent, text="Calculation Settings")
        frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        self.create_radio_button(frame, "Calculate Implied Volatility", 4, "volatility")
        self.create_radio_button(frame, "Calculate Option Price", 5, "price")

        self.create_label_entry(frame, "Option Price:", 6, "price_entry")
        self.create_label_entry(
            frame, "Implied Volatility:", 7, "volatility_entry", state="disabled"
        )

        return frame

    def create_action_frame(self, parent):
        """Creates the action frame with buttons in the Option Calculator tab."""
        frame = ttk.Frame(parent)
        frame.grid(row=8, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        ttk.Button(
            frame, text="Calculate Option", command=self.calculate_option, width=15
        ).grid(row=8, column=0, columnspan=2, pady=10)
        ttk.Button(
            frame,
            text="Multiple Spot Prices",
            command=self.calculate_for_multiple_spots,
            width=15,
        ).grid(row=9, column=0, columnspan=2, pady=10)

        self.result_label = ttk.Label(frame, text="")
        self.result_label.grid(row=13, column=0, columnspan=2, pady=10)

        return frame

    def create_label_entry(self, parent, text, row, attr_name, state="normal"):
        """Utility function to create label and entry widgets."""
        ttk.Label(parent, text=text).grid(
            row=row, column=0, sticky="w", padx=10, pady=10
        )
        entry = ttk.Entry(parent, state=state)
        entry.grid(row=row, column=1, padx=10, pady=10)
        setattr(self, attr_name, entry)

    def create_radio_button(self, parent, text, row, value):
        """Utility function to create radio buttons."""
        ttk.Radiobutton(
            parent,
            text=text,
            variable=self.calculation_mode,
            value=value,
            command=self.toggle_inputs,
        ).grid(row=row, column=0, sticky="w", padx=10, pady=10)

    def toggle_inputs(self):
        toggle_inputs(self.calculation_mode, self.price_entry, self.volatility_entry)

    def calculate_option(self):
        inputs = validate_inputs(
            self.spot_entry,
            self.strike_entry,
            self.expiry_entry,
            self.price_entry,
            self.volatility_entry,
            self.calculation_mode,
        )
        if inputs:
            spot, strike, expiry_date, price, volatility = inputs
            result = self.calculator.calculate(
                spot,
                strike,
                expiry_date,
                self.option_type_var.get(),
                self.calculation_mode.get(),
                price,
                volatility,
            )
            self.result_label.config(text=result)
            self.save_input_data()

    def calculate_for_multiple_spots(self):
        """Calculates the option price for multiple spot prices dynamically."""
        inputs = validate_inputs(
            self.spot_entry,
            self.strike_entry,
            self.expiry_entry,
            self.price_entry,
            self.volatility_entry,
            self.calculation_mode,
        )
        if inputs:
            spot, strike, expiry_date, price, volatility = inputs
            option_type = self.option_type_var.get()

            # Generate multiple spot prices dynamically
            spot_prices = self.generate_dynamic_spot_prices(spot)
            results = []

            # Recalculate volatility if needed
            if self.calculation_mode.get() == "volatility":
                volatility = self.calculator.calculate(
                    spot,
                    strike,
                    expiry_date,
                    option_type,
                    "volatility",
                    price,
                    volatility,
                )

            # Calculate option price for each spot
            for s in spot_prices:
                result = self.calculator.calculate(
                    s, strike, expiry_date, option_type, "price", price, volatility
                )
                results.append(f"{s}\t: {result}")

            self.result_label.config(text="\n".join(results))

    def generate_dynamic_spot_prices(self, spot):
        """Generates a list of spot prices around the given spot price."""
        step = (
            50
            if spot < 100
            else (
                500
                if spot >= 10000
                else 100 if spot >= 1000 else 10 if spot >= 500 else 5
            )
        )
        rounded_spot = round(spot / step) * step
        return [
            rounded_spot - 2 * step,
            rounded_spot - step,
            rounded_spot,
            rounded_spot + step,
            rounded_spot + 2 * step,
        ]

    def save_input_data(self):
        """Saves input data to a temporary file."""
        input_data = {
            "spot_price": self.spot_entry.get(),
            "strike_price": self.strike_entry.get(),
            "expiry_date": self.expiry_entry.get(),
            "option_type": self.option_type_var.get(),
            "calculation_mode": self.calculation_mode.get(),
            "option_price": self.price_entry.get(),
            "volatility": self.volatility_entry.get(),
        }
        with open(self.TMP_FILE, "w") as f:
            json.dump(input_data, f)

    def load_saved_data(self):
        """Loads saved data from the temporary file if it exists."""
        if os.path.exists(self.TMP_FILE):
            with open(self.TMP_FILE, "r") as f:
                input_data = json.load(f)
                self.spot_entry.insert(0, input_data.get("spot_price", ""))
                self.strike_entry.insert(0, input_data.get("strike_price", ""))
                self.expiry_entry.insert(0, input_data.get("expiry_date", ""))
                self.option_type_var.set(input_data.get("option_type", "CALL"))
                self.calculation_mode.set(
                    input_data.get("calculation_mode", "volatility")
                )
                self.price_entry.insert(0, input_data.get("option_price", ""))
                self.volatility_entry.insert(0, input_data.get("volatility", ""))


class MarketDataTab:
    def __init__(self, parent):
        self.data_fetcher = DataFetcher()
        self.canvas = None
        self.ema_data = {}
        self.last_group = None  # Track last group clicked
        self.create_tab(parent)
        self.ticker_info = None

    def show_date_input_dialog(self):
        """Shows an input dialog for the user to enter a date."""
        date_input = simpledialog.askstring(
            "Input Date", "Enter the date (YYYY-MM-DD):", initialvalue="2024-03-31"
        )
        if date_input:
            try:
                # Validate the input date format
                pd.to_datetime(date_input, format="%Y-%m-%d")
                self.fetch_and_plot_data_with_date(date_input)
            except ValueError:
                tk.messagebox.showerror(
                    "Invalid Date", "Please enter a valid date in YYYY-MM-DD format."
                )

    def fetch_and_plot_data_with_date(self, date_input):
        """Fetches and plots data based on the input date."""
        self.fetch_and_plot_data(self.ticker_info, date_input=date_input)

    def create_tab(self, parent):
        """Create the Market Data tab."""
        self.frame = ttk.Frame(parent)
        parent.add(self.frame, text="Market Data")

        button_frame = self.create_button_frame(self.frame)
        self.create_market_data_buttons(button_frame)

        # Labels for results
        self.market_result_label = ttk.Label(button_frame, text="")
        self.market_result_label.grid(row=3, column=0, pady=10)

        self.ema_label = ttk.Label(button_frame, text="")
        self.ema_label.grid(row=4, column=0, pady=10)

        # Configure layout for the chart
        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)

    def create_button_frame(self, parent):
        """Creates the button frame for selecting indices, stocks, and commodities."""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=0, column=0, sticky="n", padx=10, pady=10)
        return button_frame

    def create_market_data_buttons(self, parent):
        """Creates buttons for market data categories."""
        group_1 = [
            {"label": "NIFTY 50", "ticker": "^NSEI"},
            {"label": "BANKNIFTY", "ticker": "^NSEBANK"},
            {"label": "MIDCAP 50", "ticker": "^NSEMDCP50"},
        ]
        group_2 = [
            {"label": "ITC", "ticker": "ITC.NS"},
            {"label": "HDFCBANK", "ticker": "HDFCBANK.NS"},
            {"label": "ICICIBANK", "ticker": "ICICIBANK.NS"},
            {"label": "INFOSYS", "ticker": "INFY.NS"},
            {"label": "RELIANCE", "ticker": "RELIANCE.NS"},
        ]
        group_3 = [
            {"label": "CRUDE MCX", "ticker": "CL=F", "is_forex": True, "group": "MCX"},
            {
                "label": "GOLD MCX",
                "ticker": "GC=F",
                "is_forex": True,
                "multiplier": 31.1035,
                "group": "MCX",
            },
            {
                "label": "SILVER MCX",
                "ticker": "SI=F",
                "is_forex": True,
                "multiplier": 31.1035,
                "group": "MCX",
            },
        ]

        self.add_group_buttons(parent, group_1, "Indices", 0)
        self.add_group_buttons(parent, group_2, "Stocks", 1)
        self.add_group_buttons(parent, group_3, "Commodities", 2)

    def add_group_buttons(self, parent, group, title, row):
        """Utility to add buttons for each group (Indices, Stocks, Commodities)."""
        group_frame = ttk.LabelFrame(parent, text=title)
        group_frame.grid(row=row, column=0, padx=10, pady=10, sticky="ew")
        for index, ticker in enumerate(group):
            ttk.Button(
                group_frame,
                text=ticker["label"],
                command=lambda t=ticker: self.fetch_and_plot_data(t),
                width=10,
            ).grid(row=index, column=0, padx=10, pady=5)

    def fetch_and_plot_data(self, ticker_info, date_input=None):
        """Fetches data and plots candlestick chart for a given ticker and optional date."""
        current_group = ticker_info.get("group", "Others")

        # Clear ema_data if switching between MCX and other groups
        if self.last_group and self.last_group != current_group:
            self.ema_data.clear()
        self.last_group = current_group
        self.ticker_info = ticker_info
        self.market_result_label.config(text=f"Fetching {ticker_info['label']} data...")
        self.frame.update()

        range_text = self.data_fetcher.calculate_std_for_ticker(
            ticker_info["ticker"],
            ticker_info["label"],
            ticker_info.get("is_forex", False),
            ticker_info.get("multiplier", 1.0),
        )
        self.market_result_label.config(text=range_text)

        data = self.data_fetcher.download_data(
            ticker_info["ticker"], ticker_info["label"]
        )

        if ticker_info.get("is_forex", False):
            usdinr = self.data_fetcher.get_usdinr_rate()
            data = data * usdinr
        if ticker_info.get("multiplier", 1.0) != 1.0:
            data = data / ticker_info.get("multiplier", 1.0)

        if date_input:
            try:
                date_input = pd.to_datetime(date_input)
                data = data.loc[data.index <= date_input]
            except Exception as e:
                self.market_result_label.config(text=f"Error filtering data: {str(e)}")
                return

        # WIP - calculate the cumulative return
        # Initialize the "Projection 5 Years" column with NaNs
        data["Projection 5 Years"] = float("nan")

        start_price = data["Adj Close"].iloc[0]
        end_price = data["Adj Close"].iloc[-1]
        n_years = (data.index[-1] - data.index[0]).days / 365.0
        cum_return = (end_price / start_price) - 1
        discount_rate = (1 + cum_return) ** (1 / n_years) - 1

        if len(data) > 1512:
            five_years_ago_price = data.iloc[-1512:].head(252)["Adj Close"].max()
            projected_value = five_years_ago_price * (1 + discount_rate) ** 5

            # Assign values to the specific rows
            data.at[data.index[-1], "Projection 5 Years"] = projected_value
            data.at[data.index[-1255], "Projection 5 Years"] = five_years_ago_price

            # Interpolate the missing values
            data["Projection 5 Years"].interpolate(inplace=True)
        # WIP end

        if data is not None:
            self.plot_candlestick(data, ticker_info["label"])

    def plot_candlestick(self, data, ticker_name):
        """Plots candlestick chart for the market data."""
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        data["EMA_30"] = data["Adj Close"].ewm(span=30, adjust=False).mean()
        data["EMA_200"] = data["Adj Close"].ewm(span=200, adjust=False).mean()
        data = data[-125:]

        close = data.iloc[-1]["Adj Close"]
        ema = data.iloc[-1]["EMA_30"]

        if ticker_name not in self.ema_data:
            self.ema_data[ticker_name] = {"ema": ema, "close": close}

        self.update_ema_label()

        # List of addplots
        addplots = [
            mpf.make_addplot(data["EMA_30"], color="blue"),
            mpf.make_addplot(data["EMA_200"], color="red"),
        ]

        # Check if "Projection 5 Years" has any non-NaN data
        if not data["Projection 5 Years"].isna().all():
            addplots.append(
                mpf.make_addplot(
                    data["Projection 5 Years"], color="green", linestyle="--", width=0.8
                )
            )

        fig, ax = mpf.plot(
            data,
            type="hollow_candle",
            style="charles",
            title=ticker_name,
            ylabel="Price",
            addplot=addplots,
            returnfig=True,
        )

        ax[0].text(
            0.5,
            0.95,
            f"{close:.2f}",
            horizontalalignment="right",
            verticalalignment="top",
            transform=ax[0].transAxes,
            fontsize=11,
        )

        self.canvas = FigureCanvasTkAgg(fig, master=self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=1, rowspan=5, padx=20, pady=10)

        plt.close(fig)

    def update_ema_label(self):
        """Updates the EMA label with the latest data."""
        txt = "Ticker\t    EMA\tCLOSE\tBULLISH"
        for t in self.ema_data:
            d = self.ema_data[t]
            e = d["ema"]
            c = d["close"]
            b = 1 if c > e else 0
            txt = txt + "\n" + f"{t[:8]}\t    {e:.0f}\t{c:.0f}\t{b}"
        self.ema_label.config(text=txt)


class OptionCalculatorUI:
    def __init__(self, root):
        self.root = root
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky="nsew")

        self.option_calculator_tab = OptionCalculatorTab(self.notebook)
        self.market_data_tab = MarketDataTab(self.notebook)

        # Load saved data after initialization
        self.option_calculator_tab.load_saved_data()
