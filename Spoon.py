import pickle
import confidence as confidence
import pandas as pd
import numpy as np
from collections import Counter
from sklearn import svm, neighbors
from sklearn.model_selection import train_test_split
from sklearn.ensemble import VotingClassifier, RandomForestClassifier


# Machine Learning based off of Data from Soup.py
def process_data_for_labels(ticker):
    # days can be interchangeable
    hm_days = 7
    df = pd.read_csv('AMC.csv', index_col=0)
    tickers = df.columns.values.tolist()
    df.fillna(0, inplace=True)
    # You were really really tired when you made this. Look up args if you don't remember why you wrote this
    for i in range(1, hm_days + 1):
        df['{}_{}d'.format(ticker, i)] = (df[ticker].shift(-i) - df[ticker]) / df[ticker]

    df.fillna(0, inplace=True)
    return tickers, df


def buy_sell_hold(*args):
    cols = [c for c in args]
    requirement = 0.02
    for col in cols:
        if col.any() > 0.025:
            return 1
        if col.any() < -0.025:
            return -1
    return 0


def extract_sets(ticker):
    hm_days = 7
    tickers, df = process_data_for_labels(ticker)

    # y value in range correlates with hm_days
    df['{}_target'.format(ticker)] = list(map(buy_sell_hold, df[['{}_{}d'.format(ticker, i)
                                                                 for i in range(1, hm_days + 1)]].values))
    vals = df['{}_target'.format(ticker)].values.tolist()
    str_vals = [str(i) for i in vals]
    print('Data spread:', Counter(str_vals))

    df.fillna(0, inplace=True)
    df = df.replace([np.inf, -np.inf], np.nan)
    df.dropna(inplace=True)

    df_vals = df[[ticker for ticker in tickers]].pct_change()
    df_vals = df_vals.replace([np.inf, -np.inf], 0)
    df_vals.fillna(0, inplace=True)

    x = df_vals.values
    y = df['{}_target'.format(ticker)].values

    return x, y, df


def do_ml(ticker):
    x, y, df = extract_sets(ticker)

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25)

    clf = VotingClassifier([
                            ('knn', neighbors.KNeighborsClassifier()),
                            ('rfor ', RandomForestClassifier())])

    clf.fit(x_train, y_train)
    confidence = clf.score(x_test, y_test)
    print('Accuracy', confidence)
    predictions = clf.predict(x_test)
    print('Predicted spread:', Counter(predictions))

    return confidence


do_ml('Volume')
