
from sys import float_info as sflt
import math
import numpy as np
import pandas as pd
from pandas import DataFrame


def get_offset(x: int):
    """Returns an int, otherwise defaults to zero."""
    return int(x) if x else 0


def verify_series(series: pd.Series):
    """If a Pandas Series return it."""
    if series is not None and isinstance(series, pd.core.series.Series):
        return series

def get_drift(x:int):
    """Returns an int if not zero, otherwise defaults to one."""
    return int(x) if x and x != 0 else 1

def non_zero_range(high:pd.Series, low:pd.Series):
    """Returns the difference of two series and adds epsilon if
    to any zero values.  This occurs commonly in crypto data when
    high = low.
    """
    diff = high - low
    if diff.eq(0).any().any():
        diff += sflt.epsilon
    return diff

def zero(x):
    """If the value is close to zero, then return zero.  Otherwise return the value."""
    return 0 if -sflt.epsilon < x and x < sflt.epsilon else x

def fibonacci(**kwargs):
    """Fibonacci Sequence as a numpy array"""
    n = int(math.fabs(kwargs.pop('n', 2)))
    zero = kwargs.pop('zero', False)
    weighted = kwargs.pop('weighted', False)

    if zero:
        a, b = 0, 1
    else:
        n -= 1
        a, b = 1, 1

    result = np.array([a])
    for i in range(0, n):
        a, b = b, a + b
        result = np.append(result, a)

    if weighted:
        fib_sum = np.sum(result)
        if fib_sum > 0:
            return result / fib_sum
        else:
            return result
    else:
        return result

def atr(high, low, close, length=None, mamode=None, drift=None, offset=None, **kwargs):
    """Indicator: Average True Range (ATR)"""
    # Validate arguments
    high = verify_series(high)
    low = verify_series(low)
    close = verify_series(close)
    length = int(length) if length and length > 0 else 14
    min_periods = int(kwargs['min_periods']) if 'min_periods' in kwargs and kwargs['min_periods'] is not None else length
    mamode = mamode.lower() if mamode else 'ema'
    drift = get_drift(drift)
    offset = get_offset(offset)

    # Calculate Result
    tr = true_range(high=high, low=low, close=close, drift=drift)
    if mamode == 'ema':
        alpha = (1.0 / length) if length > 0 else 0.5
        atr = tr.ewm(alpha=alpha, min_periods=min_periods).mean()
    else:
        atr = tr.rolling(length, min_periods=min_periods).mean()

    # Offset
    if offset != 0:
        atr = atr.shift(offset)

    # Handle fills
    if 'fillna' in kwargs:
        atr.fillna(kwargs['fillna'], inplace=True)
    if 'fill_method' in kwargs:
        atr.fillna(method=kwargs['fill_method'], inplace=True)

    # Name and Categorize it
    atr.name = f"ATR_{length}"
    atr.category = 'volatility'

    return atr

def true_range(high, low, close, drift=None, offset=None, **kwargs):
    """Indicator: True Range"""
    # Validate arguments
    high = verify_series(high)
    low = verify_series(low)
    close = verify_series(close)
    high_low_range = non_zero_range(high, low)
    drift = get_drift(drift)
    offset = get_offset(offset)

    # Calculate Result
    prev_close = close.shift(drift)
    ranges = [high_low_range, high - prev_close, prev_close - low]
    true_range = DataFrame(ranges).T
    true_range = true_range.abs().max(axis=1)

    # Offset
    if offset != 0:
        true_range = true_range.shift(offset)

    # Handle fills
    if 'fillna' in kwargs:
        true_range.fillna(kwargs['fillna'], inplace=True)
    if 'fill_method' in kwargs:
        true_range.fillna(method=kwargs['fill_method'], inplace=True)

    # Name and Categorize it
    true_range.name = f"TRUERANGE_{drift}"
    true_range.category = 'volatility'

    return true_range