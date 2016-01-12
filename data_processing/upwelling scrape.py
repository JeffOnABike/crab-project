# upwelling scrape
import requests
import pandas as pd

def scrape_upwell():
	url = 'http://www.pfeg.noaa.gov/products/PFELData/upwell/monthly/upindex.mon'
	r = requests.get(url)

	lines = r.content.split('\n')
	header = filter(lambda x: x.startswith('POSITION'), lines)
	header = header[0].split()
	lat_42 = filter(lambda x: x.startswith('42N'), lines)
	lat_39 = filter(lambda x: x.startswith('39N').strip, lines)

	lat_42 = [line[8:].split() for line in lat_42]
	lat_39 = [line[8:].split() for line in lat_39]
	return lat_42, lat_39

def make_period_indexed_series(lat_list):
	
	df = pd.DataFrame(lat_list, columns = header)
	df.set_index('POSITION', inplace = True)
	df = df.T.unstack()

	start = '-'.join(df.index[0])
	end = '-'.join(df.index[-1]) 
	df.index = pd.PeriodIndex(start=start, end =end)
	lat = lat_list
	return pd.DataFrame(df, columns = ['upwell'], dtype = float)

if __name__ == '__main__':
	lat_42, lat_39 = scrape_upwell()
	df_39 =  make_period_indexed_series(lat_39)
	df_42 =  make_period_indexed_series(lat_42)
	pd.merge(df_42, df_39,left_index=True, right_index=True).to_csv('csv_data/upwell.csv')