# -*- coding: utf-8 -*-
"""
Created on Thu Jul 18 15:58:06 2024

@author: Eli Reese-Wirpsa
"""

import math
from scipy.stats import norm
from call import calc_D_one, calc_D_two

def BSM(d_one, d_two, stock_Price, strike, rf, t):
    C = stock_Price * norm.cdf(-d_one) - strike * math.exp(-(rf * t)) * norm.cdf(-d_two)
    return -C



stock_Price = 20
strike = 25
t = 2
vol = 0.15
rf = 0.03

d_one = calc_D_one(strike, stock_Price, rf, vol, t)
d_two = calc_D_two(d_one, vol, t)

option = BSM(d_one, d_two, stock_Price, strike, rf, t)

print(option)

