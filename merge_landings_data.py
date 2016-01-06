import pandas as pd
# import matplotlib.pyplot as plt
# import numpy as np
import cPickle as pickle


def clean_early_data():
	'''
	clean_data returns a period indexed summary of each month's landings by port
	'''
	data = pd.read_csv('raw_data/erdCAMarCatSM_fb3f_4d76_6e3d.csv')
	# format and 
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
		# make new column identifying season Nov - Oct by year that Nov was in
	season = all_data.index.year
	season -= (all_data.index.month <= 10)
	all_data['Season'] = season
	# check amount of seasons:
	# all_data.Season.value_counts()
	return all_data

if __name__ == '__main__':
	early_data = clean_early_data()
	# now get later data
	later_data = combine_later_records()
	all_landings = combine_all_data(early_data, later_data)
	with open('data/all_landings.pkl', 'w') as f:
		pickle.dump(all_landings, f)