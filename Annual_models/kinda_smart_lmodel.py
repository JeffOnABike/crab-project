import numpy as np
import pandas as pd
import cPickle as pickle
# from scipy import stats
import statsmodels.api as sm
# import matplotlib.pyplot as plt
# import seaborn as sns



# FOR LINEAR MODELS:
def leave_one_out(pdo_predictive, port_seasonal, start, len_train, verbose = False):
	pdo_predictive = pdo_predictive.copy()
	pdo_predictive.index = pdo_predictive.index.year
	test_ind = start + len_train # inclusive for pandas indexing
	train = port_seasonal.ix[start:test_ind - 1]
	train_y = train.values

	ar1 = port_seasonal.ix[start - 1:test_ind - 2]
	ar1 = ar1.reshape(len_train, 1)
	train_x =  pdo_predictive.ix[start:test_ind - 1].values
	train_x = np.hstack((train_x.reshape(len_train, 1), ar1))
	test_x_pdo = pdo_predictive.ix[test_ind]
	test_x_ar1 = port_seasonal.ix[test_ind - 1]
	l_model = sm.OLS(train_y, sm.add_constant(train_x)).fit()
	l_pred = l_model.predict([1, test_x_pdo, test_x_ar1])[0]
	test_y = port_seasonal.ix[test_ind]
	if verbose:
		print 'predicting for ', test_ind, 'season...'
		print 'predict: ', l_pred
		print 'actually: ', test_y
		print 'Model R^2 = ', l_model.rsquared
		print
	err = test_y - l_pred

	return err

# collect rolling errors starting at 1945 training, roll forward
def rolling_errors(pdo_predictive, port_seasonal, end_season, start_season = 1945, len_train = 20, verbose = False):
	if end_season < start_season + len_train:
		return 'end test further in future for this training size'
	if end_season > 2015:
		return 'cannot test further than 2015 season'

	errs = []
	start = start_season
	while start + len_train <= end_season:
		if verbose:
			print 'starting training on: ', start
		errs.append(leave_one_out(pdo_predictive, port_seasonal, start, len_train, verbose))
		start += 1
		if start >2010:
			break
 	return errs

def c_origin_errors(pdo_predictive, port_seasonal, end_season, start_season = 1945, len_train = 20, verbose = False):
	if end_season < start_season + len_train:
		return 'end test further in future for this training size'
	if end_season > 2015:
		return 'cannot test further than 2015 season'

	errs = []
	start = start_season
	while start + len_train <= end_season:
		if verbose:
			print 'starting training on: ', start
		errs.append(leave_one_out(pdo_predictive, port_seasonal, start, len_train, verbose))
		# start += 1
		len_train +=1
		if start  + len_train >2010:
			break
 	return errs


def calc_MAE(errs):
	return np.abs(np.array(errs)).mean()

if __name__ == '__main__':		
	# GET MASTER DATA
	with open('pickle_data/pdo_monthly.pkl', 'r') as f:
		pdo_monthly = pickle.load(f)
	pdo_predictive = pdo_monthly.resample('A-OCT')
	pdo_predictive.index += 4

	with open('pickle_data/areas_seasonal.pkl', 'r') as f:
		seasonal = pickle.load(f)
	# ROLLING
	results = {}
	# for port_area in seasonal:
	# 	errs = rolling_errors(pdo_predictive, seasonal[port_area], end_season = 2010, start_season = 1951, len_train = 20, verbose = True)
	# 	results[port_area] = calc_MAE(errs)
	# print results

	# C ORIGIN
	results = {}
	
	for port_area in seasonal:
		errs = c_origin_errors(pdo_predictive, seasonal[port_area], end_season = 2010, start_season = 1951, len_train = 20, verbose = True)
		results[port_area] = calc_MAE(errs)
	print results