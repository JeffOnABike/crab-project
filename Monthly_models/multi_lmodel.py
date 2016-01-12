# multiple linear regression:
import cPickle as pickle
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
'''
This is a model which looks at only Port, Month, and Year to come up with predictions for Landings.
IT IS APPLIED HERE TO MONTHLY DATA!
'''
with open('pickle_data/areas_monthly.pkl', 'r') as f:
	areas_monthly = pickle.load(f)

# areas monthly has NO EXTRA COLUMNS outside 4 areas

unstacked = areas_monthly.unstack()
# port_names = unstacked.index.levels[0]
# port_labels = unstacked.index.labels[0]

# ports = []
# for label in port_labels:
# 	ports.append(port_names[label])

unstacked = unstacked.reset_index(name = 'Landings')

months = map(lambda x: x.month, unstacked['level_1'])
years = map(lambda x: x.year, unstacked['level_1'])

unstacked['Month'] = months
unstacked['Year'] = years
# unstacked.get_dummies('Month')

dummied_monthly = pd.get_dummies(unstacked, prefix = ['Month', 'Port'], columns = ['Month', 'level_0'])

# drop base levels
dummied_monthly.drop(['level_1', 'Month_10', 'Port_Monterey'], axis = 1, inplace = True)

OLS = LinearRegression()
X = dummied_monthly.drop('Landings', axis = 1)
y = dummied_monthly['Landings']
OLS.fit(X, y)


OLS.score(X, y)
# # R^2 is .158
# In [1000]: mean_absolute_error(y, OLS.predict(X))
# Out[1000]: 317200.73467644985

# min_0_preds = map(lambda x: max(x, 0), OLS.predict(X))
# mean_absolute_error(y, min_0_preds)

# In [1002]: mean_absolute_error(y, min_0_preds)
# Out[1002]: 274429.0394015073


