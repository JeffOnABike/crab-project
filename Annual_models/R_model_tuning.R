library(tseries)
library(forecast)
# library(TSPred)

# load and configure data
data <- read.csv('R_data/all_annual.csv', header = FALSE)[2]
dates <- read.csv('R_data/all_annual.csv', header = FALSE)[1]
# TS DEFINED BY YEAR END!!!
ts.data = ts(data, start = dates$V1[1], frequency = 1)
pred_vec <- numeric()
year_vec <- numeric()
real_vec <- numeric()
model_vec <- character()
# training on previous 20 years, make next year prediction
for (start_yr in 1980:1990) { 
        end_yr = start_yr + 19
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
}

mean(abs(real_vec - pred_vec))


write.csv(result_vec, file = 'BICpreds_85_04.csv')

plot(ts.data)
data.train = window(ts.data, start = 1944, end = 1984)
plot(data.train)
data.test = window(ts.data, start = 1985)

# trace shows all kinds entertained. ic is the criteria for selection
arima1 = auto.arima(data.train, trace = TRUE, test = 'kpss', ic = 'bic')
arima2 = auto.arima(data.train, trace = TRUE, test = 'kpss', ic = 'aic')
summary(arima1)
confint(arima1)
summary(arima2)
confint(arima2)
# arima1 looks better based on confints of the coefficients (arima1)
# although arima 2 has better training RMSE

plot.ts(arima1$residuals)
hist(arima1$residuals)

## CHECK OUT SOME DIAGNOSTICS
#Ljung-Box test: hi X-sq = good p-value shows no autocorrelation among residuals
Box.test(arima1$residuals, lag=10, type='Ljung-Box')
Box.test(arima2$residuals, lag=20, type='Ljung-Box')
# Check the autocorrelations on the squared residuals
acf(arima1$residuals^2, lag.max = 30)
acf(arima2$residuals^2, lag.max = 30)

# Jarque Bera: are residuals normal? p<0.05 if so!
jarque.bera.test(arima1$residuals)
jarque.bera.test(arima2$residuals)

# get next two forecasts for each model:
arima1.forecast = forecast.Arima(arima1, h=2)
arima2.forecast = forecast.Arima(arima2, h=2)
plot(arima1.forecast)
plot(arima2.forecast)

# get a single point forecast:
arima1.forecast = forecast.Arima(arima1, h=1)
arima2.forecast =  forecast.Arima(arima1, h=1)

### NEED TO INSTALL # library(TSPred) TO DO BETTER VISUALIZATION OF NEXT PRED