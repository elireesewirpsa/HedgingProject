# -*- coding: utf-8 -*-
"""
Created on Fri Jul 19 10:01:35 2024

@author: Eli Reese-Wirpsa

to do
- finish delta-gamma-vega hedge
- break up components into seperate classes to org





Main driver of the dynamic hedging project

a) input option 1

b) calculates the number of shares for the delta-hedge for option 1

c) calc
"""

from greeks import delta_calc, gamma_calc, vega_calc
from call import BSM, calc_D_one, calc_D_two
from put import BSM_put
import sympy as sp

class Option:
    """
    A class to represent an option and calculate its Greek values.

    Attributes
    ----------
    option_type : str
        The type of the option, either 'call' or 'put'.
    strike : float
        The strike price of the option.
    stock_price : float
        The current price of the underlying stock.
    rf : float
        The risk-free interest rate.
    vol : float
        The volatility of the underlying stock.
    t : float
        The time to maturity of the option, in years.
    qty : int
        The quantity of options. Positive for buy, negative for sell.
    delta : float
        The delta of the option, calculated using the Black-Scholes model.
    gamma : float
        The gamma of the option, calculated using the Black-Scholes model.
    vega : float
        The vega of the option, calculated using the Black-Scholes model.
    market_price : float
        The actual market price of the option.

    Methods
    -------
    __init__(self, option_type, strike, stock_price, rf, vol, t, qty, trans=None, market_price=0.0):
        Constructs all the necessary attributes for the Option object.

    bsm_price(self):
        Calculates the Black-Scholes-Merton (BSM) price of the option.
    """
    def __init__(self, option_type, strike, stock_price, rf, vol, t, qty, trans=None, market_price=0.0):
        self.option_type = option_type
        self.strike = strike
        self.stock_price = stock_price
        self.rf = rf
        self.vol = vol
        self.t = t
        if trans is not None:
            self.qty = qty if trans.lower() == 'buy' else -qty
        else:
            self.qty = qty  # Default case if trans is not provided
        self.market_price = market_price
        
        self.delta = delta_calc(option_type, strike, stock_price, rf, vol, t)
        self.gamma = gamma_calc(strike, stock_price, rf, vol, t)
        self.vega = vega_calc(strike, stock_price, rf, vol, t)
        
    def bsm_price(self):
        d_one = calc_D_one(self.strike, self.stock_price, self.rf, self.vol, self.t)
        d_two = calc_D_two(d_one, self.vol, self.t)
        if self.option_type.lower() == 'put':
            return BSM_put(d_one, d_two, self.stock_price, self.strike, self.rf, self.t)
        else:
            return BSM(d_one, d_two, self.stock_price, self.strike, self.rf, self.t)

class Hedge:
    @staticmethod
    def delta_hedge(option):
        x = sp.symbols('x')
        equation = sp.Eq(option.qty * option.delta + x, 0)
        solution = sp.solve(equation, x)

        if isinstance(solution, list) and len(solution) == 1:
            n_s = float(solution[0])
        else:
            n_s = [float(sol) for sol in solution]

        return round(n_s, 0)
    
    @staticmethod
    def delta_vega_gamma_hedge(option1, option2, option3):
        y, z = sp.symbols('y z')
        equations = (
            sp.Eq(option1.qty * option1.delta + y * option2.delta + z * option3.delta, 0),
            sp.Eq(option1.qty * option1.vega + y * option2.vega + z * option3.vega, 0),
            sp.Eq(option1.qty * option1.gamma + y * option2.gamma + z * option3.gamma, 0)
        )
        solution = sp.solve(equations, (y, z))
        
        if isinstance(solution, dict) and y in solution and z in solution:
            qty2 = float(solution[y])
            qty3 = float(solution[z])
        else:
            qty2 = 0  # or handle it as needed, e.g., raise an exception or set to a default value
            qty3 = 0  # or handle it as needed, e.g., raise an exception or set to a default value

        return round(qty2, 0), round(qty3, 0)
    
    @staticmethod
    def adjust_delta_hedge(total_delta):
        x = sp.symbols('x')
        equation = sp.Eq(total_delta + x, 0)
        solution = sp.solve(equation, x)

        if isinstance(solution, list) and len(solution) == 1:
            n_s = float(solution[0])
        else:
            n_s = [float(sol) for sol in solution]

        return round(n_s, 0)

def get_user_input():
    stock_price = float(input("What is the current price of the stock? "))
    option_type = input("Call or put option? ")
    strike = float(input("What is the strike of the option? "))
    rf = .02  # Assuming a constant risk-free rate of 2%
    t = float(input("Time to maturity (enter as decimal)? "))
    vol = float(input("What is the volatility of the option (decimal)? "))
    trans = input("Buy or sell option? ")
    qty = int(input("How many options are you buying or selling? "))
    market_price = float(input("What is the current market price of the option? "))

    return stock_price, option_type, strike, rf, t, vol, trans, qty, market_price

def main():
    stock_price, option_type, strike, rf, t, vol, trans, qty, market_price = get_user_input()
    option1 = Option(option_type, strike, stock_price, rf, vol, t, qty, trans, market_price)
    
    print(f"Delta: {option1.delta}")
    print(f"Gamma: {option1.gamma}")
    print(f"Vega: {option1.vega}")
    
    n_s = Hedge.delta_hedge(option1)
    print(f"Number of shares for delta hedge: {n_s}")
    
    bsm_price = option1.bsm_price()
    print(f"BSM Price: {bsm_price}")

    current_basis = option1.market_price * abs(option1.qty)
    shares_hedged_value = option1.market_price * abs(n_s)

    print(f"Current basis: ${current_basis}")
    
    print("Enter details for the second option for gamma hedge:")
    option_type2 = input("Call or put option? ")
    strike2 = float(input("What is the strike of the option? "))
    vol2 = float(input("What is the volatility of the option (decimal)? "))
    t2 = float(input("Time to maturity (enter as decimal)? "))  # Allow different time to maturity
    rf2 = rf  # Using the same risk-free rate as the first option
    market_price2 = float(input("What is the actual market price of the option? "))
    option2 = Option(option_type2, strike2, stock_price, rf2, vol2, t2, 1, market_price=market_price2)  # Setting qty to 1 and omitting trans

    print("Enter details for the third option for vega hedge:")
    option_type3 = input("Call or put option? ")
    strike3 = float(input("What is the strike of the option? "))
    vol3 = float(input("What is the volatility of the option (decimal)? "))
    t3 = float(input("Time to maturity (enter as decimal)? "))  # Allow different time to maturity
    rf3 = rf  # Using the same risk-free rate as the first option
    market_price3 = float(input("What is the actual market price of the option? "))
    option3 = Option(option_type3, strike3, stock_price, rf3, vol3, t3, 1, market_price=market_price3)  # Setting qty to 1 and omitting trans

    qty2, qty3 = Hedge.delta_vega_gamma_hedge(option1, option2, option3)
    print(f"Quantity of second option for gamma hedge: {qty2}")
    print(f"Quantity of third option for vega hedge: {qty3}")

    # Adjust delta hedge after gamma and vega hedging
    total_delta = option1.qty * option1.delta + qty2 * option2.delta + qty3 * option3.delta
    n_s_adj = Hedge.adjust_delta_hedge(total_delta)

    print(f"Adjusted number of shares for delta hedge: {n_s_adj}")

if __name__ == "__main__":
    main()




    