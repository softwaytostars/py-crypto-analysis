from numpy import NaN as npNaN

from indicators.utils import verify_series, get_offset

# https://github.com/twopirllc/pandas-ta/blob/master/pandas_ta/overlap/ema.py
def emaFromPandaTa(close, length=None, offset=None, **kwargs):
    """Indicator: Exponential Moving Average (EMA)"""
    # Validate Arguments
    close = verify_series(close)
    length = int(length) if length and length > 0 else 10
    min_periods = kwargs.pop('min_periods', length)
    adjust = kwargs.pop('adjust', True)
    offset = get_offset(offset)
    sma = kwargs.pop('sma', True)
    ewm = kwargs.pop('ewm', False)

    # Calculate Result
    if ewm:
        # Mathematical Implementation of an Exponential Weighted Moving Average
        ema = close.ewm(span=length, min_periods=min_periods, adjust=adjust).mean()
    else:
        alpha = 2 / (length + 1)
        close = close.copy()

        def ema_(series):
            # Technical Anaylsis Definition of an Exponential Moving Average
            # Slow for large series
            series.iloc[1] = alpha * (series.iloc[1] - series.iloc[0]) + series.iloc[0]
            return series.iloc[1]

        seed = close[0:length].mean() if sma else close.iloc[0]

        close[:length - 1] = npNaN
        close.iloc[length - 1] = seed
        ma = close[length - 1:].rolling(2, min_periods=2).apply(ema_, raw=False)
        ema = close[:length].append(ma[1:])

    # Offset
    if offset != 0:
        ema = ema.shift(offset)

    # Name & Category
    ema.name = f"EMA_{length}"
    ema.category = 'overlap'

    return ema
