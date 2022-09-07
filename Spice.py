import datetime as dt
from matplotlib.pyplot import style
import pandas_datareader.data as web

style.use('ggplot')

start = dt.datetime(2011, 1, 1)
end = dt.datetime(2021, 5, 1)

df = web.DataReader('AMC', 'yahoo', start, end)
df.to_csv('AMC.csv')