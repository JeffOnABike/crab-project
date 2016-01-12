### IGNORE FILE

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
# import seaborn as sns

crab = pd.read_csv('raw_data/erdCAMarCatSM_fb3f_4d76_6e3d.csv')

def clean_crab(crab):
	# drop first row (UTC...)
	crab.drop(0, axis = 0, inplace=True)

	#cleaning
	# crab['time'] = pd.to_datetime(crab.time)
	# crab['landings'] = crab.landings.astype(int)
	new_index = pd.DatetimeIndex(crab['time'])

	crab_by_port = pd.crosstab(new_index, crab['port'], values = crab['landings'], aggfunc = sum)
	crab_by_port.drop('All', axis =1, inplace = True)

	new_series = crab_by_port.index.year
	new_series -= (crab_by_port.index.month <= 10)
	crab_by_port['Season'] = new_series

	return crab_by_port.astype(int)

	# crab.set_index('time', drop = True, inplace=True)
	# crab.drop('fish', axis = 1, inplace = True)x

crab = crab.ix[:-2]
crab = crab[crab['Season'] > 1927]
crab.drop(['Los Angeles', 'San Diego'], axis = 1, inplace = True)
# crab = pd.get_dummies(crab)
# ports = crab.columns[2:]

# crab.groupby('port').sum()

# totals = crab[crab['port'] == 'All']
# totals_by_cal_year = totals.groupby('year').sum()

# nontotals = crab[crab['port'] != 'All']
# nontotals_by_cal_year = nontotals.groupby('year').sum()

# check if all totals are real totals!
#totals_by_cal_year == nontotals_by_cal_year 


def fetch_season_subset(data, start_year, end_year):
	range_start = str(start_year) + '-11-01'
	range_end = str(end_year) + '-09-01'
	return data[range_start: range_end]

def fetch_season_total(data, start_year):
	year_subset = fetch_season_subset(data, start_year, start_year+1)
	total = year_subset['landings'].sum()
	print str(total/1000000.) + ' million pounds landed from %d to %d' % (start_year, start_year + 1)

def fetch_regional_N_or_C_total(data, region, start_year):
	# northern_regions = ['Eureka']
	# southern_regions = ['Santa Barbara', 'Los Angeles', 'San Diego', 'San Francisco', 'Monterey']
	if region not in ['N', 'C']:
		return 'Not a valid region. Pick N or C'
	# mask = data['port'].isin(northern_regions)
	mask =  data['port'] == 'Eureka'
	if region == 'C':
		mask = ~mask
	regional_subset = data[mask]

	print 'in region of %s California...' % region
	return fetch_season_total(regional_subset, start_year)

# def load_dfg_landings_data():
# 	pd.read_excel(sheetname = 'Sheet 1', skiprows = 9, index_col = 0)


records_0206 = pd.read_excel('data/Dcrab_Month&Port_2002-2015.xlsx', sheetname = '2002-2006')
records_0610 = pd.read_excel('data/Dcrab_Month&Port_2002-2015.xlsx', sheetname = '2006-2010')
records_1015 = pd.read_excel('data/Dcrab_Month&Port_2002-2015.xlsx', sheetname = '2010-2015')


unnamed = ['Unnamed: 10', 'Unnamed: 20', 'Unnamed: 30']
unnamed2 = ['Unnamed: 10', 'Unnamed: 20', 'Unnamed: 31', 'Unnamed: 41']
def clean_record(record, unnamed_list):
	cleaned_record = record.set_index('Port Area').T

	cleaned_record = cleaned_record.ix[cleaned_record.index.drop(unnamed_list)]
  	
	cleaned_record.index = pd.DatetimeIndex(cleaned_record.index)

	cleaned_record = cleaned_record.resample('M')

  	# np.apply_along_axis(pd.isnull, 0, records_1015.T)
  	# records_0206.set_index('Port Area').T
  	# pd.PeriodIndex(records_0206.index, freq='m')
  	return cleaned_record

records_0206 = clean_record(records_0206, unnamed)
records_0610 = clean_record(records_0610, unnamed)
records_1015 = clean_record(records_1015, unnamed2)
records = [records_0206, records_0610, records_1015]

records_0215 = pd.concat(records, axis = 0)#.fillna(0)
	  	# records_0215 = pd.concat([records_0206.set_index('Port Area').T, records_0610.set_index('Port Area').T, records_0206.set_index('Port Area').T], axis = 0)
records_0215 = records_0215.resample('M')
# cleaned_record.index = pd.PeriodIndex(cleaned_record.index, freq = 'm')

new_series = records_0215.index.year
new_series -= (records_0215.index.month <= 10)
records_0215['SEASON'] = new_series

records_0215.groupby('SEASON').sum()

def new_ports():
	ports = []
	for port in records_0215.columns[:-1]:
	    lil_list = []
	    for word in port[1:].split():
	    	lil_list.append(word[0]+ word[1:].lower())
	    ports.append(' '.join(lil_list))
	return np.array(ports)

port_list = new_ports
port_list.append(u'Season')

records_0215.columns = port_list

northern = [u'Crescent City', u'Trinidad', u'Eureka', u'Fort Bragg', 'Season']
southern = ['Bodega Bay', 'San Francisco', 'Halfmoon Bay', 'Monterey', 'Morro Bay', 'Season']


## THE BELOW REPRESENT THE SAME DATA AS IN THE 2011 report, save for 2010-2011 season which I have much highter data for!
n_totals = records_0215[northern].groupby('Season').sum().sum(axis = 1)/1000000
s_totals = records_0215[southern].groupby('Season').sum().sum(axis = 1)/1000000

grouped_seasons = records_0215.groupby('Season').sum()/1000000


new_records['Eureka'] = records_0215[['Crescent City', 'Trinidad', 'Eureka', 'Fort Bragg']].sum(axis =1)
new_records['San Francisco'] = records_0215[['Bodega Bay', 'San Francisco', 'Halfmoon Bay']].sum(axis = 1)
new_records['Santa Barbara'] = records_0215['Morro Bay'] # santa barbara too!?
new_records['Monterey'] = records_0215['Monterey']
new_records['Season'] = records_0215['Season']

master = pd.concat([crab, new_records], axis = 0)
master = master.fillna(0)
master.index = pd.PeriodIndex(master.index, freq = 'm')
master.groupby('Season').sum().plot()