# modeling with PDO:
import numpy as np
import pandas as pd
import cPickle as pickle
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats.kde import gaussian_kde
import statsmodels.api as sm
import scipy.stats as scs


def plot_hot_cold_hist(new_df, port, savefig = False):
	'''
	Divides seasonal landings into classes of hot seasons (+PDO) and cold seasons 
	(-PDO) at time of resample. Also prints a p-value from a 2 sample t-test 
	between the hot and cold groups.

	INPUT: 
	new_df: integer-indexed pandas DataFrame 
	port: string 
	savefig: boolean 
	'''
	cold =  new_df[new_df['pdo'] < 0][port]
	hot =  new_df[new_df['pdo'] > 0][port]

	print
	print 'compare samples from hot (+PDO) and cold (-PDO) periods...'
	print 'two sample independent t-test results:'
	print 'p value: ', scs.ttest_ind(hot, cold)[1]
	print

	# Generate probability distribution functions for Kernel Density plots
	x = np.linspace(min(new_df[port]), max(new_df[port]))
	hot_pdf = gaussian_kde(hot)
	cold_pdf = gaussian_kde(cold)

	y = cold_pdf(x)
	cold.hist(color = 'b', alpha = .2, normed= True)
	plt.plot(x,y, 'b', label = 'cold seasons')
	
	y = hot_pdf(x)
	hot.hist(color = 'r', alpha = .2, normed = True)
	plt.plot(x,y, 'r', label = 'hot seasons')

	plt.suptitle('Probability Distribution of Eureka Landings') 
	plt.title('Landings 4 years after Hot and Cold Seasons', {'fontsize': 16})
	plt.xlabel('Landings (millions of pounds)', {'fontsize': 16})
	plt.ylabel('Probability', {'fontsize': 16})
	plt.legend()
	if savefig:
		plt.savefig('images/hot_cold_hist.png')
	plt.show()
	return None

def plot_landings_vs_lagged(seasonal, port, pdo_annual, lag_years, savefig = False):
	'''
	Plots the landings against the lagged pdo resampled values from 1945 onward.

	INPUT: 
	seasonal: pandas DataFrame
	port: string
	pdo_annual: integer-indexed pandas Series
	lag_years: integer
	savefig: boolean
	'''

	seasonal[port].ix[1945:].plot(label = 'landings at %s' % port)
	pdo_annual.ix[1945:].plot(label = 'pdo lagged by %d years' % lag_years)
	plt.title('Landings compared to Lagged PDO', {'fontsize': 16})
	plt.xlabel('Season')
	plt.ylabel('Landings (millions of pounds)', {'fontsize': 16})
	plt.legend()
	if savefig:
		plt.savefig('images/line_pdo_eureka.png')
	plt.show()
	return None

def plot_lmodel_predictions(new_df, port_area):
	'''
	Plots linear model based on a realigned DataFrame with pdo as the regressor and 
	landings as the response. Also returns a model summary for inspection.

	INPUT:
	new_df: integer-indexed pandas DataFrame 
	port_area: string

	'''
	l_model = sm.OLS(new_df[port_area], sm.add_constant(new_df['pdo'])).fit()
	new_df[port_area].plot(label = 'Landings')
	l_model.fittedvalues.plot(label = 'Linear Model Fit')
	plt.title('Actual Landings compared to Linear Model')
	plt.xlabel('Season')
	plt.ylabel('Landings (millions of pounds)')
	plt.legend()
	plt.show()

	print
	print 'Model summary on only this exogenous variable:'
	print l_model.summary()

	return None

def lag_samples(seasonal, port, pdo, month, lag_years, plot = True, return_df = False):
	'''
	Lags the pdo variable annually sampling and lagging it lag_years, then aligns 
	it with landings as new_df. Returns the new_df for 1945 onward if desired, 
	otherwise returns the correlation of this aligned new_df

	INPUT:
	seasonal: integer-indexed pandas DataFrame 
	port: string 
	pdo: integer-indexed pandas Series
	month: string - abbreviated month
	lag_years: integer
	plot: boolean
	return_df: boolean
	'''

	# pdo_annual is a resampling of the sum of a year starting from month
	pdo_annual = pdo.resample('A-' + month, how = 'sum')
	pdo_annual.index = pdo_annual.index.year
	pdo_annual.index += lag_years

	# merge the lagged pdo with landings as new_df with port and pdo as cols
	df_p = pd.DataFrame(pdo_annual)
	df_s = pd.DataFrame(seasonal[port])
	new_df = pd.merge(df_s, df_p, left_index = True, right_index = True)
	new_df.columns = [port, 'pdo']

	# if indicated to plot, return visualization of this lag vs. the landings data
	if plot:
		plot_hot_cold_hist(new_df, port)
		plot_landings_vs_lagged(seasonal, port, pdo_annual, lag_years)

	if return_df:
		return new_df.ix[1945:]
	# we care most about correllation from 1945 on
	return new_df.ix[1945:].corr().ix[1][0]

