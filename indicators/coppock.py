from pandas import Series, DataFrame
from numpy import arange as nparange
import pandas as pd


# https://github.com/twopirllc/pandas-ta/blob/master/pandas_ta/momentum/coppock.py
from indicators.rma import rma
from indicators.utils import get_offset, verify_series, get_drift


def coppock(close, length=None, fast=None, slow=None, offset=None, **kwargs):
    """Indicator: Coppock Curve (COPC)"""
    # Validate Arguments
    close = verify_series(close)
    length = int(length) if length and length > 0 else 10
    fast = int(fast) if fast and fast > 0 else 11
    slow = int(slow) if slow and slow > 0 else 14
    min_periods = int(kwargs['min_periods']) if 'min_periods' in kwargs and kwargs[
        'min_periods'] is not None else length
    offset = get_offset(offset)

    # Calculate Result
    total_roc = roc(close, fast) + roc(close, slow)
    coppock = wma(total_roc, length)

    # Offset
    if offset != 0:
        coppock = coppock.shift(offset)

    # Handle fills
    if 'fillna' in kwargs:
        coppock.fillna(kwargs['fillna'], inplace=True)
    if 'fill_method' in kwargs:
        coppock.fillna(method=kwargs['fill_method'], inplace=True)

    # Name and Categorize it
    coppock.name = f"COPC_{fast}_{slow}_{length}"
    coppock.category = 'momentum'

    return coppock

def roc(close, length=None, offset=None, **kwargs):
    """Indicator: Rate of Change (ROC)"""
    # Validate Arguments
    close = verify_series(close)
    length = int(length) if length and length > 0 else 10
    min_periods = int(kwargs['min_periods']) if 'min_periods' in kwargs and kwargs[
        'min_periods'] is not None else length
    offset = get_offset(offset)

    # Calculate Result
    roc = 100 * mom(close=close, length=length) / close.shift(length)

    # Offset
    if offset != 0:
        roc = roc.shift(offset)

    # Handle fills
    if 'fillna' in kwargs:
        roc.fillna(kwargs['fillna'], inplace=True)
    if 'fill_method' in kwargs:
        roc.fillna(method=kwargs['fill_method'], inplace=True)

    # Name and Categorize it
    roc.name = f"ROC_{length}"
    roc.category = 'momentum'

    return roc


def mom(close, length=None, offset=None, **kwargs):
    """Indicator: Momentum (MOM)"""
    # Validate Arguments
    close = verify_series(close)
    length = int(length) if length and length > 0 else 10
    offset = get_offset(offset)

    # Calculate Result
    mom = close.diff(length)

    # Offset
    if offset != 0:
        mom = mom.shift(offset)

    # Handle fills
    if 'fillna' in kwargs:
        mom.fillna(kwargs['fillna'], inplace=True)
    if 'fill_method' in kwargs:
        mom.fillna(method=kwargs['fill_method'], inplace=True)

    # Name and Categorize it
    mom.name = f"MOM_{length}"
    mom.category = 'momentum'

    return mom


def wma(close, length=None, asc=None, offset=None, **kwargs):
    """Indicator: Weighted Moving Average (WMA)"""
    # Validate Arguments
    close = verify_series(close)
    length = int(length) if length and length > 0 else 10
    min_periods = int(kwargs['min_periods']) if 'min_periods' in kwargs and kwargs[
        'min_periods'] is not None else length
    asc = asc if asc else True
    offset = get_offset(offset)

    # Calculate Result
    total_weight = 0.5 * length * (length + 1)
    weights_ = Series(nparange(1, length + 1))
    weights = weights_ if asc else weights_[::-1]

    def linear(w):
        def _compute(x):
            return (w * x).sum() / total_weight

        return _compute

    close_ = close.rolling(length, min_periods=length)
    wma = close_.apply(linear(weights), raw=True)

    # Offset
    if offset != 0:
        wma = wma.shift(offset)

    # Name & Category
    wma.name = f"WMA_{length}"
    wma.category = 'overlap'

    return wma
