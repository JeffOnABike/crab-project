import numpy as np
import pandas as pd
import cPickle as pickle
import matplotlib.pyplot as plt
import seaborn

# Dictionary for subsetting by region
region = {	'Northern': ['Crescent City', 'Trinidad', 'Eureka', 'Fort Bragg'], \
			'Southern': ['Bodega Bay', 'San Francisco', 'Halfmoon Bay', 'Monterey', 'Morro Bay', 'Santa Barbara']
} 

# Dictionary for subsetting for either old or new data. Use key
port_area = { 'Eureka': ['Crescent City', 'Trinidad', 'Eureka', 'Fort Bragg'], \
			'San Francisco': ['Bodega Bay', 'San Francisco', 'Halfmoon Bay'], \
			'Santa Barbara': ['Morro Bay', 'Santa Barbara'], \
			'Monterey': ['Monterey']
}
## CHeck out with:
# all_landings[:'2002-10'][old_new['San Francisco']].sum()
coordinates =  { 	'Crescent City': (41.7557501, -124.2025913), \
					'Trinidad': (41.059291, -124.1431246), \
					'Eureka': (40.8020712, -124.1636729), \
					'Fort Bragg': (39.445723, -123.8052935), \
					'Bodega Bay': (38.33325, -123.0480571), \
					'San Francisco': (37.7749295, -122.4194155), \
					'Halfmoon Bay': (37.4635519, -122.4285862), \
					'Monterey': (36.6002378, -121.8946761),	\
					'Morro Bay': (35.3659445, -120.8499924), \
					'Santa Barbara': (34.4208305, -119.6981901)
}


# all_landings[regions['Northern'] + ['Season']]
# GRAPH LANDINGS BY TIME
def subset_data(start, end = None, port_subset = all_landings.columns):
	if end == None:
		end = start
	season_list = range(start, end + 1)
	subset = all_landings[all_landings['Season'].isin(season_list)][port_subset + ['Season']]
	return subset


non_landing_cols = {'All', 'Season'}
unwanted_ports = {'Los Angeles', 'San Diego'}	

def consolidate_data(all_landings):
	all_data = all_landings.copy()
	for area, ports in port_area.iteritems():
		all_data[area] = all_data[ports].sum(axis = 1)
		drop_cols = set(ports) - {area}
		all_data.drop(drop_cols, axis = 1, inplace = True)
	all_data['All'] = all_data.drop(non_landing_cols, axis = 1).sum(axis = 1)
	all_data.drop(unwanted_ports, axis = 1, inplace = True)
	return all_data

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
	return results

test = analyze_by_season(new, normalize_by_port)
fbragg = test.groupby(test.index.month)['Fort Bragg']
fbragg.mean().plot(kind = 'bar')


test =  all_data[['All', 'Season']]
test_all = analyze_by_season(test, normalize_by_port, False)
test_all = test_all['1929':]
test_xtab = pd.crosstab(test_all.index.year, test_all.index.month, values= test_all.All, aggfunc=sum)
# def make_pie_chart(season, grouping_dict):
# 	totals = {}
# 	for key, subset in grouping_dict.iteritems():
# 		totals[key] = all_landings.sum()[subset].sum()
# 	df = pd.DataFrame(totals.values(), index = totals.keys())
# 	df.plot(kind = 'pie', subplots = 'True')
# 	plt.show()
def plot_mom(df, col, ax):
    data = df[col]
    ax.set_xlabel('Proportion of Season')
    ax.set_ylabel('Num Seasons')
    ax.set_title(col)

    ax.set_xlim(0, 100)
    ax.set_ylim(0., 80)
    ax.legend()


months = df.columns - ['Year']
months_df = df[months]

# Use pandas to get the histogram, the axes as tuples are returned
axes = test_xtab.hist(grid=0, edgecolor='none',
                    figsize=(15, 10),
                    layout=(3,4))

# Iterate through the axes and plot the line on each of the histogram
for month, ax in zip(months, axes.flatten()):
    plot_mom(test_xtab, month, ax)

plt.tight_layout()


if __name__ == '__main__':
	with open('data/all_landings.pkl', 'r') as f:
		all_landings = pickle.load(f)