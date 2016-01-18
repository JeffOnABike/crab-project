# modeling with PDO:
import numpy as np
import pandas as pd
import cPickle as pickle
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats.kde import gaussian_kde
import statsmodels.api as sm
import scipy.stats as scs


def plot_cumulative_pdo(pdo_monthly):
	'''
	Looks at overall trends in the PDO change over time as evidenced by cumulative sum of the monthly pdo 
	INPUT:
	pdo_monthly: pandas Series - a monthly period-indexed of monthly pdo measurements
	OUTPUT:
	None
	'''
	pdo_cumsum = pdo_monthly.cumsum()
	pdo_cumsum.plot()
	plt.title('Cumulative PDO measurements')
	plt.show()
	return None

def plot_hot_cold_hist(new_df, port):
	cold =  new_df[new_df['pdo'] < 0][port]
	hot =  new_df[new_df['pdo'] > 0][port]

	print
	print 'compare samples from hot and cold periods...'
	print 'two sample independent t-test results:'
	print scs.ttest_ind(hot, cold)
	print

	# make some kdes!
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
	plt.savefig('images/hot_cold_hist.png')
	plt.show()
	return None

def plot_landings_vs_lagged(seasonal, port, pdo_annual, lag_years):
	seasonal[port].ix[1945:].plot(label = 'landings at %s' % port)
	pdo_annual.ix[1945:].plot(label = 'pdo lagged by %d years' % lag_years)
	plt.title('Landings compared to Lagged PDO', {'fontsize': 16})
	plt.xlabel('Season')
	plt.ylabel('Landings (millions of pounds)', {'fontsize': 16})
	plt.legend()
	plt.savefig('images/line_pdo_eureka.png')
	plt.show()
	return None

def plot_lmodel_predictions(new_df, port_area):
	'''
	new_df: pandas DataFrame with column IDing port area 
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
	Lags the pdo variable annually sampling and lagging it lag_years. Also allows for a plot to be returned
	'''
	pdo_annual = pdo.resample('A-' + month, how = 'sum')
	pdo_annual.index = pdo_annual.index.year
	pdo_annual.index += lag_years

	# merge the lagged exogenous variable with the response
	df_p = pd.DataFrame(pdo_annual)
	df_s = pd.DataFrame(seasonal[port])
	new_df = pd.merge(df_s, df_p, left_index = True, right_index = True)
	new_df.columns = [port, 'pdo']

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
	INPUT: 
	pdo_monthly: pandas Series - a monthly period-indexed of monthly pdo measurements
	seasonal: pandas DataFrame - an integer-indexed with columns representing landings (inMlb) by port
	return_df: boolean - return the results as a DataFrame
	OUTPUT:
	
	'''
	months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

	results=[]
	for lag_years in range(0,6):
		for month in months:
			for port in seasonal:
				corr = lag_samples(seasonal, port, pdo_monthly, month, lag_years, plot = False)
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

def write_pdo_resampled(pdo_monthly):
	pdo_resampled = pdo_monthly.resample('A-OCT')
	pdo_resampled.index = pdo_resampled.index.year 
	## THIS IS NOT LAGGED!
	with open('pickle_data/pdo_resampled.pkl', 'w') as f:
		pickle.dump(pdo_resampled, f)
	pdo_resampled.to_csv('csv_data/pdo_resampled.csv')

	#THIS IS LAGGED
	pdo_resampled_lag4 = pdo_resampled.copy()
	pdo_resampled_lag4.index += 4
	with open('pickle_data/pdo_resampled_lag4.pkl', 'w') as f:
		pickle.dump(pdo_resampled_lag4, f)
	pdo_resampled_lag4.to_csv('csv_data/pdo_resampled_lag4.csv')

if __name__ == '__main__':
	# Load the data
	with open('pickle_data/pdo_monthly.pkl', 'r') as f:
		pdo_monthly = pickle.load(f)
	with open('pickle_data/areas_seasonal.pkl', 'r') as f:
		areas_seasonal = pickle.load(f)

	plot_cumulative_pdo(pdo_monthly)
	cross_cors = crosscorrelate_pdo_seasonal(pdo_monthly, areas_seasonal, return_df = True)
#      lag_years resample month port area      corr
# 227          4            OCT    eureka -0.379281

	port_area = 'Eureka'
	top_result = cross_cors[cross_cors['port area'] == port_area].iloc[0]
	new_df = lag_samples(areas_seasonal, port_area, pdo_monthly, top_result['resample month'],  top_result['lag_years'], return_df = True)
	plot_lmodel_predictions(new_df, port_area)

	write = False
	# if write:
	# 	write_pdo_resampled(pdo_monthly)





	# how's sanfrancisco look?
	# cross_cors = crosscorrelate_pdo_seasonal(pdo_monthly, areas_seasonal, return_df = True)
	# port_area = 'San Francisco'
	# top_result = cross_cors[cross_cors['port area'] == port_area].iloc[0]
	# new_df = lag_samples(areas_seasonal, port_area, pdo_monthly, top_result['resample month'],  top_result['lag_years'], return_df = True)
	# plot_lmodel_predictions(new_df, port_area)

