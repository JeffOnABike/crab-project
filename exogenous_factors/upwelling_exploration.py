# upwelling_exploration.py:

'''
Performs upwelling index EDA to look for correlations with landings
'''
import numpy as np
import pandas as pd
import cPickle as pickle
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats.kde import gaussian_kde
import statsmodels.api as sm
import scipy.stats as scs



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

	# if plot:
	# ## DO SOME COOL KDEES HERE
	# 	cold =  new_df[new_df['upwell'] < 0][port]
	# 	hot =  new_df[new_df['upwell'] > 0][port]


	# 	# make some kdes!
	# 	x = np.linspace(min(new_df[port]), max(new_df[port]))
	# 	hot_pdf = gaussian_kde(hot)
	# 	cold_pdf = gaussian_kde(cold)

	# 	y = cold_pdf(x)
	# 	cold.hist(color = 'b', alpha = .2, normed=True, bins = 15)
	# 	plt.plot(x,y, 'b', label = 'cold')
		
	# 	y = hot_pdf(x)
	# 	hot.hist(color = 'r', alpha = .2, normed = True, bins = 15)
	# 	plt.plot(x,y, 'r', label = 'hot')

	# 	plt.legend()
	# 	plt.show()

	if plot:
		new_df.plot(kind = 'scatter', x = 'upwell', y = port)
		plt.show()

	if return_df:
		return new_df.ix[1945:]
	# we care most about correllation from 1945 on
	return new_df.ix[1945:].corr().ix[1][0]

# Grid search for best correlations:
def transform_pdo(upwell_monthly):
	months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
	results=[]
	for lag_years in range(1,6):
		for month in months:
			for port in seasonal:
				corr = lag_samples(seasonal, port, upwell_monthly, month, lag_years, plot = False)
				results.append([lag_years, month, port, corr])
	df_results = pd.DataFrame(results, columns = ['lag_years', 'resample month', 'port area', 'corr']).sort_values(by = 'corr')
	return df_results

# we can pick out the predictive feature to be OCT 4 years prior
#      lag_years resample month port area      corr
# 227          4            OCT    eureka -0.379281
# 226          4            OCT       all -0.375394

if __name__ == '__main__':
	with open('pickle_data/upwell_monthly.pkl', 'r') as f:
		upwell_df = pickle.load(f)
	with open('pickle_data/areas_seasonal.pkl', 'r') as f:
		seasonal = pickle.load(f)
	# plot_cumulative_pdo()
	upwell_monthly = upwell_df['lat_42']
	results =  transform_pdo(upwell_monthly)
	port_area = 'Eureka'
	upwell_resampled = lag_samples(seasonal, port_area, upwell_monthly, 'AUG', 3, return_df = True)

	l_model = sm.OLS(upwell_resampled[port_area], sm.add_constant(upwell_resampled['upwell'])).fit()
	upwell_resampled[port_area].plot()
	l_model.fittedvalues.plot()
	plt.show()
	print l_model.summary()
# R-squared:                       0.258

	
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

# import pandas as pd
# import statsmodels.api as sm

# upwell_df = pd.read_csv('csv_data/upwell.csv', index_col=0)
# upwell_df.index = upwell_df.index.to_datetime()

# statsmodels.tsa.stattools.ccf(x, y)
# x = upwell_df.lat_42
# y = upwell_df.lat_39

# # get the landings monthly data
# with (open('data/new_all_data.pkl','r')) as f:
#     everything_monthly = pickle.load(f)

# all_monthly = everything_monthly['All']
# all_monthly.index = all_monthly.index.to_datetime()

# # ALIGN timeseries
# aligned = pd.concat([x,all_monthly], join = 'inner', axis = 1)

# aligned['lat_42'], aligned['All']
# sm.tsa.stattools.ccf(aligned['lat_42'], aligned['All'])

# aligned.resample('A-NOV', how = 'sum')

# eureka_monthly.to_csv('csv_data/eureka_monthly.csv')

# '''
# NEW CODE
# '''
# eureka = seasonal['Eureka']
# joined = pd.concat([eureka, df], join= 'inner', axis = 1)