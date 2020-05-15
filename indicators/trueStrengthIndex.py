from ta.utils import ema

from indicators.ema import emaFromPandaTa


def double_smooth(src, long, short):
    first_smooth = emaFromPandaTa(src, long)
    return emaFromPandaTa(first_smooth, short)


def tsi(close, long=25, short=13, signal=13):
    pc = close - close.shift(1)
    double_smoothed_pc = double_smooth(pc, long, short)
    double_smoothed_abs_pc = double_smooth(abs(pc), long, short)
    tsi_value = 100 * (double_smoothed_pc / double_smoothed_abs_pc)
    ematsi = emaFromPandaTa(tsi_value, signal)
    return (tsi_value, ematsi)
