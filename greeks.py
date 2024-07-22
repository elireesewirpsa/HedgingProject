# -*- coding: utf-8 -*-
"""
Created on Thu Jul 18 16:11:43 2024

@author: Eli Reese-Wirpsa
"""
from call import calc_D_one
from scipy.stats import norm
import math

def delta_calc(optionT, strike, stock_Price, rf, vol, t ):
    delta = calc_D_one(strike, stock_Price, rf, vol, t)
    if optionT == "Call":
        return norm.cdf(delta)
    else:
        return norm.cdf(delta) - 1
    
        
def gamma_calc(strike, stock_Price, rf, vol, t ):
    d_one = calc_D_one(strike, stock_Price, rf, vol, t)
    gamma = math.exp(-d_one**2 / 2) / (stock_Price * vol * math.sqrt(2 * math.pi * t))
    
    return gamma

def vega_calc(strike, stock_Price, rf, vol, t):
    d_one = calc_D_one(strike, stock_Price, rf, vol, t)
    vega = stock_Price * norm.pdf(d_one) * math.sqrt(t)
    return vega


