import numpy as np
import pandas as pd
import cPickle as pickle
import matplotlib.pyplot as plt
import seaborn

# Dictionary for subsetting by region
# region = {	'Northern': ['Crescent City', 'Trinidad', 'Eureka', 'Fort Bragg'], \
# 			'Southern': ['Bodega Bay', 'San Francisco', 'Halfmoon Bay', 'Monterey', 'Morro Bay', 'Santa Barbara']
# } 

# Dictionary for subsetting for either old or new data. Use key
region = { 'Eureka': ['Crescent City', 'Trinidad', 'Eureka', 'Fort Bragg'], \
			'San Francisco': ['Bodega Bay', 'San Francisco', 'Halfmoon Bay'], \
			'Santa Barbara': ['Morro Bay', 'Santa Barbara'], \
			'Monterey': ['Monterey'], \
			'All ports': ['Bodega Bay', 'Crescent City', 'Eureka', 'Fort Bragg', \
						'Halfmoon Bay', 'Los Angeles', 'Monterey', 'Morro Bay', \
						'San Diego', 'San Francisco', 'Santa Barbara', 'Trinidad'],\
			'Northern': ['Crescent City', 'Trinidad', 'Eureka', 'Fort Bragg'], \
			'Southern': ['Bodega Bay', 'San Francisco', 'Halfmoon Bay', 'Monterey', \
						'Morro Bay', 'Santa Barbara'], 							
			'Standard': ['Eureka', 'San Francisco', 'Santa Barbara', 'Monterey']					
}

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


non_landing_cols = {'All', 'Season'}
unwanted_ports = {'Los Angeles', 'San Diego'}	
season_month ={1: 3, 2: 4, 3: 5, 4: 6, 5: 7, 6: 8, 7: 9, 8: 10, 9: 11, 10: 12, 11: 1, 12: 2}

# all_landings[regions['Northern'] + ['Season']]
# GRAPH LANDINGS BY TIME
# def subset_data(data, start_season, end_season = None, port_area = 'Standard'):
# 	'''
# 	INPUT:
# 	data: columns include all ports, as well as 'All', 'Season'

# 	OUTPUT:
# 	data_subset: dataframe
# 	start - end seasons (inclusive)
# 	port_subset is formed using the region dictionary
# 	'''
# 	port_subset = region[port_area]
# 	if end_season == None:
# 		end_season = start_season + 1
# 	start_date = str(start_season) + '-11'
# 	end_date = str(end_season) + '-10'
# 	data_subset = data.ix[start_date:end_date][port_subset + list(non_landing_cols)]
# 	return data_subset

## SUBSET FUNCTION might be needed just for a slice of cols, not times..


def subset_on_seasons(data, start_season, end_season = None):
	'''
	Destroys no columns
	Simple slice subset based on start and end seasons
	'''
	if end_season == None:
		end_season = start_season + 1
	start_date = str(start_season) + '-11'
	end_date = str(end_season) + '-10'
	data_subset = data.ix[start_date:end_date]
	return data_subset

def reconcile_data(all_landings):
	'''
	reconciles old data (1927:) with new data (2002:)
	'''
	all_data = all_landings.copy()
	for area, ports in port_area.iteritems():
		all_data[area] = all_data[ports].sum(axis = 1)
		drop_cols = set(ports) - {area}
		all_data.drop(drop_cols, axis = 1, inplace = True)
	all_data['All'] = all_data.drop(non_landing_cols, axis = 1).sum(axis = 1)
	all_data.drop(unwanted_ports, axis = 1, inplace = True)
	return all_data

def add_season_month_col(all_data):
	'''
	Performs operation in place!
	Returns dataframe with S_Month column
	'''
	new_col = []
	for m in all_data.index.month:
		new_col.append(season_month[m])
	all_data['S_Month'] = new_col
	return None

def make_monthly_boxplot(data, port = 'All'):
	ylim = data[port].max()/1000000.
	print ylim
	lst = [data[data['S_Month'] == m][port]/1000000. for m in list(season_month)]
	plt.boxplot(lst)
	plt.ylim(0,ylim)
	plt.show()

## boxplot code:
# for month in season_seq:
# 	month_hi.ix[month].ix[1928:1948]['All'].boxplot()

def plot_all_years_one_col(data, port = None):
	if not port:
		port = ['Eureka', 'San Francisco', 'Santa Barbara', 'Monterey']
	(data.groupby('Season').sum()[port]/1000000).plot(kind = 'bar')
	plt.legend()
	plt.show()

## PIE CHARTS are stupid, but in case:

# def make_pie_chart(season, grouping_dict):
# 	totals = {}
# 	for key, subset in grouping_dict.iteritems():
# 		totals[key] = all_landings.sum()[subset].sum()
# 	df = pd.DataFrame(totals.values(), index = totals.keys())
# 	df.plot(kind = 'pie', subplots = 'True')
# 	plt.show()


def make_hist_landings(data, start_season, end_season):
	season_subset = subset_on_seasons(data, start_season, end_season)
	season_subset.groupby('Season').sum()['All'].hist(bins = 25)
	# all_data['1944':].groupby('Season').sum()['All'].hist(bins = 25)
	plt.show()
#might want to go with something like from rainfall daY??


# def plot_mom(df, col, ax):
#     data = df[col]
#     ax.set_xlabel('Proportion of Season')
#     ax.set_ylabel('Num Seasons')
#     ax.set_title(col)

#     ax.set_xlim(0, 100)
#     ax.set_ylim(0., 80)
#     ax.legend()


# months = df.columns - ['Year']
# months_df = df[months]

# # Use pandas to get the histogram, the axes as tuples are returned
# axes = test_xtab.hist(grid=0, edgecolor='none',
#                     figsize=(15, 10),
#                     layout=(3,4))

# # Iterate through the axes and plot the line on each of the histogram
# for month, ax in zip(months, axes.flatten()):
#     plot_mom(test_xtab, month, ax)

# plt.tight_layout()




if __name__ == '__main__':
	with open('data/new_all_landings.pkl', 'r') as f:
		all_landings = pickle.load(f)
	all_data = reconcile_data(all_landings)
	add_season_month_col(all_data)
	with open('data/new_all_data.pkl', 'w') as f:
		pickle.dump(all_data, f)
	make_hist_landings(all_data, 1928, 1945)
	plot_all_years_one_col(all_data, port = None)
	make_monthly_boxplot(all_data, port = 'All')
