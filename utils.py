from datetime import datetime
from tkinter import messagebox


def validate_inputs(
    spot_entry,
    strike_entry,
    expiry_entry,
    price_entry,
    volatility_entry,
    calculation_mode,
):
    try:
        spot = float(spot_entry.get())
        strike = float(strike_entry.get())
        expiry_date = expiry_entry.get()

        if calculation_mode.get() == "volatility":
            price = float(price_entry.get())
            return spot, strike, expiry_date, price, None
        else:
            volatility = float(volatility_entry.get())
            return spot, strike, expiry_date, None, volatility

    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numbers.")
        return None


def calculate_time_to_expiration(expiry_date):
    today = datetime.today()
    expiry = datetime.strptime(expiry_date, "%Y-%m-%d")
    return (expiry - today).days / 365.0


def toggle_inputs(calculation_mode, price_entry, volatility_entry):
    if calculation_mode.get() == "volatility":
        price_entry.config(state="normal")
        volatility_entry.config(state="disabled")
    else:
        price_entry.config(state="disabled")
        volatility_entry.config(state="normal")
