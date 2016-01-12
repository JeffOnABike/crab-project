# check out R results:
import pandas as pd
import numpy as np

# ts_all = pd.read_csv('data/ts_all.csv')

#BIC predictions
# first is SEASON ENDING 1985
R_preds = pd.read_csv('BICpreds_85_04.csv')
# R_preds['Unnamed: 0'] = range(1985, 2005)
R_preds.index = pd.date_range(start = '1985', end = '2005', freq = 'A-SEP')
R_preds.drop('Unnamed: 0', axis = 1, inplace = True)
pd.merge(pd.DataFrame(ts_all), R_preds, left_index=True, right_index = True)
real_preds = pd.merge(pd.DataFrame(ts_all), R_preds, left_index=True, right_index = True)

np.mean(np.abs(real_preds[0] - real_preds['x']))
np.mean(np.abs(real_preds[0] - mean_guess))