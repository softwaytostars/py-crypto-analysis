from ta.utils import ema

from indicators.ema import emaFromPandaTa


def double_smooth(src, long, short):
    first_smooth = src.ewm(span=long, adjust=False).mean()
    return first_smooth.ewm(span=short, adjust=False).mean()

def tsi(close, long=25, short=13, signal=13):
    pc = close - close.shift(1)
    double_smoothed_pc = double_smooth(pc, long, short)
    double_smoothed_abs_pc = double_smooth(abs(pc), long, short)
    tsi_value = 100.0 * (double_smoothed_pc / double_smoothed_abs_pc)
    ematsi = tsi_value.ewm(span=signal, adjust=False).mean()
    return (tsi_value, ematsi)
