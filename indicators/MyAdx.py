from indicators.rma import rma
from indicators.utils import true_range
import numpy as np
import pandas as pd

def dirmov(high, low, close, len):
    up = high - high.shift(1)
    down = low.shift(1) - low
    tr = true_range(high, low, close)
    truerange = rma(tr, len)
    plus =  100 * rma(pd.Series(np.where((up > down) & (up > 0), up, 0)), len) / truerange
    minus = 100 * rma(pd.Series(np.where((down > up) & (down > 0), down, 0)), len) / truerange
    return (plus, minus)


def adx(high, low, close, LWdilength, LWadxlength):
    tuple = dirmov(high, low, close, LWdilength)
    plus = tuple[0]
    minus = tuple[1]
    sum = plus + minus
    adx = 100 * rma(abs(plus - minus) / pd.Series(np.where(sum == 0, 1, sum)), LWadxlength)
    return adx


def ADXStrength(high, low, close):
    ADX = adx(high, low, close, 14, 14)
    return (ADX - 15) * 2.5
