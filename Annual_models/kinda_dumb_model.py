import numpy as np
import pandas as pd
import cPickle as pickle
import statsmodels.api as sm
# from model_evaluation import calc_MAE, rolling_errors, leave_one_out

'''
The kinda_dumb_model always guesses this season's totals for next season
'''

def kinda_dumb_model(train):
	pred = train.iloc[-1]
	return pred


def leave_one_out(port_seasonal, start, len_train, verbose = False):
	loocv_ind = start + len_train # inclusive for pandas indexing
	train = port_seasonal.ix[start:loocv_ind - 1]
	if verbose:
		# print 'training set :'
		# print train
		print
	pred = kinda_dumb_model(train)
	target = port_seasonal.ix[loocv_ind]
	if verbose:
		print 'predicting for ', loocv_ind, 'season...'
		print 'predict: ', pred
		print 'actually: ', target
		print
	err = target - pred
	return err

def rolling_errors(port_seasonal, end_season, start_season = 1945, len_train = 20, verbose = False):
	if end_season < start_season + len_train:
		return 'end test further in future for this training size'
	if end_season > 2015:
		return 'cannot test further than 2015 season'

	errs = []
	start = start_season
	while start + len_train <= end_season:
		if verbose:
			print 'starting training on: ', start
		errs.append(leave_one_out(port_seasonal, start, len_train, verbose))
		start += 1
		if start >2015:
			break
 	return errs


def calc_MAE(errs):
	return np.abs(np.array(errs)).mean()

if __name__ == '__main__':		
	# GET SEASONAL DATA FOR ALL SEASONS
	with open('pickle_data/areas_seasonal.pkl', 'r') as f:
		seasonal = pickle.load(f)
	results = {}
	for port_area in seasonal:
		errs = rolling_errors(seasonal[port_area], end_season = 2010, start_season = 1949, len_train = 22, verbose = True)
		results[port_area] = calc_MAE(errs)
	print results

