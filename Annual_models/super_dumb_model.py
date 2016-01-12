import numpy as np
import pandas as pd
import cPickle as pickle
# from scipy import stats
import statsmodels.api as sm
import matplotlib.pyplot as plt
# # get seasonals by port area
# def get_seasonal_dict(all_monthly):
# 	season_tots = all_monthly.groupby('Season').sum()/1000000.

# 	seasonal = {	'all' : season_tots['All'], 
# 					'eureka' : season_tots['Eureka'], 
# 					'sf' : season_tots['San Francisco'], 
# 					'monterey' : season_tots['Monterey'], 
# 					'sb' : season_tots['Santa Barbara']
# 	}
# 	return seasonal

# FOR LINEAR MODELS:
def leave_one_out(port_seasonal, start, len_train, verbose = False):
	loocv_ind = start + len_train # inclusive for pandas indexing
	train = port_seasonal.ix[start:loocv_ind - 1]

	y = train.values
	x = range(1, y.shape[0] + 1)
	l_model = sm.OLS(y, sm.add_constant(x)).fit()
	l_pred = l_model.predict([1, len_train + 1])[0]
	target = port_seasonal.ix[loocv_ind]
	if verbose:
		print 'predicting for ', loocv_ind, 'season...'
		print 'predict: ', l_pred
		print 'actually: ', target
		print
	err = target - l_pred
	sample_MAE = calc_MAE(l_model.resid)
	return err, sample_MAE

# collect rolling errors starting at 1945 training, roll forward
def rolling_errors(port_seasonal, end_season, start_season = 1945, len_train = 20, verbose = False):
	if end_season < start_season + len_train:
		return 'end test further in future for this training size'
	if end_season > 2015:
		return 'cannot test further than 2015 season'

	errs = []
	MAEs = []
	start = start_season
	while start + len_train <= end_season:
		if verbose:
			print 'starting training on: ', start
		err, sample_MAE = leave_one_out(port_seasonal, start, len_train, verbose)
		errs.append(err)
		MAEs.append(sample_MAE)

		start += 1
		if start >2005:
			break
 	return errs, MAEs

def c_origin_errors(port_seasonal, end_season, start_season = 1945, len_train = 20, verbose = False):
	if end_season < start_season + len_train:
		return 'end test further in future for this training size'
	if end_season > 2015:
		return 'cannot test further than 2015 season'

	errs = []
	MAEs = []

	start = start_season
	while start + len_train <= end_season:
		if verbose:
			print 'starting training on: ', start
		err, sample_MAE = leave_one_out(port_seasonal, start, len_train, verbose)
		errs.append(err)
		MAEs.append(sample_MAE)

		# start += 1
		len_train +=1
		if start  + len_train >2010:
			break
 	return errs, MAEs

def calc_MAE(errs):
	return np.abs(np.array(errs)).mean()


if __name__ == '__main__':		
	# GET MASTER DATA
	with open('pickle_data/areas_seasonal.pkl', 'r') as f:
		seasonal = pickle.load(f)

	# set constraints of test
	start_season = 1949
	len_train = 20
	end_season = 2010
	year_span = range(start_season+len_train, end_season+1)

	results = {}
	sample_MAEs = {}
	for port_area in seasonal:
		print ':::'
		print 'NOW PREDICTING FOR %s PORT:::' % port_area
		print ':::'
		errs, MAEs = c_origin_errors(seasonal[port_area], end_season = 2010, start_season = 1949, len_train = 20, verbose = True)
		results[port_area] = calc_MAE(errs)
		sample_MAEs[port_area] = MAEs
	print results
	#Plot an example:
	plt.plot(year_span, sample_MAEs['Eureka'])
	
	'''
	ROLLIN ORIGIN:
	'''
	results = {}
	sample_MAEs = {}
	for port_area in seasonal:
		print ':::'
		print 'NOW PREDICTING FOR %s PORT:::' % port_area
		print ':::'
		errs, MAEs = rolling_errors(seasonal[port_area], end_season = 2010, start_season = 1949, len_train = 22, verbose = True)
		results[port_area] = calc_MAE(errs)
		sample_MAEs[port_area] = MAEs
	print results
	#Plot an example:
	# plt.plot(year_span, sample_MAEs['Eureka'])
	

# 1945 -> when pots came into routine use in all regions
# trining: 1945 season until 1994 season
# test set: 1995-2004. Holdout: 2005-2014






## OPTIONAL CODE LATER

# ## Make a lin regression
# l = sb_seasonal.shape[0]
# t = np.arange(1, l + 1).reshape(l,1)
# Y = sb_seasonal.values.reshape(l,1)
# X  = np.hstack((np.ones(Y.shape),t))
# # X = sm.add_constant(sb_seasonal).values
# beta_vec = (np.linalg.inv(np.dot(X.T, X))).dot(X.T).dot(Y)
# yhat = X.dot(beta_vec)
# H = (X.dot(np.linalg.inv(X.T.dot(X)))).dot(X.T)

# def lin_model(ts, plot = True):
# 	'''
# 	Generate linear model from input time series

# 	'''
# 	y = ts.values
# 	x = range(1, ts.shape[0] + 1)
# 	l_model = sm.OLS(y, sm.add_constant(x)).fit()
# 	if plot:
# 		ts.plot(figsize=(12,8), lw=0.5)
# 		pd.Series(l_model.fittedvalues, index=ts.index).plot(style='r')
# 		plt.show()
# 	l_intercept = l_model.params[0]
# 	l_coef = l_model.params[1]
# 	return l_model, l_intercept, l_coef
