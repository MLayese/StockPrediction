# All the imports
import bs4 as bs
import pickle
import requests
import datetime as dt
import pandas as pd
import pandas_datareader.data as web
import os
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from sklearn import svm, neighbors
from sklearn.model_selection import train_test_split
from sklearn.ensemble import VotingClassifier, RandomForestClassifier
from matplotlib.pyplot import style

style.use('ggplot')

print(os.getcwd())


# list for the S&P 500
def sp500_tickers():
    resp = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, "lxml")
    table = soup.find('table', {'id': 'constituents'})
    # Empty list
    tickers = []
    # tr = table row in case I forget/td = table data/0 is all the company names
    for row in table.findAll('tr')[1:]:
        ticker = row.find('td').text
        if "." in ticker:
            ticker = ticker.replace('.', '-')
            print('ticker replaced to', ticker)
        tickers.append(ticker.strip())
        # strip()gets rid of \n

    with open("sp500tickers.pickle", "wb") as f:
        pickle.dump(tickers, f)

    print(tickers)

    return tickers


sp500_tickers()


def yahoo_data(reload_sp500=False):
    if reload_sp500:
        tickers = sp500_tickers()
    else:
        with open("sp500tickers.pickle", "rb") as f:
            tickers = pickle.load(f)

    if not os.path.exists('stock_dfs'):
        os.makedirs('stock_dfs')

    start = dt.datetime(2011, 1, 1)
    end = dt.datetime(2021, 5, 1)

    for ticker in tickers:
        try:
            print(ticker)
            if not os.path.exists('stock_dfs/{}.csv'.format(ticker)):
                df = web.DataReader(ticker, 'yahoo', start, end)
                df.reset_index(inplace=True)
                df.set_index('Date', inplace=True)
                df.to_csv('stock_dfs/{}.csv'.format(ticker))
            else:
                print('Already have {}'.format(ticker))
        except KeyError:
            pass


# This took quite awhile to download
#yahoo_data()


# Compiling all the CSV files for individual companies into one giant data frame
def compile_data():
    with open("sp500tickers.pickle", "rb") as f:
        tickers = pickle.load(f)

    main_df = pd.DataFrame()

    for count, ticker in enumerate(tickers):
        df = pd.read_csv('stock_dfs/{}.csv'.format(ticker.replace('.', '-')))
        df.set_index('Date', inplace=True)

        df.rename(columns={'Adj Close': ticker}, inplace=True)
        df.drop(['Open', 'High', 'Low', 'Close', 'Volume'], 1, inplace=True)

        if main_df.empty:
            main_df = df
        else:
            main_df = main_df.join(df, how='outer')

        if count % 10 == 0:
            print(count)
    print(main_df.tail())
    main_df.to_csv('sp500_joined_closes.csv')


#compile_data()
def visualize_data():
    # Beta comparisons of company returns
    df = pd.read_csv('sp500_joined_closes.csv')
    # df['AAPL'].plot()
    # plt.show()
    df.set_index('Date', inplace=True)
    df_corr = df.pct_change().corr()
    print(df_corr.head())

visualize_data()
