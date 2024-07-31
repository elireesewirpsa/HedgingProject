# -*- coding: utf-8 -*-

"""
Created on Fri Jul 19 10:01:35 2024

@author: Eli Reese-Wirpsa

Main driver of the dynamic hedging project

Steps:
1. Calculate transaction to delta hedge short call position
2. Find gamma of current portfolio
3. Introduce second option
4. Find how many second options are needed to be delta-gamma neutral
5. Find the amount of shares needed to be delta-gamma neutral
6. Find value of portfolio using the options market prices
7. Find vega of delta-gamma neutral portfolio
8. Use a system of equations to solve for new number of options 2 and 3 for gamma-vega neutrality
9. Adjust number of shares for delta hedge to be delta neutral
10. Find value of portfolio using market prices
"""

from greeks import delta_calc, gamma_calc, vega_calc
from call import BSM, calc_D_one, calc_D_two
from put import BSM_put
import sympy as sp

class Option:
    """
    A class to represent an option and calculate its Greek values.
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
            self.qty = qty
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
        return float(solution[0]) if solution else 0
    
    @staticmethod
    def gamma_hedge(option1, option2):
        y = sp.symbols('y')
        equation = sp.Eq(option1.qty * option1.gamma + y * option2.gamma, 0)
        solution = sp.solve(equation, y)
        return float(solution[0]) if solution else 0

    @staticmethod
    def delta_gamma_hedge(option1, n_s, option2_qty, option2):
        x = sp.symbols('x')
        equation = sp.Eq(option1.qty * option1.delta + n_s + option2_qty * option2.delta + x, 0)
        solution = sp.solve(equation, x)
        return float(solution[0]) if solution else 0
    
    @staticmethod
    def delta_vega_gamma_hedge(option1, option2, option3):
        y, z = sp.symbols('y z')
        equations = (
            sp.Eq(option1.qty * option1.gamma + y * option2.gamma + z * option3.gamma, 0),
            sp.Eq(option1.qty * option1.vega + y * option2.vega + z * option3.vega, 0)
        )
        solution = sp.solve(equations, (y, z))
        
        qty2 = float(solution[y]) if solution and y in solution else 0
        qty3 = float(solution[z]) if solution and z in solution else 0

        return qty2, qty3
    
    @staticmethod
    def adjust_delta_hedge(option1, option2_qty, option2, option3_qty, option3, current_shares):
        x = sp.symbols('x')
        equation = sp.Eq(option1.qty * option1.delta + option2_qty * option2.delta + option3_qty * option3.delta + current_shares + x, 0)
        solution = sp.solve(equation, x)
        return float(solution[0]) if solution else 0

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
    # Step 1: Get initial option details
    stock_price, option_type, strike, rf, t, vol, trans, qty, market_price = get_user_input()
    option1 = Option(option_type, strike, stock_price, rf, vol, t, qty, trans, market_price)
    
    print(f"Delta: {option1.delta}")
    print(f"Gamma: {option1.gamma}")
    print(f"Vega: {option1.vega}")
    
    # Step 1: Initial delta hedge
    n_s = Hedge.delta_hedge(option1)
    n_s = round(n_s,0)
    print(f"Number of shares for initial delta hedge: {n_s}")
    
    # Step 2: Calculate the gamma of the current portfolio
    gamma_portfolio = option1.qty * option1.gamma
    print(f"Gamma of the portfolio: {gamma_portfolio}")
    
    # Step 3: Input details for the second option for delta-gamma hedge
    print("Enter details for the second option for gamma hedge:")
    stock_price2 = stock_price  # Using the same stock price as the first option
    option_type2 = input("Call or put option? ")
    strike2 = float(input("What is the strike of the option? "))
    vol2 = float(input("What is the volatility of the option (decimal)? "))
    t2 = float(input("Time to maturity (enter as decimal)? "))  # Allow different time to maturity
    rf2 = rf  # Using the same risk-free rate as the first option
    market_price2 = float(input("What is the actual market price of the option? "))
    option2 = Option(option_type2, strike2, stock_price2, rf2, vol2, t2, 1, market_price=market_price2)

    # Step 4: Find the quantity of the second option needed for delta-gamma neutrality
    option2_qty = Hedge.gamma_hedge(option1, option2)
    print(f"Quantity of second option for gamma hedge: {option2_qty}")

    # Step 5: Adjust delta hedge after gamma hedging
    n_s_adj = Hedge.delta_gamma_hedge(option1, n_s, option2_qty, option2)
    n_s_adj = round(n_s + n_s_adj,0)
    print(f"Adjusted number of shares for delta-gamma hedge: {n_s_adj}")
    
    # Step 6: Calculate the value of the portfolio using the market prices of the options
    value_portfolio = option1.qty * option1.market_price + option2_qty * option2.market_price + n_s * stock_price
    print(f"Value of the portfolio: ${value_portfolio}")

    # Step 7: Calculate the vega of the delta-gamma neutral portfolio
    vega_portfolio = option1.qty * option1.vega + option2_qty * option2.vega
    print(f"Vega of the delta-gamma neutral portfolio: {vega_portfolio}")

    # Step 8: Input details for the third option for vega hedge
    print("Enter details for the third option for vega hedge:")
    stock_price3 = stock_price  # Using the same stock price as the first option
    option_type3 = input("Call or put option? ")
    strike3 = float(input("What is the strike of the option? "))
    vol3 = float(input("What is the volatility of the option (decimal)? "))
    t3 = float(input("Time to maturity (enter as decimal)? "))  # Allow different time to maturity
    rf3 = rf  # Using the same risk-free rate as the first option
    market_price3 = float(input("What is the actual market price of the option? "))
    option3 = Option(option_type3, strike3, stock_price3, rf3, vol3, t3, 1, market_price=market_price3)

    # Step 9: Use a system of equations to solve for new number of options 2 and 3 for gamma-vega neutrality
    option2_qty_new, option3_qty_new = Hedge.delta_vega_gamma_hedge(option1, option2, option3)
    print(f"New quantity of second option for gamma-vega hedge: {option2_qty_new}")
    print(f"Quantity of third option for vega hedge: {option3_qty_new}")

    # Step 10: Adjust delta hedge after gamma-vega hedging
    n_s_final = Hedge.adjust_delta_hedge(option1, option2_qty_new, option2, option3_qty_new, option3, n_s)
    n_s_final = round(n_s + n_s_final,0)
    print(f"Final adjusted number of shares for delta-gamma-vega hedge: {n_s_final}")

    # Step 11: Calculate the final value of the portfolio using market prices
    final_value_portfolio = abs(option1.qty) * option1.market_price + abs(option2_qty_new) * option2.market_price + abs(option3_qty_new) * option3.market_price
    print(f"Final value of the portfolio: ${final_value_portfolio}")

if __name__ == "__main__":
    main()





    