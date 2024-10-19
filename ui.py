import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplfinance as mpf
from calculations import OptionCalculator
from data_fetch import DataFetcher
from utils import toggle_inputs, validate_inputs
import matplotlib.pyplot as plt


class OptionCalculatorUI:
    def __init__(self, root):
        self.root = root
        self.calculator = OptionCalculator()
        self.data_fetcher = DataFetcher()
        self.canvas = None  # This will hold the chart canvas

        # Setup the Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky="nsew")

        # Initialize Tabs
        self.tabs = {}
        self.init_option_calculator_tab()
        self.init_market_data_tab()

        # Configure grid for dynamic resizing
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

    def init_option_calculator_tab(self):
        """Initializes the Option Calculator tab."""
        option_tab = ttk.Frame(self.notebook)
        self.notebook.add(option_tab, text="Option Calculator")

        # Create input frame
        input_frame = self.create_input_frame(option_tab)
        calc_settings_frame = self.create_calc_settings_frame(option_tab)
        action_frame = self.create_action_frame(option_tab)

    def create_input_frame(self, parent):
        """Creates the input frame in the option calculator tab."""
        frame = ttk.LabelFrame(parent, text="Input Data")
        frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        self.create_label_entry(frame, "Spot Price:", 0, "spot_entry")
        self.create_label_entry(frame, "Strike Price:", 1, "strike_entry")
        self.create_label_entry(frame, "Expiry Date (YYYY-MM-DD):", 2, "expiry_entry")

        # Option Type Dropdown
        ttk.Label(frame, text="Option Type (CALL/PUT):").grid(
            row=3, column=0, sticky="w", padx=10, pady=10
        )
        self.option_type_var = tk.StringVar()
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
        """Creates the calculation settings frame in the option calculator tab."""
        frame = ttk.LabelFrame(parent, text="Calculation Settings")
        frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        self.calculation_mode = tk.StringVar(value="volatility")
        self.create_radio_button(frame, "Calculate Implied Volatility", 4, "volatility")
        self.create_radio_button(frame, "Calculate Option Price", 5, "price")

        # Option Price and Volatility Inputs
        self.create_label_entry(frame, "Option Price:", 6, "price_entry")
        self.create_label_entry(
            frame, "Implied Volatility:", 7, "volatility_entry", state="disabled"
        )

        return frame

    def create_action_frame(self, parent):
        """Creates the action frame with buttons in the option calculator tab."""
        frame = ttk.Frame(parent)
        frame.grid(row=8, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        ttk.Button(frame, text="Calculate Option", command=self.calculate_option).grid(
            row=8, column=0, columnspan=2, pady=10
        )
        ttk.Button(
            frame,
            text="Multiple Spot Prices",
            command=self.calculate_for_multiple_spots,
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

    def init_market_data_tab(self):
        """Initializes the Market Data tab and groups buttons by categories."""
        self.market_data_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.market_data_tab, text="Market Data")

        # Define groups of tickers
        group_1 = [
            {"label": "NIFTY 50", "ticker": "^NSEI", "name": "Nifty"},
            {"label": "BANKNIFTY", "ticker": "^NSEBANK", "name": "Banknifty"},
            {
                "label": "MIDCAP 50",
                "ticker": "^NSEMDCP50",
                "name": "Nifty Midcap 50",
            },
        ]

        group_2 = [
            {"label": "ITC", "ticker": "ITC.NS", "name": "ITC"},
            {"label": "HDFCBANK", "ticker": "HDFCBANK.NS", "name": "HDFC Bank"},
            {
                "label": "ICICIBANK",
                "ticker": "ICICIBANK.NS",
                "name": "ICICI Bank",
            },
            {"label": "INFOSYS", "ticker": "INFY.NS", "name": "Infosys"},
            {"label": "RELIANCE", "ticker": "RELIANCE.NS", "name": "Reliance"},
        ]

        group_3 = [
            {
                "label": "CRUDE MCX",
                "ticker": "CL=F",
                "name": "Crude Oil",
                "is_forex": True,
            }
        ]

        # Create frames for each group
        button_frame = ttk.Frame(self.market_data_tab)
        button_frame.grid(row=0, column=0, sticky="n", padx=10, pady=10)

        # Add buttons for group 1 (Nifty, Bank Nifty, Midcap)
        group_1_frame = ttk.LabelFrame(button_frame, text="Indices")
        group_1_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        for index, ticker in enumerate(group_1):
            ttk.Button(
                group_1_frame,
                text=ticker["label"],
                command=lambda t=ticker: self.fetch_and_plot_data(t),
                width=10,  # Set fixed width
            ).grid(row=index, column=0, padx=10, pady=5)

        # Add buttons for group 2 (ITC, HDFC, ICICI, Infosys, Reliance)
        group_2_frame = ttk.LabelFrame(button_frame, text="Stocks")
        group_2_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        for index, ticker in enumerate(group_2):
            ttk.Button(
                group_2_frame,
                text=ticker["label"],
                command=lambda t=ticker: self.fetch_and_plot_data(t),
                width=10,  # Set fixed width
            ).grid(row=index, column=0, padx=10, pady=5)

        # Add button for group 3 (Crude)
        group_3_frame = ttk.LabelFrame(button_frame, text="Commodities")
        group_3_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        for index, ticker in enumerate(group_3):
            ttk.Button(
                group_3_frame,
                text=ticker["label"],
                command=lambda t=ticker: self.fetch_and_plot_data(t),
                width=10,  # Set fixed width
            ).grid(row=index, column=0, padx=10, pady=5)

        # Result label for market data feedback
        self.market_result_label = ttk.Label(button_frame, text="")
        self.market_result_label.grid(row=3, column=0, pady=10)

        # Set up grid layout for chart display
        self.market_data_tab.grid_columnconfigure(1, weight=1)
        self.market_data_tab.grid_rowconfigure(0, weight=1)

    def fetch_and_plot_data(self, ticker_info):
        """Fetches data and plots candlestick for a given ticker."""
        self.market_result_label.config(
            text=f"Fetching {ticker_info['name']} data..."
        )  # Feedback
        self.root.update()  # Force immediate update for visual feedback

        range_text = self.data_fetcher.calculate_std_for_ticker(
            ticker_info["ticker"],
            ticker_info["name"],
            ticker_info.get("is_forex", False),
        )
        self.market_result_label.config(text=range_text)

        data = self.data_fetcher.download_data(
            ticker_info["ticker"], ticker_info["name"]
        )
        if ticker_info.get("is_forex", False):
            usdinr = self.data_fetcher.get_usdinr_rate()
            data = data * usdinr

        if data is not None:
            self.plot_candlestick(data, ticker_info["name"])

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

    def calculate_for_multiple_spots(self):
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

            spot_prices = self.generate_dynamic_spot_prices(spot)
            results = []

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

            for s in spot_prices:
                result = self.calculator.calculate(
                    s, strike, expiry_date, option_type, "price", price, volatility
                )
                results.append(f"{s}\t: {result}")

            self.result_label.config(text="\n".join(results))

    def generate_dynamic_spot_prices(self, spot):
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

    def plot_candlestick(self, data, ticker_name):
        # Clear the existing chart, if any
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        # Calculate 30-day and 200-day EMA
        data["EMA_30"] = data["Adj Close"].ewm(span=30, adjust=False).mean()
        data["EMA_200"] = data["Adj Close"].ewm(span=200, adjust=False).mean()

        # Prepare data for hollow candlestick chart
        data = data[-100:]  # Take the last 100 rows

        # Get the last traded price (LTP) from the latest data point
        ltp = data["Adj Close"].iloc[-1]

        # Create figure and axes for custom plotting
        fig, ax = mpf.plot(
            data,
            type="hollow_candle",  # Change to hollow candles
            style="charles",
            title=ticker_name,
            ylabel="Price",
            addplot=[
                mpf.make_addplot(data["EMA_30"], color="blue", label="30 EMA"),
                mpf.make_addplot(data["EMA_200"], color="red", label="200 EMA"),
            ],
            returnfig=True,
        )

        # Set the legend (EMA labels) to be centered below the chart
        ax[0].legend(
            ["30 EMA", "200 EMA"],
            loc="upper center",
            bbox_to_anchor=(0.5, -0.15),
            ncol=2,
            frameon=False,
        )

        # Annotate the chart with the LTP (Last Traded Price)
        ax[0].text(
            0.5,
            0.95,
            f"{ltp:.2f}",
            horizontalalignment="right",
            verticalalignment="top",
            transform=ax[0].transAxes,
            fontsize=11,
        )

        # Display the chart in the right side of the Market Data tab
        self.canvas = FigureCanvasTkAgg(fig, master=self.market_data_tab)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=1, rowspan=5, padx=20, pady=10)

        # Close the figure to avoid too many open figures
        plt.close(fig)
