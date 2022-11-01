from math import pi
from bokeh.plotting import figure, show, output_notebook, output_file
import IPython
import pandas as pd

def showAll(df, withbuysell, filename):
    output_notebook()
    def get_candlestick_width(datetime_interval):
        if datetime_interval == 'minute':
            return 30 * 60 * 1000  # half minute in ms
        elif datetime_interval == 'hour':
            return 0.5 * 60 * 60 * 1000  # half hour in ms
        elif datetime_interval == 'day':
            return 12 * 60 * 60 * 1000  # half day in ms
        elif datetime_interval == 'week':
            return 24 * 7 * 60 * 60 * 1000 * 0.5

    inc = df.Close > df.Open
    dec = df.Open > df.Close
    title = '%s datapoints from %s to %s for %s and %s from %s with MACD strategy' % (
        'week', 'a', 'b', 'c', 'to_symbol', 'exchange')
    p = figure(width=2000, title=title)

    # plot macd strategy
    p.line(df.datetime, 0, color='black')
    p.line(df.datetime, 20, color='black')
    #p.line(df.index, 5000+df.tsi, color='blue')
    p.line(df.datetime, 1000*df.tsi, color='blue')
    p.line(df.datetime, 1000*df.ematsi, color='red')
    # p.line(df.index, df.macd_signal, color='orange')
    p.vbar(x=df.index, bottom=[0 for _ in df.index], top=10*df.ao, width=4, color="purple")

    # plot boll strategy
    # p.line(df.index, df.boll, color='blue')
    # p.line(df.index, df.boll_ub, color='orange')
    # p.line(df.index, df.boll_lb, color="green")

    #plot SAR
    p.diamond(df.datetime, df.SAR, size=4,
                 color="#1C9099", line_width=2)
    # plot candlesticks
    p.line(df.datetime, df.Close, color='black')
    candlestick_width = get_candlestick_width('week')
    # p.segment(df.index, df.High,
    #           df.index, df.Low, color="black")
    # p.vbar(df.index[inc], candlestick_width, df.Open[inc],
    #        df.Close[inc], fill_color="#D5E1DD", line_color="black")
    # p.vbar(df.index[dec], candlestick_width, df.Open[dec],
    #        df.Close[dec], fill_color="#F2583E", line_color="black")
    if withbuysell:
        interval_index = df.index[1] - df.index[0]
        p.segment(df.index-3*interval_index, df.buy, df.index+3*interval_index, df.buy,
                   color="green")
        p.segment(df.index, 0, df.index, df.buy+0.1*df.buy,
                  color="green")

        p.segment(df.index - 3 * interval_index, df.sell, df.index + 3 * interval_index, df.sell,
                  color="red")
        p.segment(df.index, 0, df.index, df.sell + 0.1 * df.sell,
                  color="red")

    # p.hbar(df.sell, candlestick_width, df.index - 100, df.index + 100, color="red")

    output_file(filename, title="visualizing trading strategy")
    show(p)
