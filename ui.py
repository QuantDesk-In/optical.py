import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplfinance as mpf
from calculations import OptionCalculator
from data_fetch import DataFetcher
from utils import toggle_inputs, validate_inputs
import math


class OptionCalculatorUI:
    def __init__(self, root):
        self.root = root
        self.calculator = OptionCalculator()
        self.data_fetcher = DataFetcher()
        self.canvas = None  # This will hold the chart canvas

        # Setup the Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky="nsew")

        # Create frames for each tab
        self.option_tab = ttk.Frame(self.notebook)
        self.market_data_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.option_tab, text="Option Calculator")
        self.notebook.add(self.market_data_tab, text="Market Data")

        # Setup UI for both tabs
        self.setup_option_calculator_ui()
        self.setup_market_data_ui()

        # Configure grid for dynamic resizing
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

    def setup_option_calculator_ui(self):
        # Create frames for grouping elements inside the Option Calculator tab
        input_frame = ttk.LabelFrame(self.option_tab, text="Input Data")
        input_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        calc_settings_frame = ttk.LabelFrame(
            self.option_tab, text="Calculation Settings"
        )
        calc_settings_frame.grid(
            row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=10
        )

        action_frame = ttk.Frame(self.option_tab)
        action_frame.grid(row=8, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        # Spot Price
        ttk.Label(input_frame, text="Spot Price:").grid(
            row=0, column=0, sticky="w", padx=10, pady=10
        )
        self.spot_entry = ttk.Entry(input_frame)
        self.spot_entry.grid(row=0, column=1, padx=10, pady=10)

        # Strike Price
        ttk.Label(input_frame, text="Strike Price:").grid(
            row=1, column=0, sticky="w", padx=10, pady=10
        )
        self.strike_entry = ttk.Entry(input_frame)
        self.strike_entry.grid(row=1, column=1, padx=10, pady=10)

        # Expiry Date
        ttk.Label(input_frame, text="Expiry Date (YYYY-MM-DD):").grid(
            row=2, column=0, sticky="w", padx=10, pady=10
        )
        self.expiry_entry = ttk.Entry(input_frame)
        self.expiry_entry.grid(row=2, column=1, padx=10, pady=10)

        # Option Type Dropdown
        ttk.Label(input_frame, text="Option Type (CALL/PUT):").grid(
            row=3, column=0, sticky="w", padx=10, pady=10
        )
        self.option_type_var = tk.StringVar()
        option_type_menu = ttk.Combobox(
            input_frame,
            textvariable=self.option_type_var,
            state="readonly",
            values=["CALL", "PUT"],
        )
        option_type_menu.grid(row=3, column=1, padx=10, pady=10)
        option_type_menu.current(0)

        # Calculation Mode
        self.calculation_mode = tk.StringVar(value="volatility")
        ttk.Radiobutton(
            calc_settings_frame,
            text="Calculate Implied Volatility",
            variable=self.calculation_mode,
            value="volatility",
            command=self.toggle_inputs,
        ).grid(row=4, column=0, sticky="w", padx=10, pady=10)
        ttk.Radiobutton(
            calc_settings_frame,
            text="Calculate Option Price",
            variable=self.calculation_mode,
            value="price",
            command=self.toggle_inputs,
        ).grid(row=5, column=0, sticky="w", padx=10, pady=10)

        # Option Price
        ttk.Label(calc_settings_frame, text="Option Price:").grid(
            row=6, column=0, sticky="w", padx=10, pady=10
        )
        self.price_entry = ttk.Entry(calc_settings_frame)
        self.price_entry.grid(row=6, column=1, padx=10, pady=10)

        # Implied Volatility
        ttk.Label(calc_settings_frame, text="Implied Volatility:").grid(
            row=7, column=0, sticky="w", padx=10, pady=10
        )
        self.volatility_entry = ttk.Entry(calc_settings_frame)
        self.volatility_entry.grid(row=7, column=1, padx=10, pady=10)
        self.volatility_entry.config(state="disabled")

        # Buttons for Actions
        ttk.Button(
            action_frame, text="Calculate Option", command=self.calculate_option
        ).grid(row=8, column=0, columnspan=2, pady=10)

        ttk.Button(
            action_frame,
            text="Multiple Spot Prices",
            command=self.calculate_for_multiple_spots,
        ).grid(row=9, column=0, columnspan=2, pady=10)

        # Result Label
        self.result_label = ttk.Label(action_frame, text="")
        self.result_label.grid(row=13, column=0, columnspan=2, pady=10)

    def setup_market_data_ui(self):
        # Buttons for Market Data (Nifty, Midcap, Crude, etc.)
        button_frame = ttk.Frame(self.market_data_tab)
        button_frame.grid(row=0, column=0, sticky="n", padx=10, pady=10)

        ttk.Button(
            button_frame, text="Nifty Ranges", command=self.nifty_operations
        ).grid(row=1, column=0, padx=10, pady=10)
        ttk.Button(
            button_frame, text="Midcap Ranges", command=self.midcap_operations
        ).grid(row=2, column=0, padx=10, pady=10)
        ttk.Button(
            button_frame, text="Banknifty Ranges", command=self.banknifty_operations
        ).grid(row=3, column=0, padx=10, pady=10)
        ttk.Button(
            button_frame, text="Crude Oil Ranges", command=self.crude_operations
        ).grid(row=4, column=0, padx=10, pady=10)

        # Result Label for Market Data
        self.market_result_label = ttk.Label(button_frame, text="")
        self.market_result_label.grid(row=5, column=0, pady=10)

        # Set up grid layout for chart display on the right
        self.market_data_tab.grid_columnconfigure(1, weight=1)
        self.market_data_tab.grid_rowconfigure(0, weight=1)

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
            spot, strike, expiry_date, price, volatility = (
                inputs[0],
                inputs[1],
                inputs[2],
                inputs[3],
                inputs[4],
            )
            option_type = self.option_type_var.get()

            # Generate dynamic spot prices based on the input spot
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
                    s,
                    strike,
                    expiry_date,
                    option_type,
                    "price",
                    price,
                    volatility,
                )
                results.append(f"{s}\t: {result}")

            self.result_label.config(text="\n".join(results))

    def generate_dynamic_spot_prices(self, spot):
        # Determine the rounding and step size based on the spot price magnitude
        step = 50  # Default step size
        if spot >= 10000:
            step = 500
        elif spot >= 1000:
            step = 100
        elif spot >= 500:
            step = 50
        elif spot >= 100:
            step = 10
        else:
            step = 5

        # Round the spot price to the nearest multiple of the step
        rounded_spot = round(spot / step) * step

        # Generate the nearby spot prices
        spot_prices = [
            rounded_spot - 2 * step,
            rounded_spot - step,
            rounded_spot,
            rounded_spot + step,
            rounded_spot + 2 * step,
        ]

        return spot_prices

    def nifty_operations(self):
        self.market_result_label.config(text="Fetching Nifty data...")  # Feedback
        self.root.update()  # Force immediate update for visual feedback
        range_text = self.data_fetcher.calculate_std_for_ticker("^NSEI", "Nifty")
        self.market_result_label.config(text=range_text)
        data = self.data_fetcher.download_data("^NSEI", "Nifty")
        if data is not None:
            self.plot_candlestick(data, "Nifty")

    def crude_operations(self):
        self.market_result_label.config(text="Fetching Crude Oil data...")  # Feedback
        self.root.update()  # Force immediate update for visual feedback
        range_text = self.data_fetcher.calculate_std_for_ticker(
            "CL=F", "Crude Oil", is_forex=True
        )
        self.market_result_label.config(text=range_text)
        data = self.data_fetcher.download_data("CL=F", "Crude Oil")
        usdinr = self.data_fetcher.get_usdinr_rate()
        data = data * usdinr
        if data is not None:
            self.plot_candlestick(data, "Crude Oil")

    def midcap_operations(self):
        self.market_result_label.config(text="Fetching Midcap data...")  # Feedback
        self.root.update()  # Force immediate update for visual feedback
        range_text = self.data_fetcher.calculate_std_for_ticker(
            "^NSEMDCP50", "Nifty Midcap 50", is_forex=False
        )
        self.market_result_label.config(text=range_text)
        data = self.data_fetcher.download_data("^NSEMDCP50", "Nifty Midcap 50")

        if data is not None:
            self.plot_candlestick(data, "Nifty Midcap 50")

    def banknifty_operations(self):
        self.market_result_label.config(text="Fetching Banknifty data...")  # Feedback
        self.root.update()  # Force immediate update for visual feedback
        range_text = self.data_fetcher.calculate_std_for_ticker(
            "^NSEBANK", "Banknifty", is_forex=False
        )
        self.market_result_label.config(text=range_text)
        data = self.data_fetcher.download_data("^NSEBANK", "Banknifty")

        if data is not None:
            self.plot_candlestick(data, "Bank Nifty")

    def plot_candlestick(self, data, ticker_name):
        # Clear the existing chart, if any
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        # Calculate 30-day and 200-day EMA
        data["EMA_30"] = data["Adj Close"].ewm(span=30, adjust=False).mean()
        data["EMA_200"] = data["Adj Close"].ewm(span=200, adjust=False).mean()

        # Prepare data for candlestick chart
        data = data[-100:]  # Take the last 100 rows

        # Get the last traded price (LTP) from the latest data point
        ltp = data["Adj Close"].iloc[-1]

        # Create figure and axes for custom plotting
        fig, ax = mpf.plot(
            data,
            type="candle",
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