# Grid search for best correlations:
def crosscorrelate_pdo_seasonal(pdo_monthly, seasonal, return_df = False):
	'''
	Cross-correlates pdo resampled with annual frequency across all months, going 
	from present back to 6 years, grid-searching for a highest magnitude 
	correlations. Returns best correlations as a dataframe if desired.

	INPUT: 
	pdo_monthly: period-indexed (monthly) pandas Series 
	seasonal: integer-indexed pandas DataFrame 
	return_df: boolean 
	
	OUTPUT: (optional)
	df_results: pandas Dataframe
	
	'''
	months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', \
	'OCT', 'NOV', 'DEC']

	results=[]
	for lag_years in range(0,6):
		for month in months:
			for port in seasonal:
				corr = lag_samples(seasonal, port, pdo_monthly, month, lag_years, \
					plot = False)
				results.append([lag_years, month, port, corr])
	columns = ['lag_years', 'resample month', 'port area', 'corr']
	df_results = pd.DataFrame(results, columns = columns)
	df_results = df_results.sort_values(by = 'corr')

	print
	print 'Highest Magnitude negative correlations:'
	print df_results.head(5)
	print
	print 'Highest Magnitude positive correlations:'
	print df_results[::-1].head(5)

	if return_df:
		return df_results
	return None

def write_pdo_resampled(pdo_monthly):
	'''
	Writes the optimally resampled and lagged pdo measurements to csv and pickle 
	based on cross-correlation results.

	INPUT: 
	pdo_monthly - period-indexed pandas DataFrame
	'''

	pdo_resampled = pdo_monthly.resample('A-OCT')
	pdo_resampled.index = pdo_resampled.index.year 

	# THIS IS NOT LAGGED!
	with open('pickle_data/pdo_resampled.pkl', 'w') as f:
		pickle.dump(pdo_resampled, f)
	pdo_resampled.to_csv('csv_data/pdo_resampled.csv')

	# THIS IS LAGGED
	pdo_resampled_lag4 = pdo_resampled.copy()
	pdo_resampled_lag4.index += 4
	with open('pickle_data/pdo_resampled_lag4.pkl', 'w') as f:
		pickle.dump(pdo_resampled_lag4, f)
	pdo_resampled_lag4.to_csv('csv_data/pdo_resampled_lag4.csv')
	return None

def work_the_magic(pdo_monthly, areas_seasonal, port_area = 'Eureka', write = False):
	'''
	Calls all functions of this file in succession to explore the best alignment of 
	lagging/resampling PDO writes resampled and lagged pdo if indicated.

	INPUT: 
	pdo_monthly: period-indexed pandas Series
	areas_seasonal: integer-indexed pandas DataFrame
	port_area: string
	write: boolean
	'''
	cross_cors = crosscorrelate_pdo_seasonal(pdo_monthly, areas_seasonal, \
		return_df = True)
	top_result = cross_cors[cross_cors['port area'] == port_area].iloc[0]
	optimal_month = top_result['resample month']
	optimal_year = top_result['lag_years']
	new_df = lag_samples(areas_seasonal, port_area, pdo_monthly, optimal_month, \
		optimal_year, return_df = True)
	plot_lmodel_predictions(new_df, port_area)
	if write:
		write_pdo_resampled(pdo_monthly)
	return None


if __name__ == '__main__':
	# Load the data: pdo monthly and areas_seasonal
	with open('pickle_data/pdo_monthly.pkl', 'r') as f:
		pdo_monthly = pickle.load(f)
	with open('pickle_data/areas_seasonal.pkl', 'r') as f:
		areas_seasonal = pickle.load(f)

	work_the_magic(pdo_monthly, areas_seasonal, port_area, write = False)




