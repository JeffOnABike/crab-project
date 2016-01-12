# modeling with PDO:
import numpy as np
import pandas as pd
import cPickle as pickle
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats.kde import gaussian_kde
import statsmodels.api as sm
import scipy.stats as scs
# General Trends

# def plot_cumulative_pdo():
# 	pdo_cumsum = pdo.cumsum()
# 	pdo_cumsum.plot()
# 	plt.title('Cumulative PDO measurements')
# 	# plt.vlines('1977-1', 0, pdo_cumsum.ix['1977'])
# 	# plt.vlines('1945-1', 0, pdo_cumsum.ix['1945'])
# 	plt.show()
# 	return


def lag_samples(seasonal, port, pdo, month, lag_years, plot = True, return_df = False):
	# try mean and sum
	pdo_annual = pdo.resample('A-' + month, how='sum')
	pdo_annual.index = pdo_annual.index.year
	pdo_annual.index += lag_years

	if plot:
		seasonal[port].ix[1945:].plot(label = 'landings at %s' % port)
		pdo_annual.ix[1945:].plot(label = 'pdo lagged by %d years' % lag_years)
		plt.legend()
		plt.show()

	df_p = pd.DataFrame(pdo_annual)
	df_s = pd.DataFrame(seasonal[port])
	new_df = pd.merge(df_s, df_p, left_index = True, right_index = True)
	new_df.columns = [port, 'pdo']

	if plot:
	## DO SOME COOL KDEES HERE
		cold =  new_df[new_df['pdo'] < 0][port]
		hot =  new_df[new_df['pdo'] > 0][port]


		# make some kdes!
		x = np.linspace(min(new_df[port]), max(new_df[port]))
		hot_pdf = gaussian_kde(hot)
		cold_pdf = gaussian_kde(cold)

		y = cold_pdf(x)
		cold.hist(color = 'b', alpha = .2, normed=True, bins = 15)
		plt.plot(x,y, 'b', label = 'cold')
		
		y = hot_pdf(x)
		hot.hist(color = 'r', alpha = .2, normed = True, bins = 15)
		plt.plot(x,y, 'r', label = 'hot')

		plt.legend()
		plt.show()

	# if plot:
	# 	new_df.plot(kind = 'scatter', x = 'pdo', y = port)
	# 	plt.show()

	if return_df:
		return new_df.ix[1945:]
	# we care most about correllation from 1945 on
	return new_df.ix[1945:].corr().ix[1][0]

# Grid search for best correlations:
def transform_pdo(pdo_monthly):
	months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
	results=[]
	for lag_years in range(1,6):
		for month in months:
			for port in seasonal:
				corr = lag_samples(seasonal, port, pdo_monthly, month, lag_years, plot = False)
				results.append([lag_years, month, port, corr])
	df_results = pd.DataFrame(results, columns = ['lag_years', 'resample month', 'port area', 'corr']).sort_values(by = 'corr')
	return df_results.head(10)

# we can pick out the predictive feature to be OCT 4 years prior
#      lag_years resample month port area      corr
# 227          4            OCT    eureka -0.379281
# 226          4            OCT       all -0.375394

if __name__ == '__main__':
	with open('pickle_data/pdo_monthly.pkl', 'r') as f:
		pdo_monthly = pickle.load(f)
	with open('pickle_data/areas_seasonal.pkl', 'r') as f:
		seasonal = pickle.load(f)
	# plot_cumulative_pdo()
	transform_pdo(pdo_monthly)
	port_area = 'Eureka'
	new_df = lag_samples(seasonal, port_area, pdo_monthly, 'OCT', 4, return_df = True)

	l_model = sm.OLS(new_df[port_area], sm.add_constant(new_df['pdo'])).fit()
	new_df[port_area].plot()
	l_model.fittedvalues.plot()
	plt.show()
	print l_model.summary()
	hot = new_df[new_df['pdo']>0][port_area].values
	cold = new_df[new_df['pdo']<0][port_area].values
	print
	print 'compare samples from hot and cold periods...'
	print 'two sample independent t-test results:'
	print scs.ttest_ind(hot, cold)
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