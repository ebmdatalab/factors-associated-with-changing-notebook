import pandas as pd
from lib.regression import data_for_regression as dfr


# STILL NEED TO ADD A FUNCITON TO CACHE THE RESULTING JOINED FILE

def get_data():
	df = pd.DataFrame()
	for i in dir(dfr):
	    item = getattr(dfr,i)
	    if callable(item):
	        df = df.join(item(),how='outer')
	return df