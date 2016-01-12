# eda with PDO?
import numpy as np
import pandas as pd
import cPickle as pickle
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats.kde import gaussian_kde
from pandas.tools.plotting import lag_plot
from pandas.tools.plotting import autocorrelation_plot

with open('data/new_pdo.pkl', 'r') as f:
	pdo = pickle.load(f)

lag_plot(seasonal['eureka'])
autocorrelation_plot(seasonal['all'].ix[1945:])
'''
Might abandon some of this below?
'''


def season_higher(all_data):
	tuples = zip(all_data.Season, all_data.index.month)
	new_index = pd.MultiIndex.from_tuples(tuples, names = ['Season', 'Month'])
	all_data.index = new_index
	return all_data.drop('Season', axis = 1)

def month_higher(all_data):
	tuples = zip(all_data.index.month, all_data.Season)
	new_index = pd.MultiIndex.from_tuples(tuples, names = ['Month', 'Season'])
	all_data.index = new_index
	return all_data.drop('Season', axis = 1)



def get_seasonal_breakdown(all_data, norm_by_season = True):
	grouped = all_data.groupby('Season').sum()
	if norm_by_season:
		for col in grouped.columns.drop('All'):
			grouped[col] /= grouped['All']
	return grouped

def make_seasonal_plots(grouped):
	(grouped['All']/1000000).plot(kind = 'bar')
	grouped.drop('All', axis = 1).plot()
	plt.show()




'''
The below only look at NON consolidated data
'''

def normalize_by_port(subset,drop_unwanted = True):
	if drop_unwanted:
		drop_cols = non_landing_cols & set(subset.columns)
	else:
		drop_cols = {'Season'}
	subset = subset.drop(drop_cols, axis = 1)
	normed = subset/subset.sum(axis = 0)
	normed = normed.dropna(axis = 1, how = 'all')
	return (normed * 100).round(2).fillna(0)

def normalize_by_month(subset, drop_unwanted = True):
	if drop_unwanted:
		drop_cols = non_landing_cols & set(subset.columns)
	else:
		drop_cols = {'Season'}
	subset = subset.drop(drop_cols, axis = 1)
	normed = (subset.T/subset.sum(axis = 1)).T
	normed = normed.dropna(axis = 1, how = 'all')
	return (normed * 100).round(2).fillna(0)

def analyze_by_season(subset, norm_fxn, drop_unwanted = True):
	season_groups = subset.groupby('Season')
	results = pd.DataFrame(columns = subset.columns.drop('Season'))
	for season in season_groups.groups.iterkeys():
		results = pd.concat([results, norm_fxn(season_groups.get_group(season), drop_unwanted = drop_unwanted)], axis = 0)
	return results.dropna(axis = 1, how = 'all')

# Generalize this one.. might be ok though.
def get_one_port_month_norms():
	test = analyze_by_season(new, normalize_by_port)
	fbragg = test.groupby(test.index.month)['Fort Bragg']
	fbragg.mean().plot(kind = 'bar')
	plt.show()



# test =  all_data[['All', 'Season']]
# test_all = analyze_by_season(test, normalize_by_port, False)
# test_all = test_all['1929':]
# test_xtab = pd.crosstab(test_all.index.year, test_all.index.month, values= test_all.All, aggfunc=sum)

