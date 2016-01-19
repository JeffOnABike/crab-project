# upwelling_exploration.py:

'''
Performs upwelling index EDA and transformations to find for correlations with landings
'''
import numpy as np
import pandas as pd
import cPickle as pickle
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm

def make_plots(seasonal, port, upwell_annual, lag_years, new_df):
	'''
	Creates plots of upwelling lagged and resampled to compare the effect on landings

	INPUT:
	seasonal: integer-indexed pandas DataFrame
	port: string
	upwell_annual: integer-indexed pandas DataFrame
	lag_years: integer
	new_df: pandas DataFrame
	'''
	seasonal[port].ix[1945:].plot(label = 'landings at %s' % port)
	(upwell_annual.ix[1945:]/100.).plot(label = 'upwell lagged by %d years' % lag_years)
	plt.title('Resampled, lagged Upwelling *10^-2 vs. Landings')
	plt.legend()
	plt.show()
	new_df.plot(kind = 'scatter', x = 'upwell', y = port)
	plt.title('Resampled, lagged Upwelling vs. Landings')
	plt.show()
	return None

def lag_samples(seasonal, port, upwell_monthly, month, lag_years, plot = True, return_df = False):
	'''
	Transforms upwelling variable by annually sampling and lagging it lag_years, then aligns it with landings as new_df. Returns the new_df for 1945 onward if desired, otherwise returns the correlation of this aligned new_df

	INPUT:
	seasonal: integer-indexed pandas DataFrame 
	port: string 
	upwell_monthly: period-indexed pandas Series
	month: string - abbreviated month
	lag_years: integer
	plot: boolean
	return_df: boolean
	'''
	upwell_annual = upwell_monthly.resample('A-' + month, how='sum')
	upwell_annual.index = upwell_annual.index.year
	upwell_annual.index += lag_years

	df_p = pd.DataFrame(upwell_annual)
	df_s = pd.DataFrame(seasonal[port])
	new_df = pd.merge(df_s, df_p, left_index = True, right_index = True)
	new_df.columns = [port, 'upwell']

	if plot:
		make_plots(seasonal, port, upwell_annual, lag_years, new_df)

	if return_df:
		return new_df.ix[1945:]
	# we care most about correllation from 1945 on
	return new_df.ix[1945:].corr().ix[1][0]


def crosscorrelate_upwell_seasonal(upwell_monthly, seasonal, port):
	'''
	Cross-correlate all annual resamplings going back 6 years with landings, grid-searching for a highest magnitude correlations. Returns best correlations as a dataframe.

	INPUT: 
	upwell_monthly: period-indexed (monthly) pandas Series 
	seasonal: integer-indexed pandas DataFrame 
	port: string
	
	OUTPUT: 
	df_results: pandas Dataframe
	'''
	months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
	results=[]
	for lag_years in range(0,6):
		for month in months:
			for port in seasonal:
				corr = lag_samples(seasonal, port, upwell_monthly, month, lag_years, plot = False, return_df = False)
				results.append([lag_years, month, port, corr])
	df_results = pd.DataFrame(results, columns = ['lag_years', 'resample month', 'port area', 'corr']).sort_values(by = 'corr')

	print
	print 'Highest Magnitude negative correlations:'
	print df_results.head(5)
	print
	print 'Highest Magnitude positive correlations:'
	print df_results[::-1].head(5)
	print
	
	return df_results

def lmodel_plot(upwell_resampled, port_area):
	'''
	Plots linear model based on a realigned DataFrame with pdo as the regressor and landings as the response. Also returns a model summary for inspection.

	INPUT:
	upwell_resampled: integer-indexed pandas DataFrame 
	port_area: string

	'''

	l_model = sm.OLS(upwell_resampled[port_area], sm.add_constant(upwell_resampled['upwell'])).fit()
	upwell_resampled[port_area].plot(label = 'Landings at %s' % port_area)
	l_model.fittedvalues.plot(label = 'Linear Model Fit')
	plt.title('Actual Landings compared to Linear Model')
	plt.xlabel('Season')
	plt.ylabel('Landings (millions of pounds)')
	plt.legend()
	plt.show()
	print l_model.summary()

def write_upwell_files(upwell_monthly):
	'''
	Writes the optimally resampled and lagged pdo measurements to csv and pickle based on cross-correlation results.

	INPUT: 
	upwell_monthly - period-indexed pandas Series
	'''

	upwell_resampled = upwell_monthly.resample('A-AUG', how = 'sum')
	upwell_resampled_lag3 = upwell_resampled.copy()
	upwell_resampled.index = upwell_resampled.index.year

	# write upwell_resampled on AUG to csv
	with open('pickle_data/upwell_resampled.pkl', 'w') as f:
		pickle.dump(upwell_resampled, f)
	upwell_resampled.to_csv('csv_data/upwell_resampled.csv')

	
	upwell_resampled_lag3.index = upwell_resampled_lag3.index.year 
	upwell_resampled_lag3.index += 3
	with open('pickle_data/upwell_resampled_lag3.pkl', 'w') as f:
		pickle.dump(upwell_resampled_lag3, f)
	upwell_resampled_lag3.to_csv('csv_data/upwell_resampled_lag3.csv')
	return None


def work_the_magic(seasonal, upwell_monthly, port_area = 'Eureka', write = False):
	'''
	Calls all functions of this file in succession to explore the best alignment of lagging/resampling upwelling writes resampled and lagged upwelling if indicated.

	INPUT: 
	seasonal: integer-indexed pandas DataFrame
	upwell_monthly: period-indexed pandas Series
	port_area: string
	write: boolean
	'''
	# Cross-correlate the upwelling with the 
	cross_cors =  crosscorrelate_upwell_seasonal(upwell_monthly, seasonal, port_area)
	top_result = cross_cors[cross_cors['port area'] == port_area].iloc[-1]
	optimal_month = top_result['resample month']
	optimal_year = top_result['lag_years']
	upwell_resampled_lagged = lag_samples(seasonal, port_area, upwell_monthly, optimal_month,  optimal_year, return_df = True)
	lmodel_plot(upwell_resampled_lagged, port_area)

	if write:
		write_upwell_files(upwell_monthly)


if __name__ == '__main__':
	# import the data needed for cross-correlation
	with open('pickle_data/upwell_monthly.pkl', 'r') as f:
		upwell_df = pickle.load(f)
	with open('pickle_data/areas_seasonal.pkl', 'r') as f:
		seasonal = pickle.load(f)

	# Use only upwelling from the closest latitude to the port area Eureka
	work_the_magic(seasonal, upwell_df['lat_42'], 'Eureka', write = False)