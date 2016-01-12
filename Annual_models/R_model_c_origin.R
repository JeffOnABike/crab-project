library(tseries)
library(forecast)
# library(TSPred)

# load and configure data
data <- read.csv('R_data/eureka_annual.csv', header = FALSE)[2]
dates <- read.csv('R_data/eureka_annual.csv', header = FALSE)[1]
# TS DEFINED BY YEAR END!!!
ts.data = ts(data, start = dates$V1[1], frequency = 1)
pred_vec <- numeric()
year_vec <- numeric()
real_vec <- numeric()
MAE_vec <- numeric()
model_vec <- character()
# training on previous 20 years, make next year prediction
for (end_yr in 1970:2009) { 
        start_yr = 1945
        test_yr = end_yr + 1
        data.train = window(ts.data, start = start_yr, end = end_yr)
        data.test = window(ts.data,start = test_yr)[1]
        arima1 = auto.arima(data.train, trace = FALSE, ic = 'aic')
        model = arima1.forecast$method
        arima1.forecast = forecast.Arima(arima1, h=1)
        print(arima1.forecast)
        # doesnt always work!::
        #pred <- predict(arima1)$pred[1]
        pred = arima1.forecast$mean[1]
        # print(arima1.forecast$mean[1])
        year_vec = c(year_vec, test_yr)
        model_vec = c(model_vec, model)
        pred_vec = c(pred_vec, pred)
        real_vec = c(real_vec, data.test)
        MAE_vec = c(MAE_vec, mean(abs(arima1$residuals)))
}
mean(MAE_vec)
mean(abs(real_vec - pred_vec))
