# -*- coding: utf-8 -*-
"""
Created on Fri Jul 19 10:01:35 2024

@author: Eli Reese-Wirpsa
"""

from greeks import delta_calc, gamma_calc, vega_calc

## setting up inputs, will change to pull stock price from yf
stock_Price = float(input("What is the current price of the stock"))
optionT  = input("Call or put option")
strike = float(input("What is the strike of the option"))
rf = .02
t = float(input("time to maturirty (enter as decimal)"))
vol = float(input("What is the vol of option (decimal"))

## calculate 3 greeks for option

delta_1 = delta_calc(optionT, strike, stock_Price, rf, vol, t)
print(delta_1)

gamma_1 = gamma_calc(strike, stock_Price, rf, vol, t)
print(gamma_1)

vega_1 = vega_calc(strike, stock_Price, rf, vol, t)
print(vega_1)

