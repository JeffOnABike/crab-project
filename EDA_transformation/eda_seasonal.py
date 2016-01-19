'''
Perform different perspectives of data visualization on landings data aggregated by season and port areas only

N.B.: run from crab-project directory, not from within this directory!
'''

# SEASONAL EDA
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import cPickle as pickle

def stacked_bar(areas_seasonal, savefig = False):
	'''
	INPUT: 
	areas_seasonal - pandas DataFrame
	savefig - boolean
	'''
	areas_seasonal.plot(kind = 'bar', stacked = True, figsize = (14,8))
	plt.title('Seasonal Landings by Port Area', {'fontsize': 24})
	plt.ylabel('Millions of Pounds', {'fontsize': 16})
	if savefig:
		plt.savefig('images/stacked_bar.png')
	plt.show()
	return None

def eureka_line(areas_seasonal, savefig = False):
	'''
	INPUT: 
	areas_seasonal - pandas DataFrame
	savefig - boolean
	'''
	areas_seasonal['Eureka'].plot(kind = 'line', marker= 'o', figsize = (14,8))
	plt.ylim((0,35))
	plt.title('Seasonal Landings in Eureka Area', {'fontsize': 24})
	plt.ylabel('Millions of Pounds', {'fontsize': 16})
	if savefig:
		plt.savefig('images/eureka_line.png')
	plt.show()
	return None

def histogram_all_ports(areas_seasonal):
	'''
	INPUT: 
	areas_seasonal - pandas DataFrame
	'''
	areas_seasonal_tots = areas_seasonal.sum(axis = 1)
	areas_seasonal_tots.hist(bins = range(0, 33))
	plt.suptitle('Histogram of Seasonal Landings')
	plt.xlabel('Millions of Pounds')
	plt.ylabel('Frequency')
	plt.show()
	return areas_seasonal_tots

def areas_proportion_plot(areas_seasonal, areas_seasonal_tots):
	'''
	Plots seasonal landings by port area proportionally on area graph

	INPUT: 
	areas_seasonal - pandas DataFrame
	areas_seasonal_tots - pandas DataFrame
	'''
	areas_seasonal = areas_seasonal.copy()
	normed_areas_seasonal = 100.0 * (areas_seasonal.T/areas_seasonal_tots).T
	normed_areas_seasonal.plot(kind = 'area')
	plt.suptitle('Percentage of CA Landings by Port Area')
	plt.ylabel('Percentage of Season Landings')
	plt.ylim(0,100)
	plt.xlabel('Season')
	plt.show()
	return None

def areas_boxplot(areas_seasonal, savefig = False):
	'''
	Boxplots the areas landings

	INPUT: 
	areas_seasonal - pandas DataFrame
	beginning_year - integer
	savefig - boolean
	'''

	N_to_S = ['Eureka', 'San Francisco', 'Monterey', 'Santa Barbara']
	sns.boxplot(areas_seasonal.ix[1945:], order = N_to_S)
	plt.title('Seasonal Landings by Port Area', {'fontsize': 16})
	plt.ylabel('Millions of lbs.')
	if savefig:
		plt.savefig('images/areas_boxplot.png')
	plt.show()
	return None

def work_the_magic(areas_seasonal, beginning_year, savefig = False):
	'''
	Calls all the above plotting functions in succession, saves figs if indicated.

	INPUT: 
	areas_seasonal - pandas DataFrame
	beginning_year - integer
	savefig - boolean
	'''
	areas_seasonal = areas_seasonal.ix[beginning_year:]

	# make plots of seasonally, port-area aggregated data
	stacked_bar(areas_seasonal, savefig = savefig)	
	eureka_line(areas_seasonal, savefig = savefig)
	areas_seasonal_tots = histogram_all_ports(areas_seasonal)
	areas_proportion_plot(areas_seasonal, areas_seasonal_tots)
	areas_boxplot(areas_seasonal, savefig = savefig)
	return None

if __name__ == '__main__':
	# load areas_seasonal data from pickle
	with open('pickle_data/areas_seasonal.pkl', 'r') as f:
		areas_seasonal = pickle.load(f)

	# set starting year to subset data ('crab pot era')
	work_the_magic(areas_seasonal, beginning_year = 1945, savefig = False)


	
