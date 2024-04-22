import pandas as pd
from pandas.testing import assert_series_equal

from whylabs_toolkit.monitor.diagnoser.helpers.describe import filter_by_index


def test_filter_by_index():
    to_sort = pd.Series([0, 1, 1], index=['c3', 'c4', 'c1'])
    ref = pd.Series([10, 9, 8], index=['c1', 'c2', 'c3'])
    expected = pd.Series([10, 8, 0], index=['c1', 'c3', 'c4'])
    assert_series_equal(filter_by_index(to_sort.index, ref), expected)
    assert_series_equal(filter_by_index(['c3', 'c4', 'c1'], ref), expected)
