PROCESS:
I. LANDINGS DATA processing, saving
1. Run merge_landings_data.py

	pickles:
		ports_monthly.pkl
	writes to csv:
		ports_monthly.csv
	- represents monthly (period indexed) landings in lbs from all uniquely identified ports in as per the raw data*:
		
	description of output:
		PeriodIndex: 1051 entries, 1928-01 to 2015-07
		Freq: M
		Columns: Data columns (total 12 columns): float
			Bodega Bay, Crescent City, Eureka, Fort Bragg, Halfmoon Bay, Los Angeles, Monterey, Morro Bay, San Diego, San Francisco, Santa Barbara, Trinidad

	* 'All' is discarded since it is an aggregation of ports


2.  Run consolidate_monthly.py

	pickles:
		areas_monthly.pkl
	writes to csv:
		areas_monthly.csv
	- represents monthly (period indexed) landings in lbs from 4 port areas*:
		Eureka
		San Francisco
		Monterey
		Santa Barbara

	description of output: 
		PeriodIndex: 1051 entries, 1928-01 to 2015-07
		Freq: M
		Data columns (total 4 columns):
		Eureka           1051 non-null float64
		Monterey         1051 non-null float64
		San Francisco    1051 non-null float64
		Santa Barbara    1051 non-null float64

	* San Diego and Los Angeles are discarded.

3. Run group_by_season.py

	pickles:
		areas_seasonal.pkl
		ports_seasonal.pkl
	writes to csv:
		areas_seasonal.csv
		ports_seasonal.csv

	DIVIDES BY A MILLION 
	Integer indexed aggregation of landings (in MILLIONS of pounds)

	Description of areas_seasonal df:
		Int64Index: 88 entries, 1927 to 2014
		Data columns (total 4 columns)
	Description of ports_seasonal df:
		Data columns (total 12 columns):
		*includes San Diego, Los Angeles

II. LANDINGS EDA:

2. Run basic_eda.py
this opens new_all_landings df,
then reconciles it into the 4 port areas.
it adds a season month and season column for visualization:
-histogram all landings
-barchart by season and port
-monthly landings boxplot
finally it dumps the consolidated data with new cols into new_all_data.pkl [1051 rows x 7 columns]
all months in pounds, 4 port areas + All, S_month, and Season

3. Run basic_modeling.py
opens new_all_data.pkl [1051 rows x 7 columns]
saves to file new_all_landings plot

4. Super dumb model:
opends new_all_landings, groups by season, divides BY MILLION!
runs linear regression on rolling 20 year cycles, uses LOOCV
returns MAE for each port as a dictionary

5. Kinda dumb model:
unpickles seasonal as a dictionarly
always predicts last year, LOOCV
returns MAE or RMSE for each port as dictionary
**material imporvement on super dumb model!

5. Run pdo_explortation:
looks at the ideal alignment of PDO measurements for correlation over the span of 1945:present
plots a bunch of exploratory, then fits a linear model and shows fitted values as well as the summary

6. kinda smart model:
incorportes PDO_A-OCT as a predictive variable along with AR-1