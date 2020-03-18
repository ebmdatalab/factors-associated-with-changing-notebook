import os
import pandas as pd
from lib.regression import data_for_regression as dfr


def get_data():
    """Runs all functions in data_for_regression.py
    Each of these functions returns a df with entity code as the index.
    All dfs are joined and the resulting df is cached.
    
    Returns:
        pandas DataFrame: Containing all regression variables
    """
    cache_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "data", "cached_all_data.csv"
    )
    if not os.path.exists(cache_path):
        df = pd.DataFrame()
        for i in dir(dfr):
            item = getattr(dfr, i)
            if callable(item):
                df = df.join(item(), how="outer")
        df.to_csv(cache_path, index_label="code")
    else:
        df = pd.read_csv(cache_path, index_col="code")
    return df
