# group by season
import cPickle as pickle
import pandas as pd
'''
Reads in most basic pickled dfs of:
	ports_monthly (all ports)
	areas_monthly (all areas)
'''


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

# season_month = {	1: 3, 2: 4, 3: 5, 4: 6, 5: 7, 6: 8, 7: 9, 8: 10, \
# 				 	9: 11, 10: 12, 11: 1, 12: 2}

# def add_s_month_col(monthly_data):
# 	'''
# 	Performs operation in place!
# 	Returns dataframe with S_Month column
# 	'''
# 	new_col = []
# 	for m in monthly_data.index.month:
# 		new_col.append(season_month[m])
# 	monthly_data['S_Month'] = new_col
# 	return None



if __name__ == '__main__':
	with open('pickle_data/ports_monthly.pkl', 'r') as f:
		ports_monthly = pickle.load(f)
	with open('pickle_data/areas_monthly.pkl', 'r') as f:
		areas_monthly = pickle.load(f)
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