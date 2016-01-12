import numpy as np
import pandas as pd
import cPickle as pickle
from scipy import stats
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_squared_error
from math import sqrt

# GET MASTER DATA
with open('data/new_all_data.pkl', 'r') as f:
	all_data = pickle.load(f)
# GET ALL SEASONAL TOTALS BY PORT!, NORM TO MILLlb.
mil = 1000000.
season_tots = all_data.groupby('Season').sum()/mil

def plot_stacked_bar(save = False):
	season_tots.drop(['All', 'S_Month'], axis = 1).plot(kind = 'bar', stacked = True, figsize =(14,8))
	plt.ylabel('Millions of pounds')
	plt.suptitle('Annual landings of Dungeness Crab by Season and Port Area')
	# plt.show()
	if save == True:
		plt.savefig('images/new_AnnualLandings.png')
	return
plot_stacked_bar(save = True)
series_seasonal = {	'All': season_tots['All'], \
					'Eureka' : season_tots['Eureka'], \
					'Sf': season_tots['San Francisco'], \
					'Monterey' : season_tots['Monterey'], \
					'Sb' : season_tots['Santa Barbara']
}

def make_timeseries(data_seasonal):
	# time series is identified by ending month (Sept of year after season)
	start = str(data_seasonal.index[0]+1) + '-09-01'
	end = str(data_seasonal.index[-1]+2) + '-09-01'
	dt_index = pd.date_range(start = start, end = end, freq = 'A-SEP')

	## OR by same year:
	# start = str(data_seasonal.index[0]+1) + '-11-01'
	# end = str(data_seasonal.index[-1]+2) + '-11-01'
	# dt_index = pd.date_range(start = start, end = end, freq = 'A-NOV')
	ts = pd.Series(data_seasonal.values, index=dt_index)
	return ts

def lin_model(ts, plot = True):

	y = ts.values
	x = range(1, ts.shape[0] + 1)
	l_model = sm.OLS(y, sm.add_constant(x)).fit()
	if plot:
		ts.plot(figsize=(12,8), lw=0.5)
		pd.Series(l_model.fittedvalues, index=ts.index).plot(style='r')
		plt.show()
	return l_model

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

def test_one_year(series_seasonal, start, end, ar, d, ma):
	# split original series_seasonal data:
	actual_ts = make_timeseries(series_seasonal.ix[start:end + 1])
	train_ts = actual_ts[:-1]

	# train models with train_ts
	l_model = lin_model(train_ts, plot = True)
	l_model_int = l_model.params[0]
	l_model_coef = l_model.params[1]
	train_ts_detrend = detrend_data(train_ts, l_model, plot = False)
	s_model = fit_sarimax(train_ts_detrend, ar,d,ma,0,0,0,0)

	# look at ACF_PACF for model resids and compare RMSE of fits
	print 'RMSE sarimax model fit: ',evaluate_model(s_model)
	print 'RMSE linear model fit: ', evaluate_model(l_model)
	print
	l_forecast_trended = l_model_int + len(actual_ts)*l_model_coef
	s_forecast_detrended = s_model.forecast()
	s_forecast_trended = s_forecast_detrended + l_forecast_trended

	mil = 1000000.
	# more interpretable:
	# season ID identifies year in which that season STARTED
	forecast_season_id = s_forecast_trended.index.year[0] - 1
	l_forecast = l_forecast_trended/mil
	s_forecast = s_forecast_trended.values[0]/mil
	actual = actual_ts.ix[s_forecast_trended.index[-1]]/mil

	print 'for the %d season...' % forecast_season_id
	print 'linear model forecast: ', l_forecast
	print 'AR model forecast: ', s_forecast
	print 'actual landings: ', actual
	print

	# retrend for the plot!
	# linear_vals = np.append(l_model.predict(), l_forecast_trended)
	plot_sarimax_pred(train_ts_detrend, s_model, 2)
	# return train_ts_detrend, s_model
	return [forecast_season_id, l_forecast, s_forecast, actual]

def do_a_lot():
	all_results = []
	for data_ended in xrange(1966, 2014):
		all_results.append(test_one_year(all_seasonal, 1945, data_ended, 2))

	df = pd.DataFrame(all_results, columns = ['Season', 'l_pred', 's_pred', 'actual'])
	df[['l_pred','s_pred','actual']].plot()
	plt.legend()
	plt.show()
	return all_results

def get_RMSE(df, col):
	rms = sqrt(mean_squared_error(df['actual'], df[col]))
	return rms



# if __name__ == '__main__':
	# with open('data/all_data.pkl', 'r') as f:
	# 	all_data = pickle.load(f)

# training_years = zip(range(1944,1994), range(1965,2014))

## FIX THIS:
# def plot_linear_pred(ts, sarimax_model, steps):
# 	# x = ts.index.union(smodel.forecast(steps = steps).index)
# 	ts.plot(label = 'actual')
# 	sarimax_model.predict().plot(label = 'model fit')
# 	sarimax_model.forecast(steps = steps).plot(label = 'future')
# 	plt.legend()
# 	plt.show()
# 	return
		

# pdo_annual = pdo.resample('A-OCT', how='sum')
# pdo_annual.index = pdo_annual.index.year
# pdo_annual.index += 3



# if __name__ == '__main__':
# 	with open('data/all_data.pkl', 'r') as f:
# 		all_data = pickle.load(f)


# (season_tots/1000000).plot()
# pdo_annual.plot()
# df_p = pd.DataFrame(pdo_annual)
# df_s = pd.DataFrame(season_tots)
# new_df = pd.merge(df_s, df_p, left_index = True, right_index = True)
# new_df['All']= new_df['All']/1000000.

# x = new_df[0]
# y = new_df['All']
# model = sm.OLS(y, sm.add_constant(x)).fit()
# y.plot(figsize = (12, 8))
# pd.Series(model.fittedvalues, index = y.index).plot()
# model.summary()

# new_index = pd.PeriodIndex(start = eureka.index[0], end = eureka.index[-1])
# eureka.index = new_index
# model = sm.tsa.ARIMA(eureka, order = (3,1,0))


# all_data = consolidate_data(all_landings)
# seasonal_all = get_seasonal_breakdown(all_data)['All']
# monthly_all = all_data['All']
# monthly_all.groupby(monthly_all.index.month).mean()
# monthly_all.groupby(monthly_all.index.year).mean()
# x = range(len(y))
# y = monthly_all.values
# model = sm.OLS(y, sm.add_constant(x)).fit()
# monthly_all.plot(figsize = (12, 8))
# pd.Series(model.fittedvalues, index = monthly_all.index).plot()
# model.summary()
# df = monthly_all
# df['t'] = range(1, df.shape[0] + 1)
# df['t_2'] = df['t']**2
# x = df[['t', 't_2']]
# x = np.hstack([x.values, pd.get_dummies(df.index.month).values])
# df.plot(kind = 'scatter', x = 't', y='resids', figsize=(12,8))