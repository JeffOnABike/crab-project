import numpy as np
import pandas as pd
import cPickle as pickle
from scipy import stats
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns

# GET MASTER DATA
with open('data/all_data.pkl', 'r') as f:
	all_data = pickle.load(f)

# MAKE SEASONAL TIME SERIES BY PORT
season_tots = all_data.groupby('Season').sum()
series_seasonal = {	'All': season_tots['All'], \
					'Eureka' : season_tots['Eureka'], \
					'Sf': season_tots['San Francisco'], \
					'Monterey' : season_tots['Monterey'], \
					'Sb' : season_tots['Santa Barbara']
}

def make_timeseries(data_seasonal):
	# time series is identified by ending month (Sept of year after season)
	# start = str(data_seasonal.index[0]+1) + '-09-01'
	# end = str(data_seasonal.index[-1]+2) + '-09-01'
	# dt_index = pd.date_range(start = start, end = end, freq = 'A-SEP')

	## OR by same year:
	start = str(data_seasonal.index[0]) + '-11-01'
	end = str(data_seasonal.index[-1] + 1) + '-11-01'

	dt_index = pd.date_range(start = start, end = end, freq = 'A-NOV')
	ts = pd.Series(data_seasonal.values, index=dt_index)
	return ts


def lin_model(ts, plot = True):
	'''
	Generate linear model from input time series

	'''
	y = ts.values
	x = range(1, ts.shape[0] + 1)
	l_model = sm.OLS(y, sm.add_constant(x)).fit()
	if plot:
		ts.plot(figsize=(12,8), lw=0.5)
		pd.Series(l_model.fittedvalues, index=ts.index).plot(style='r')
		plt.show()
	l_intercept = l_model.params[0]
	l_coef = l_model.params[1]
	return l_model, l_intercept, l_coef

# plt.show()
# lin_model.summary()
# # we get an R squared of .27,
# # const - 6.028 (M)
# # x1 coef: 59,630

# AIC = 2960.3334956497265


def acf_pacf(ts, lags= 50, periods = 0):
	fig = plt.figure(figsize=(12,8))
	plt.suptitle('Time Series differenced by %s' % periods)
	ax1 = fig.add_subplot(211)
	fig = sm.graphics.tsa.plot_acf(ts[periods:], lags=lags, ax=ax1)
	ax2 = fig.add_subplot(212)
	fig = sm.graphics.tsa.plot_pacf(ts[periods:], lags=lags, ax=ax2)
	plt.show()
	return

def detrend_data(ts, l_model, plot = True):
	ts_detrend = pd.Series(l_model.resid, index=ts.index)
	if plot:
		ts_detrend.plot(figsize=(12,8))
		plt.title('Detrended Data')
		plt.show()
	return ts_detrend

def difference_data(ts, periods):
	if periods == 0:
		return 'periods must be > 0'
	differenced_data = ts.diff(periods = periods)
	plt.plot(differenced_data)
	plt.title('Time Series Differenced by %s' % periods)
	plt.show()
	acf_pacf(differenced_data, periods = periods)
	return 

#p: number of autoregressive terms 6?
#d: number of non-seasonal differences -1
#q: number of moving-avg terms 0

def fit_sarimax(ts, p, d, q, P, D, Q, L):
	# order=(1,1,0), seasonal_order=(0,1,0,10)
	order=(p,d,q)
	seasonal_order=(P,D,Q,L)
	sarimax_model=sm.tsa.SARIMAX(ts, order=order).fit()
	print 'AIC: ', sarimax_model.aic
	print 'BIC: ', sarimax_model.bic
	return sarimax_model
## FOR EUREKA:
# smodel = fit_sarimax(ts, 8,1,0,0,0,0,0)
#AIC = 2886.4919868
# 9 is also close!

## FOR SF:
# smodel = fit_sarimax(ts, 5,1,0,0,0,0,0)
# AIC = 2891.90418164

# FOR ALL:
# smodel = fit_sarimax(ts, 5,1,0,0,0,0,0)
def evaluate_model(model):
	'''
	errors is array of models for training set:
	option : SARIMAX errors: sarimax_model.forecasts_error
	LINEAR errors: linear_model.resid
	'''
	errors = model.resid
	acf_pacf(errors, lags = 15)
	sq_err = np.square(errors)
	MSE = sq_err.mean()
	RMSE = MSE**.5
	return RMSE
# RMSE for 9,1,0: 3.4037211410043109 (M)
# RMSE for 8,1,0: 3.4289796264733203 (M)
# RMSE for lmodel: 4.7726433647793751 (M)

def plot_sarimax_pred(ts, sarimax_model, steps = 2):
	# x = ts.index.union(smodel.forecast(steps = steps).index)
	
	sarimax_model.predict().plot(label = 'model fit')
	sarimax_model.forecast(steps = steps).plot(label = 'future')
	ts.plot(label = 'actual')
	plt.legend()
	plt.show()
	return

def test_one_year(series_seasonal, start, end, ar):
	# time_slice_plus_pred = series_seasonal.ix[start:end + 1]
	time_slice = series_seasonal.ix[start:end]
	ts = make_timeseries(time_slice)
	l_model = lin_model(ts, plot = True)
	ts_detrend = detrend_data(ts, l_model, plot = False)
	s_model = fit_sarimax(ts_detrend, ar,1,0,0,0,0,0)
	print 'RMSE sarimax model fit: ',evaluate_model(s_model)
	print 'RMSE linear model fit: ', evaluate_model(l_model)
	print
	forecast = s_model.forecast()
	forecast_season_id = forecast.index.year[0] - 1
	print 'model forecast: ', forecast.values[0]
	print 'actual: ', ts_detrend.ix[str(forecast_season_id)]
	print
	plot_sarimax_pred(ts_detrend, s_model, 2)
	return ts_detrend, s_model

# if __name__ == '__main__':
	with open('data/all_data.pkl', 'r') as f:
		all_data = pickle.load(f)