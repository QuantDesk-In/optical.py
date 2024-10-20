from py_vollib.black_scholes import black_scholes as bsm
from py_vollib.black_scholes.implied_volatility import implied_volatility

from utils import calculate_time_to_expiration


class OptionCalculator:
    def calculate(
        self, spot, strike, expiry_date, option_type, mode, price=None, volatility=None
    ):
        time_to_expiration = calculate_time_to_expiration(expiry_date)
        r = 0.07  # Risk-free rate

        try:
            if mode == "volatility":
                implied_vol = implied_volatility(
                    price, spot, strike, time_to_expiration, r, option_type.lower()[0]
                )
                return f"{implied_vol:.4f}"
            else:
                option_price = bsm(
                    option_type.lower()[0],
                    spot,
                    strike,
                    time_to_expiration,
                    r,
                    volatility,
                )
                return f"{option_price:.2f}"
        except Exception as e:
            return f"Error: {str(e)}"
