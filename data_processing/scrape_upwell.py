# upwelling_scrape.py
'''
Scrapes NOAA monthly data for 1946-present for latitudes 42 and 39, and writes them to a csv file in the /csv_data folder.  

INPUT:
None

OUTPUT:
merged_df is PeriodIndexed with monthly frequency, with float cols: 'lat_42', 'lat_39'

The csv file with the merged_df written to it can be accessed with:
pd.read_csv('csv_data/upwell.csv', index_col=0)
'''

import requests
import pandas as pd
import cPickle as pickle

def scrape_upwell():
	url = 'http://www.pfeg.noaa.gov/products/PFELData/upwell/monthly/upindex.mon'
	r = requests.get(url)

	lines = r.content.split('\n')
	header = filter(lambda x: x.startswith('POSITION'), lines)
	header = header[0].split()
	lat_42 = filter(lambda x: x.startswith('42N'), lines)
	lat_39 = filter(lambda x: x.startswith('39N'), lines)

	lat_42 = [line[8:].split() for line in lat_42]
	lat_39 = [line[8:].split() for line in lat_39]
	return lat_42, lat_39, header

def make_period_indexed_series(lat_list, header):
	'''
	INPUT:
	lat_list: list of upwelling index values for a particular latitude
	header: list of colnames that was scraped from the header of upwelling index webpage

	OUTPUT:
	DataFrame of the upwelling, PeriodIndexed, of float type so it can be merged
	'''
	df = pd.DataFrame(lat_list, columns = header)
	df.set_index('POSITION', inplace = True)
	df = df.T.unstack()

	start = '-'.join(df.index[0])
	end = '-'.join(df.index[-1]) 
	df.index = pd.PeriodIndex(start=start, end =end)
	lat = lat_list
	return pd.DataFrame(df, columns = ['upwell'], dtype = float)

def main(write_to_csv = True, pickle_it = True):
	'''
	INPUT: 
	write_to_csv: boolean --  write to csv or not

	OUTPUT:
	merged_df with upwelling latitude columns
	'''
	lat_42, lat_39, header = scrape_upwell()
	df_39 =  make_period_indexed_series(lat_39, header)
	df_42 =  make_period_indexed_series(lat_42, header)
	merged_df = pd.merge(df_42, df_39,left_index=True, right_index=True)
	merged_df.columns = ['lat_42', 'lat_39']
	if write_to_csv:
		merged_df.to_csv('csv_data/upwell_monthly.csv')
	if pickle_it:
		with open('pickle_data/upwell_monthly.pkl', 'w') as f:
			pickle.dump(merged_df, f)
	return merged_df


if __name__ == '__main__':
	upwell_df = main(write_to_csv = True, pickle_it = True)
