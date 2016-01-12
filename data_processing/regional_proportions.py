# regional proportions by month
with open('data/new_all_landings.pkl', 'r') as f:
	monthly_landings = pickle.load(f)

non_landing_cols = {'Season', 'All'} #used to have 'All'
unwanted_ports = {'Los Angeles', 'San Diego', 'All'}	

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

in_season_mask = (monthly_landings.index.month > 10) | (monthly_landings.index.month < 7) 
test = monthly_landings[in_season_mask].drop(unwanted_ports, axis = 1)
analyze_by_season(test, normalize_by_month).plot()

early_monthly = monthly_landings.ix[:'2002-10']
later_monthly = monthly_landings.ix['2002-11':]

later_data[in_season_mask].drop(unwanted_ports, axis = 1 ).plot(kind = 'area')
plt.show()

def make_proportion_plot(monthly_data):
	in_season_mask = (monthly_data.index.month > 10) | (monthly_data.index.month < 7) 
	masked = monthly_data[in_season_mask].drop(unwanted_ports, axis = 1)
	masked = masked.dropna(axis = 1, how = 'all')
	print masked.columns
	normalized = analyze_by_season(masked, normalize_by_month)
	normalized.plot(kind = 'area', figsize = (6,4))
	plt.ylim(0,100)
	plt.draw()
	time.sleep(1)
	plt.pause(.001)
	plt.clf()

for year in range(1945, 1950):
	make_proportion_plot(early_monthly.ix[str(year) + '-11':str(year + 1) + '-10'])
	plt.clf()
plt.close()

