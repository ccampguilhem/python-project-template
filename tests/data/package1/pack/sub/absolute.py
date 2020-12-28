import pack.analytics
from pandas import DataFrame
import relative
import sample
# This one is illegal in Python 3 but OK in Python 2.7 but could be prevented with:
# from __future__ import absolute_import
from relative import is_relative


def head(df):
    return df.head()


def info(df):
    return df.info()

