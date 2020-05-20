from pandas import DataFrame

from indicators.rma import rma
from indicators.utils import verify_series, get_drift, get_offset, atr, zero
import pandas as pd

def adx(high, low, close, length=None, drift=None, offset=None, **kwargs):
    """Indicator: ADX"""
    # Validate Arguments
    high = verify_series(high)
    low = verify_series(low)
    close = verify_series(close)
    length = length if length and length > 0 else 14
    drift = get_drift(drift)
    offset = get_offset(offset)

    # Calculate Result
    _atr = atr(high=high, low=low, close=close, length=length)

    up = high - high.shift(drift)
    dn = low.shift(drift) - low

    pos = ((up > dn) & (up > 0)) * up
    neg = ((dn > up) & (dn > 0)) * dn

    pos = pos.apply(zero)
    neg = neg.apply(zero)

    dmp = (100 / _atr) * rma(close=pos, length=length)
    dmn = (100 / _atr) * rma(close=neg, length=length)

    dx = 100 * (dmp - dmn).abs() / (dmp + dmn)
    adx = rma(close=dx, length=length)

    # Offset
    if offset != 0:
        dmp = dmp.shift(offset)
        dmn = dmn.shift(offset)
        adx = adx.shift(offset)

    # Handle fills
    if 'fillna' in kwargs:
        adx.fillna(kwargs['fillna'], inplace=True)
        dmp.fillna(kwargs['fillna'], inplace=True)
        dmn.fillna(kwargs['fillna'], inplace=True)
    if 'fill_method' in kwargs:
        adx.fillna(method=kwargs['fill_method'], inplace=True)
        dmp.fillna(method=kwargs['fill_method'], inplace=True)
        dmn.fillna(method=kwargs['fill_method'], inplace=True)

    # Name and Categorize it
    adx.name = f"ADX_{length}"
    dmp.name = f"DMP_{length}"
    dmn.name = f"DMN_{length}"

    adx.category = dmp.category = dmn.category = 'trend'

    # Prepare DataFrame to return
    data = {adx.name: adx, dmp.name: dmp, dmn.name: dmn}
    adxdf = DataFrame(data)
    adxdf.name = f"ADX_{length}"
    adxdf.category = 'trend'

    return adxdf


def average_directional_movement_index(df, n, n_ADX):
    """Calculate the Average Directional Movement Index for given data.

    :param df: pandas.DataFrame
    :param n:
    :param n_ADX:
    :return: pandas.DataFrame
    """
    i = 0
    UpI = []
    DoI = []
    while i + 1 <= df.index[-1]:
        UpMove = df.loc[i + 1, 'High'] - df.loc[i, 'High']
        DoMove = df.loc[i, 'Low'] - df.loc[i + 1, 'Low']
        if UpMove > DoMove and UpMove > 0:
            UpD = UpMove
        else:
            UpD = 0
        UpI.append(UpD)
        if DoMove > UpMove and DoMove > 0:
            DoD = DoMove
        else:
            DoD = 0
        DoI.append(DoD)
        i = i + 1
    i = 0
    TR_l = [0]
    while i < df.index[-1]:
        TR = max(df.loc[i + 1, 'High'], df.loc[i, 'Close']) - min(df.loc[i + 1, 'Low'], df.loc[i, 'Close'])
        TR_l.append(TR)
        i = i + 1
    TR_s = pd.Series(TR_l)
    # ATR = pd.Series(TR_s.ewm(span=n, min_periods=n).mean())
    ATR = rma(TR_s, n)
    UpI = pd.Series(UpI)
    DoI = pd.Series(DoI)
    # PosDI = 100*pd.Series(UpI.ewm(span=n, min_periods=n).mean() / ATR)
    PosDI = 100 * rma(UpI, n) / ATR
    # NegDI = 100*pd.Series(DoI.ewm(span=n, min_periods=n).mean() / ATR)
    NegDI = 100 * rma(DoI, n) / ATR
    # ADX = 100*pd.Series((abs(PosDI - NegDI) / (PosDI + NegDI)).ewm(span=n_ADX, min_periods=n_ADX).mean(), name='adx')
    ADX = 100 * rma(abs(PosDI - NegDI) / (PosDI + NegDI), n_ADX)
    return ADX