# SEASONAL EDA
import matplotlib.pyplot as plt
import seaborn as sns
import cPickle as pickle
'''
RUNNING FROM CLI:
run from crab-project directory, not from within this directory!
'''

def main(areas_seasonal, ports_seasonal):
	areas_seasonal.plot(kind = 'bar', stacked = True, figsize = (14,8))
	plt.suptitle('Seasonal Landings by Port Area')
	plt.ylabel('Millions of Pounds')
	plt.savefig('images/stacked_bar.png')
	plt.clf()

	## HISTOGRAM 
	areas_seasonal_tots = areas_seasonal.sum(axis = 1)
	areas_seasonal_tots.hist(bins = range(0, 33))
	plt.suptitle('Histogram of Seasonal Landings')
	plt.xlabel('Millions of Pounds')
	plt.ylabel('Frequency')
	plt.show()

	## AREA PLOT OF PROPORTIONS BY SEASON
	normed_areas_seasonal = 100.0 * (areas_seasonal.T/areas_seasonal_tots).T
	normed_areas_seasonal.plot(kind = 'area')
	plt.suptitle('Percentage of CA landings by Port Area')
	plt.ylabel('Percentage of Season Landings')
	plt.ylim(0,100)
	plt.xlabel('Season')
	plt.show()

	N_to_S = ['Eureka', 'San Francisco', 'Monterey', 'Santa Barbara']
	sns.boxplot(areas_seasonal, order = N_to_S)
	plt.show()

	unwanted_ports = {'Los Angeles', 'San Diego'}
	N_to_S = ['Crescent City', 'Trinidad', 'Eureka', 'Fort Bragg', 'Bodega Bay', 'San Francisco', 'Halfmoon Bay', 'Monterey', 'Morro Bay', 'Santa Barbara', 'Los Angeles', 'San Diego']
	plt.xticks(rotation=45)
	sns.boxplot(ports_seasonal, order = N_to_S) #figsize = (12,8)
	plt.title('Landings Variability by Port')
	plt.xlabel('Ports listed Northernmost to Southernmost')
	plt.ylabel('Millions of Pounds Landed per Season')
	plt.show()

	#THIS IS THE SAME AS AREAS:
	# ports_seasonal.ix[:2001].dropna(how = 'all', axis = 1).plot()

	## LATER STUFF:
	N_to_S = ['Crescent City', 'Trinidad', 'Eureka', 'Fort Bragg', 'Bodega Bay', 'San Francisco', 'Halfmoon Bay', 'Monterey', 'Morro Bay']
	later_ports_seasonal = ports_seasonal.ix[2002:].dropna(how = 'all', axis = 1)
	later_ports_seasonal_tots = later_ports_seasonal.sum(axis = 1)
	later_normed_ports_seasonal = 100.0 * (later_ports_seasonal.T/later_ports_seasonal_tots).T
	later_normed_ports_seasonal[N_to_S[::-1]].plot(kind = 'area', figsize = (10,6))
	plt.legend(bbox_to_anchor = (1.18, .8))
	plt.show()

if __name__ == '__main__':
	
	with open('pickle_data/areas_seasonal.pkl', 'r') as f:
		areas_seasonal = pickle.load(f)

	with open('pickle_data/ports_seasonal.pkl', 'r') as f:
		ports_seasonal = pickle.load(f)

	main(areas_seasonal, ports_seasonal)
