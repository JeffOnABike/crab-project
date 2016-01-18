# upwelling_exploration.py:

'''
Performs upwelling index EDA to look for correlations with landings
'''
import numpy as np
import pandas as pd
import cPickle as pickle
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm



def lag_samples(seasonal, port, upwell_monthly, month, lag_years, plot = True, return_df = False):
	# try mean and sum
	upwell_annual = upwell_monthly.resample('A-' + month, how='sum')
	upwell_annual.index = upwell_annual.index.year
	upwell_annual.index += lag_years

	if plot:
		seasonal[port].ix[1945:].plot(label = 'landings at %s' % port)
		(upwell_annual.ix[1945:]/100.).plot(label = 'upwell lagged by %d years' % lag_years)
		plt.legend()
		plt.show()

	df_p = pd.DataFrame(upwell_annual)
	df_s = pd.DataFrame(seasonal[port])
	new_df = pd.merge(df_s, df_p, left_index = True, right_index = True)
	new_df.columns = [port, 'upwell']


	if plot:
		new_df.plot(kind = 'scatter', x = 'upwell', y = port)
		plt.show()

	if return_df:
		return new_df.ix[1945:]
	# we care most about correllation from 1945 on
	return new_df.ix[1945:].corr().ix[1][0]


def cross_corr(upwell_monthly, port):
	'''
	Cross-correlate all annual resamplings going back 6 years with landings.
	'''
	months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
	results=[]
	for lag_years in range(0,6):
		for month in months:
			for port in seasonal:
				corr = lag_samples(seasonal, port, upwell_monthly, month, lag_years, plot = False)
				results.append([lag_years, month, port, corr])
	df_results = pd.DataFrame(results, columns = ['lag_years', 'resample month', 'port area', 'corr']).sort_values(by = 'corr')
	return df_results

def lmodel_plot(upwell_resampled, port_area):
	l_model = sm.OLS(upwell_resampled[port_area], sm.add_constant(upwell_resampled['upwell'])).fit()
	upwell_resampled[port_area].plot()
	l_model.fittedvalues.plot()
	plt.show()
	print l_model.summary()

def write_upwell_files(upwell_monthly):
	upwell_resampled = upwell_monthly.resample('A-AUG', how = 'sum')
	upwell_resampled_lag3 = upwell_resampled.copy()
	upwell_resampled.index = upwell_resampled.index.year
	with open('pickle_data/upwell_resampled.pkl', 'w') as f:
		pickle.dump(upwell_resampled, f)
	upwell_resampled.to_csv('csv_data/upwell_resampled.csv')

	
	upwell_resampled_lag3.index = upwell_resampled_lag3.index.year 
	upwell_resampled_lag3.index += 3
	with open('pickle_data/upwell_resampled_lag3.pkl', 'w') as f:
		pickle.dump(upwell_resampled_lag3, f)
	upwell_resampled_lag3.to_csv('csv_data/upwell_resampled_lag3.csv')
	return None


if __name__ == '__main__':
	with open('pickle_data/upwell_monthly.pkl', 'r') as f:
		upwell_df = pickle.load(f)
	with open('pickle_data/areas_seasonal.pkl', 'r') as f:
		seasonal = pickle.load(f)
	# plot_cumulative_pdo()
	upwell_monthly = upwell_df['lat_42']
	port_area = 'Eureka'

	cross_cors =  cross_corr(upwell_monthly, port_area)

	
	top_result = cross_cors[cross_cors['port area'] == port_area].iloc[-1]


	upwell_resampled_lagged = lag_samples(seasonal, port_area, upwell_monthly, top_result['resample month'],  top_result['lag_years'], return_df = True)



	lmodel_plot(upwell_resampled_lagged, port_area)
	# R-squared:                       0.258
	write = False
	# if write:
	# 	write_upwell_files(upwell_monthly)
