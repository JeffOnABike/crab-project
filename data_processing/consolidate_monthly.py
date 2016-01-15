import numpy as np
import pandas as pd
import cPickle as pickle


port_area = { 'Eureka': ['Crescent City', 'Trinidad', 'Eureka', 'Fort Bragg'], \
			'San Francisco': ['Bodega Bay', 'San Francisco', 'Halfmoon Bay'], \
			'Santa Barbara': ['Morro Bay', 'Santa Barbara'], \
			'Monterey': ['Monterey']
}
unwanted_ports = {'Los Angeles', 'San Diego'}	

def reconcile_ports(all_landings):
	'''
	reconciles old data (1927:) with new data (2002:) by reducing ports to port areas
	'''
	all_data = all_landings.copy()
	for area, ports in port_area.iteritems():
		all_data[area] = all_data[ports].sum(axis = 1)
		drop_cols = set(ports) - {area}
		all_data.drop(drop_cols, axis = 1, inplace = True)
	# all_data['All'] = all_data.drop(non_landing_cols, axis = 1).sum(axis = 1)
	all_data.drop(unwanted_ports, axis = 1, inplace = True)
	return all_data

# non_landing_cols = {'All', 'Season'}
def add_season_col(monthly_data):
	'''
	Performs operation in place!
	Returns dataframe with Season column
	'''
	# make new column identifying season Nov - Oct by year that Nov was in
	season = monthly_data.index.year
	season -= monthly_data.index.month <= 10
	monthly_data['Season'] = season
	return None

def write_seasonally_grouped(ports_monthly, areas_monthly):
	add_season_col(areas_monthly)
	add_season_col(ports_monthly)

	mil = 1000000.
	ports_seasonal = ports_monthly.groupby('Season').sum()/mil
	areas_seasonal = areas_monthly.groupby('Season').sum()/mil

	# write seasonally aggregated data to files:
	with open('pickle_data/ports_seasonal.pkl', 'w') as f:
		pickle.dump(ports_seasonal, f)
	with open('pickle_data/areas_seasonal.pkl', 'w') as f:
		pickle.dump(areas_seasonal, f)			
	ports_seasonal.to_csv('csv_data/ports_seasonal.csv')
	areas_seasonal.to_csv('csv_data/areas_seasonal.csv')
	return None


if __name__ == '__main__':
	# open pickled dataframe of ports monthly
	with open('pickle_data/ports_monthly.pkl', 'r') as f:
		ports_monthly = pickle.load(f)

	# reduce unique ports to port areas other than unwanted ports
	areas_monthly = reconcile_ports(ports_monthly)

	# write consolidated area and season data to csv/pickle
	write = False
	if write:
		areas_monthly.to_csv('csv_data/areas_monthly.csv')
		with open('pickle_data/areas_monthly.pkl', 'w') as f:
			pickle.dump(areas_monthly, f)
		write_seasonally_grouped(ports_monthly, areas_monthly)




	# plot_all_years_one_col(areas_monthly, port = None)
	# make_monthly_boxplot(areas_monthly, port = 'All')
