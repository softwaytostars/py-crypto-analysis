import pandas as pd


def read_datasetBitStamp(filename):
    print('Reading data from %s' % filename)
    df = pd.read_csv(filename)
    df = df.set_index('opentime')
    df = df.sort_index()  # sort by datetime
    print(df.shape)
    return df
