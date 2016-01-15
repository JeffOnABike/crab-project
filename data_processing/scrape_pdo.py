'''
Scrape the source of Pacific Decadal Oscillation readings
'''
import numpy as np
import pandas as pd
import requests
import cPickle as pickle

def scrape_site(url):
	r = requests.get(url)
	text = r.text.split('\n')
	return text

def build_dataframe(text):
	head = filter(lambda x: x.startswith('YEAR'),text)[0]
	head_ind = text.index(head)
	months = head.split()[1:]
	months = map(lambda x: x.capitalize(), months)

	data = []
	years = []
	for line in text[(head_ind + 2):]:
	    if line == '':
	        break
	    new_line = line.split()
	    year = new_line.pop(0)
	    years.append(year.strip('*'))
	    data.append(new_line)

	df = pd.DataFrame(data, index = years, columns = months, dtype = float)
	return df

def make_timeseries(df):
	ser = df.T.unstack().dropna()

	start_date = '-'.join(ser.index[0])
	end_date = '-'.join(ser.index[-1])

	new_index = pd.PeriodIndex(start = start_date, end = end_date, freq = 'm')
	ser.index = new_index
	return ser

if __name__ == '__main__':
	url = 'http://research.jisao.washington.edu/pdo/PDO.latest'
	text = scrape_site(url)
	df = build_dataframe(text)
	ser = make_timeseries(df)
	with open('pickle_data/pdo_monthly.pkl', 'w') as f:
		pickle.dump(ser, f)
	ser.to_csv('csv_data/pdo_monthly.csv')
