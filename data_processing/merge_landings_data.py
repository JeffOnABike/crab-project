'''
merge_landings_data.py reads the respective csv and excel files in the raw_data folder representing different time windows of landings data (1927-2002 and 2002-2014 respectively), and merges them as one dataframe and writes them to pickle and csv objects 'ports_monthly'
'''

import pandas as pd
import cPickle as pickle


def clean_early_data():
	'''
	Returns a period indexed dataframe of each month's landings by port from 1928-01 through 2002-12
	'''
	data = pd.read_csv('raw_data/erdCAMarCatSM_fb3f_4d76_6e3d.csv')
	data.drop(0, axis = 0, inplace=True)
	new_index = pd.PeriodIndex(data['time'], freq = 'm')
	data_by_port = pd.crosstab(index = new_index, columns = data['port'], values = data['landings'], aggfunc = sum)

	return data_by_port.astype(int)


def data_from_excel_sheet(sheet):
	'''
	returns a record in datetime indexed format with ports as columns
	'''
	record = pd.read_excel('raw_data/Dcrab_Month&Port_2002-2015.xlsx', sheetname = sheet)

	# Get rid of some meaningless columns
	unnamed_cols = filter(lambda x: str(x).startswith('Unnamed'),record.columns)
	record.drop(unnamed_cols, axis = 1, inplace = True)

	# pivot data and set index to datetime
	record = record.set_index('Port Area').T
	# record.index = pd.DatetimeIndex(record.index)
	# record = record.resample('m')
  	return record

def combine_later_records():
	'''
	Combines landings data from each excel sheet 
	'''
	sheets = ['2002-2006', '2006-2010', '2010-2015']	
	records = [data_from_excel_sheet(sheet) for sheet in sheets]
	later_data = pd.concat(records, axis = 0)
	
	# get period indexing
	later_data = later_data.resample('m')
	later_data.index = pd.PeriodIndex(later_data.index)

	# fix columns
	new_cols = map(lambda x: x[1:].title(), later_data.columns)
	later_data.columns = new_cols

	return later_data

def combine_all_data(early_data, later_data):
	cutoff_date = later_data.index[0] - 1
	all_data = pd.concat([early_data[:cutoff_date], later_data], axis = 0)
	all_data.drop('All', axis = 1, inplace = True)

	return all_data

if __name__ == '__main__':
	early_years = clean_early_data()
	later_years = combine_later_records()
	# N.B. : all_years_monthly has uniquely identified ports as cols
	all_years_monthly = combine_all_data(early_years, later_years)
	write = False
	if write: 
		all_years_monthly.to_csv('csv_data/ports_monthly.csv')
		with open('pickle_data/ports_monthly.pkl', 'w') as f:
			pickle.dump(all_years_monthly, f)