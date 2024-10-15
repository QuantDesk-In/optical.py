import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplfinance as mpf
from calculations import OptionCalculator
from data_fetch import DataFetcher
from utils import toggle_inputs, validate_inputs
from tkinter import messagebox


class OptionCalculatorUI:
    def __init__(self, root):
        self.root = root
        self.calculator = OptionCalculator()
        self.data_fetcher = DataFetcher()
        self.canvas = None  # This will hold the chart canvas

        self.setup_ui()

    def setup_ui(self):
        # Use notebook (tabs) for better layout organization
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, columnspan=3, sticky="nsew")

        # Tabs
        self.tab_input = ttk.Frame(self.notebook)
        self.tab_data_operations = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_input, text="Option Calculator")
        self.notebook.add(self.tab_data_operations, text="Market Data Operations")

        self.setup_input_tab()
        self.setup_data_operations_tab()

        # Result display
        self.result_frame = ttk.Frame(self.root)
        self.result_frame.grid(
            row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=10
        )
        self.result_label = tk.Text(self.result_frame, height=10, wrap="word")
        self.result_label.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.result_label.config(state=tk.DISABLED)

        # Responsive layout
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

    def setup_input_tab(self):
        # Input Frame (organized with better padding and structure)
        input_frame = ttk.LabelFrame(self.tab_input, text="Input Data")
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Spot Price
        ttk.Label(input_frame, text="Spot Price:").grid(
            row=0, column=0, sticky="w", padx=10, pady=5
        )
        self.spot_entry = ttk.Entry(input_frame)
        self.spot_entry.grid(row=0, column=1, padx=10, pady=5)

        # Strike Price
        ttk.Label(input_frame, text="Strike Price:").grid(
            row=1, column=0, sticky="w", padx=10, pady=5
        )
        self.strike_entry = ttk.Entry(input_frame)
        self.strike_entry.grid(row=1, column=1, padx=10, pady=5)

        # Expiry Date with DatePicker
        ttk.Label(input_frame, text="Expiry Date:").grid(
            row=2, column=0, sticky="w", padx=10, pady=5
        )

        # Safely handle DateEntry to avoid KeyError on focus loss
        try:
            self.expiry_entry = DateEntry(input_frame, date_pattern="yyyy-mm-dd")
            self.expiry_entry.grid(row=2, column=1, padx=10, pady=5)
        except Exception as e:
            messagebox.showerror("Error", f"Error creating DateEntry: {str(e)}")
            # Fallback to simple Entry widget if DateEntry fails
            self.expiry_entry = ttk.Entry(input_frame)
            self.expiry_entry.grid(row=2, column=1, padx=10, pady=5)

        # Option Type Dropdown
        ttk.Label(input_frame, text="Option Type:").grid(
            row=3, column=0, sticky="w", padx=10, pady=5
        )
        self.option_type_var = tk.StringVar()
        self.option_type_menu = ttk.Combobox(
            input_frame,
            textvariable=self.option_type_var,
            state="readonly",
            values=["CALL", "PUT"],
        )
        self.option_type_menu.grid(row=3, column=1, padx=10, pady=5)
        self.option_type_menu.current(0)

        self.option_type_var = tk.StringVar()
        self.option_type_menu = ttk.Combobox(
            input_frame,
            textvariable=self.option_type_var,
            state="readonly",
            values=["CALL", "PUT"],
        )
        self.option_type_menu.grid(row=3, column=1, padx=10, pady=5)
        self.option_type_menu.current(0)

        # Calculation Mode (Implied Volatility or Option Price)
        calc_settings_frame = ttk.LabelFrame(
            self.tab_input, text="Calculation Settings"
        )
        calc_settings_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.calculation_mode = tk.StringVar(value="volatility")
        ttk.Radiobutton(
            calc_settings_frame,
            text="Calculate Implied Volatility",
            variable=self.calculation_mode,
            value="volatility",
            command=self.toggle_inputs,
        ).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        ttk.Radiobutton(
            calc_settings_frame,
            text="Calculate Option Price",
            variable=self.calculation_mode,
            value="price",
            command=self.toggle_inputs,
        ).grid(row=1, column=0, sticky="w", padx=10, pady=5)

        # Option Price and Volatility
        ttk.Label(calc_settings_frame, text="Option Price:").grid(
            row=2, column=0, sticky="w", padx=10, pady=5
        )
        self.price_entry = ttk.Entry(calc_settings_frame)
        self.price_entry.grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(calc_settings_frame, text="Implied Volatility:").grid(
            row=3, column=0, sticky="w", padx=10, pady=5
        )
        self.volatility_entry = ttk.Entry(calc_settings_frame)
        self.volatility_entry.grid(row=3, column=1, padx=10, pady=5)
        self.volatility_entry.config(state="disabled")

        # Action Buttons with better layout
        action_frame = ttk.Frame(self.tab_input)
        action_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        ttk.Button(
            action_frame, text="Calculate Option", command=self.calculate_option
        ).grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        ttk.Button(
            action_frame,
            text="Calculate for Multiple Spots",
            command=self.calculate_for_multiple_spots,
        ).grid(row=1, column=0, padx=10, pady=5, sticky="ew")

    def setup_data_operations_tab(self):
        # Buttons for market data operations
        action_frame = ttk.LabelFrame(
            self.tab_data_operations, text="Market Data Operations"
        )
        action_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ttk.Button(
            action_frame, text="Nifty Ranges", command=self.nifty_operations
        ).grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        ttk.Button(
            action_frame, text="Crude Oil Ranges", command=self.crude_operations
        ).grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        ttk.Button(
            action_frame, text="Midcap Ranges", command=self.midcap_operations
        ).grid(row=2, column=0, padx=10, pady=5, sticky="ew")

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
            self.display_result(result)

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
                results.append(f"Spot {s}: {result}")

            self.display_result("\n".join(results))

    def nifty_operations(self):
        self.display_result("Fetching Nifty data...")
        range_text = self.data_fetcher.calculate_std_for_ticker("^NSEI", "Nifty")
        self.display_result(range_text)
        data = self.data_fetcher.download_data("^NSEI", "Nifty")
        if data is not None:
            self.plot_candlestick(data, "Nifty")

    def crude_operations(self):
        self.display_result("Fetching Crude Oil data...")
        range_text = self.data_fetcher.calculate_std_for_ticker(
            "CL=F", "Crude Oil", is_forex=True
        )
        self.display_result(range_text)
        data = self.data_fetcher.download_data("CL=F", "Crude Oil")
        usdinr = self.data_fetcher.get_usdinr_rate()
        data = data * usdinr
        if data is not None:
            self.plot_candlestick(data, "Crude Oil")

    def midcap_operations(self):
        self.display_result("Fetching Midcap data...")
        range_text = self.data_fetcher.calculate_std_for_ticker(
            "^NSEMDCP50", "Nifty Midcap 50", is_forex=False
        )
        self.display_result(range_text)
        data = self.data_fetcher.download_data("^NSEMDCP50", "Nifty Midcap 50")
        if data is not None:
            self.plot_candlestick(data, "Nifty Midcap 50")

    def plot_candlestick(self, data, ticker_name):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        data["EMA_30"] = data["Adj Close"].ewm(span=30, adjust=False).mean()
        data["EMA_200"] = data["Adj Close"].ewm(span=200, adjust=False).mean()
        data = data[-100:]

        fig, ax = mpf.plot(
            data,
            type="candle",
            style="charles",
            title=ticker_name,
            ylabel="Price",
            addplot=[
                mpf.make_addplot(data["EMA_30"], color="blue"),
                mpf.make_addplot(data["EMA_200"], color="red"),
            ],
            returnfig=True,
        )

        ax[0].legend(
            ["30 EMA", "200 EMA"],
            loc="upper center",
            bbox_to_anchor=(0.5, -0.15),
            ncol=2,
            frameon=False,
        )
        self.canvas = FigureCanvasTkAgg(fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=2, rowspan=20, padx=20, pady=10)

    def generate_dynamic_spot_prices(self, spot):
        step = 50 if spot >= 500 else 5
        rounded_spot = round(spot / step) * step
        return [
            rounded_spot - 2 * step,
            rounded_spot - step,
            rounded_spot,
            rounded_spot + step,
            rounded_spot + 2 * step,
        ]

    def display_result(self, text):
        self.result_label.config(state=tk.NORMAL)
        self.result_label.delete(1.0, tk.END)
        self.result_label.insert(tk.END, text)
        self.result_label.config(state=tk.DISABLED)
