### this script runs constant origin and rolling origin training 
### Rolling origin is 22 years. This is based on data availability
### LOOCV testing is performed on 1971 - 2010
### insample MAE and testing MAE are returned 

##
## LOAD DATA HERE. change the PORT in <PORT>_annual.csv
##
library(hydroGOF)

areas_seasonal <- read.csv('csv_data/areas_seasonal.csv', header = TRUE)
eureka_data <- areas_seasonal$Eureka
eureka_years <- areas_seasonal$Season
eureka_ts <- ts(eureka_data, start = eureka_years[1])


pdo_lagged <- read.csv('csv_data/pdo_resampled_lag4.csv', header = FALSE)
pdo_data <- pdo_lagged$V2
pdo_years <- pdo_lagged$V1
pdo_ts <- ts(pdo_data, start = pdo_years[1])

upwell_lagged <- read.csv('csv_data/upwell_resampled_lag3.csv', header = FALSE)
upwell_data <- upwell_lagged$V2
upwell_years <- upwell_lagged$V1
upwell_ts <- ts(upwell_data, start = upwell_years[1])

merged_ts <- ts.intersect(landings = land_ts, pdo = pdo_ts, upwell = upwell_ts, dframe = TRUE)
start_yr <- max(c(upwell_years[1], pdo_years[1], eureka_years[1]))

#pred_vec <- numeric()
year_vec <- numeric()
real_vec <- numeric()

m1_model_vec <- character()

m1_pred_vec <- numeric()
m2_pred_vec <- numeric()
m3_pred_vec <- numeric()
m4_pred_vec <- numeric()
m5_pred_vec <- numeric()
m6_pred_vec <- numeric()
m7_pred_vec <- numeric()

MAE1_vec <- numeric()
MAE2_vec <- numeric()
MAE3_vec <- numeric()
MAE4_vec <- numeric()
MAE5_vec <- numeric()
MAE6_vec <- numeric()
MAE7_vec <- numeric()
#model_vec <- character()

# CONSTANT ORIGIN
for (end_yr in 1964:2013) { 
        # set training on exogenous and target variables:
        pdo_train = window(merged_ts$pdo, start = start_yr, end_yr)
        upwell_train = window(merged_ts$upwell, start = start_yr, end = end_yr)
        exogenous_train = data.frame(pdo = pdo_train, upwell = upwell_train)
        eureka_train = window(eureka_ts, start = start_yr, end = end_yr)
        
        test_yr = end_yr + 1
        # set test:
        eureka_test = window(eureka_ts,start = test_yr)[1]
        ## COME BACK TO SET TEST EXOGENOUS
        pdo_test = window(pdo_ts,start = test_yr)[1]
        upwell_test = window(upwell_ts,start = test_yr)[1]
        exogenous_test = data.frame(pdo = pdo_test, upwell = upwell_test)

        # MOST COMPLEX MODELS:
        arima_ex2_bic = auto.arima(eureka_train, trace = TRUE, xreg = exogenous_train, ic ='bic', test = 'adf')
        arima_ex2_aic = auto.arima(eureka_train, trace = TRUE, xreg = exogenous_train, ic ='aicc', test = 'adf')
        
        # Less Complex Timeseries Models:
        arima_100_mean = Arima(x = eureka_train, order = c(1,0,0), include.mean = TRUE)
        arima_001_mean = Arima(x = eureka_train, order = c(0,0,1), include.mean = TRUE)
        
        # Other models:
        #TSLM?
        #ETS??
        #HOLT WINTERS??!

        #comparison lin regress:
        lin_ex2 <- lm(eureka_train ~ exogenous_train$pdo + exogenous_train$upwell)
        
        # DUMB MODELS
        super_dumb <- lm(eureka_train ~ 1)

        ## FORECASTING ###
        #arima_ex3 = arima(x = eureka_train, xreg = exogenous_train, order = c(0,0,1))
        arima_ex2_aic.forecast = forecast.Arima(arima_ex2_aic, xreg = exogenous_test, h=1)$mean[1]
        arima_ex2_bic.forecast = forecast.Arima(arima_ex2_bic, xreg = exogenous_test, h=1)$mean[1]
        arima_100_mean.forecast = forecast.Arima(arima_100_mean, h = 1)$mean[1]
        arima_001_mean.forecast = forecast.Arima(arima_001_mean, h = 1)$mean[1]
        lin_ex2.forecast = max(lin_ex2$coefficients[1] + lin_ex2$coefficients[2]*exogenous_test$pdo + lin_ex2$coefficients[3]*exogenous_test$upwell)
        last_value = tail(eureka_train, n = 1)[1]
        super_dumb.forecast = max(lm(eureka_train ~ 1)$coefficients[1])
        
        #arima_ex3.forecast = forecast.Arima(arima_ex3, xreg = exogenous_test, h=1)
        #print(kinda_dumb.forecast)
        #print(arima_ex3.forecast)
        print(last_value)
        print('Generating results for:')
        print(test_yr)        
        print('Actual observation:')
        print(eureka_test)
        #model = kinda_dumb.forecast$method
        # doesnt always work!::
        #pred <- predict(arima1)$pred[1]
        #pred = kinda_dumb.forecast$mean[1]
        # print(arima1.forecast$mean[1])
        year_vec = c(year_vec, test_yr)
        #model_vec = c(model_vec, model)
        arima_ex2_aic_model = forecast.Arima(arima_ex2_aic, xreg = exogenous_test, h=1)$method
        m1_model_vec = c(m1_model_vec, arima_ex2_aic_model)
        m1_pred_vec = c(m1_pred_vec, arima_ex2_aic.forecast) 
        m2_pred_vec = c(m2_pred_vec, arima_ex2_bic.forecast)
        m3_pred_vec = c(m3_pred_vec, arima_100_mean.forecast)
        m4_pred_vec = c(m4_pred_vec, arima_001_mean.forecast)
        m5_pred_vec = c(m5_pred_vec, lin_ex2.forecast)
        m6_pred_vec = c(m6_pred_vec, last_value)
        m7_pred_vec = c(m7_pred_vec, super_dumb.forecast)
        
        real_vec = c(real_vec, eureka_test)
        MAE1_vec = c(MAE1_vec, mean(abs(arima_ex2_aic$residuals)))
        MAE2_vec = c(MAE2_vec, mean(abs(arima_ex2_bic$residuals)))
        MAE3_vec = c(MAE3_vec, mean(abs(arima_100_mean$residuals)))
        MAE4_vec = c(MAE4_vec, mean(abs(arima_001_mean$residuals)))
        MAE5_vec = c(MAE5_vec, mean(abs(lin_ex2$resid)))
        MAE6_vec = c(MAE6_vec, mean(abs(diff(eureka_train))))
        MAE7_vec = c(MAE7_vec, mean(abs(super_dumb$resid)))
}

print('Constant Origin ARIMA model results:')
print('in-sample MAE:')

mean(MAE1_vec)
mean(MAE2_vec)
mean(MAE3_vec)
mean(MAE4_vec)
mean(MAE5_vec)
mean(MAE6_vec)
mean(MAE7_vec)

print('out-of-sample MAE:')
mae(sim = m1_pred_vec, obs = real_vec)
mae(sim = m2_pred_vec, obs = real_vec)
mae(sim = m3_pred_vec, obs = real_vec)
mae(sim = m4_pred_vec, obs = real_vec)
mae(sim = m5_pred_vec, obs = real_vec)
mae(sim = m6_pred_vec, obs = real_vec)
mae(sim = m7_pred_vec, obs = real_vec)

t.test(abs(m7_pred_vec-real_vec), abs(m1_pred_vec-real_vec), alternative = 'greater')

m1_model_vec
summary(arima_ex2_aic)
confint(arima_ex2_aic)
ts.plot(arima_ex2_aic$residuals, type = 'p')
acf(arima_ex2_aic$residuals)

#check on non-zero coefficients for auto-regressive in residuals:
Box.test(arima_ex2_aic$residuals, lag=18, type="Ljung-Box")

#jarque.bera.test(arima1$residuals)

## GRAPH!
# the good:
real_ts = ts(real_vec, start = year_vec[1], end=tail(year_vec, n = 1))
ts.plot(real_ts, type = 'l', col = 1)
pred_ts = ts(m1_pred_vec, start = year_vec[1], end=tail(year_vec, n = 1))
lines(pred_ts, type = 'l', col = 2)

# the bad:
real_ts = ts(real_vec, start = year_vec[1], end=tail(year_vec, n = 1))
ts.plot(real_ts, type = 'l', col = 1)
pred_ts = ts(m5_pred_vec, start = year_vec[1], end=tail(year_vec, n = 1))
lines(pred_ts, type = 'l', col = 2)

#the ugly:
real_ts = ts(real_vec, start = year_vec[1], end=tail(year_vec, n = 1))
ts.plot(real_ts, type = 'l', col = 1)
pred_ts = ts(m7_pred_vec, start = year_vec[1], end=tail(year_vec, n = 1))
lines(pred_ts, type = 'l', col = 2)

#interesting side point:
real_ts = ts(real_vec, start = year_vec[1], end=tail(year_vec, n = 1))
ts.plot(real_ts, type = 'l', col = 1)
pred_ts = ts(m6_pred_vec, start = year_vec[1], end=tail(year_vec, n = 1))
lines(pred_ts, type = 'l', col = 2)












##
## FOR ROLLING ORIGIN:
##

# Reset everything:
start_yr <- max(c(upwell_years[1], pdo_years[1], eureka_years[1]))

#pred_vec <- numeric()
year_vec <- numeric()
real_vec <- numeric()

m1_model_vec <- character()
m2_pred_vec <- numeric()
m1_pred_vec <- numeric()
m2_pred_vec <- numeric()
m3_pred_vec <- numeric()
m4_pred_vec <- numeric()
m5_pred_vec <- numeric()
m6_pred_vec <- numeric()
m7_pred_vec <- numeric()

MAE1_vec <- numeric()
MAE2_vec <- numeric()
MAE3_vec <- numeric()
MAE4_vec <- numeric()
MAE5_vec <- numeric()
MAE6_vec <- numeric()
MAE7_vec <- numeric()

for (end_yr in 1970:2009) { 
        # set training on exogenous and target variables:
        pdo_train = window(merged_ts$pdo, start = start_yr, end_yr)
        upwell_train = window(merged_ts$upwell, start = start_yr, end = end_yr)
        exogenous_train = data.frame(pdo = pdo_train, upwell = upwell_train)
        eureka_train = window(eureka_ts, start = start_yr, end = end_yr)
        
        test_yr = end_yr + 1
        # set test:
        eureka_test = window(eureka_ts,start = test_yr)[1]
        ## COME BACK TO SET TEST EXOGENOUS
        pdo_test = window(pdo_ts,start = test_yr)[1]
        upwell_test = window(upwell_ts,start = test_yr)[1]
        exogenous_test = data.frame(pdo = pdo_test, upwell = upwell_test)
        
        # MOST COMPLEX MODELS:
        arima_ex2_bic = auto.arima(eureka_train, trace = TRUE, xreg = exogenous_train, ic ='bic', test = 'adf')
        arima_ex2_aic = auto.arima(eureka_train, trace = TRUE, xreg = exogenous_train, ic ='aic', test = 'adf')
        
        # Less Complex Timeseries Models:
        arima_100_mean = Arima(x = eureka_train, order = c(1,0,0), include.mean = TRUE)
        arima_001_mean = Arima(x = eureka_train, order = c(0,0,1), include.mean = TRUE)
        
        # Other models:
        #TSLM?
        #ETS??
        #HOLT WINTERS??!
        
        #comparison lin regress:
        lin_ex2 <- lm(eureka_train ~ exogenous_train$pdo + exogenous_train$upwell)
        
        # DUMB MODELS
        super_dumb <- lm(eureka_train ~ 1)
        
        ## FORECASTING ###
        #arima_ex3 = arima(x = eureka_train, xreg = exogenous_train, order = c(0,0,1))
        arima_ex2_aic.forecast = forecast.Arima(arima_ex2_aic, xreg = exogenous_test, h=1)$mean[1]
        arima_ex2_bic.forecast = forecast.Arima(arima_ex2_bic, xreg = exogenous_test, h=1)$mean[1]
        arima_100_mean.forecast = forecast.Arima(arima_100_mean, h = 1)$mean[1]
        arima_001_mean.forecast = forecast.Arima(arima_001_mean, h = 1)$mean[1]
        lin_ex2.forecast = max(lin_ex2$coefficients[1] + lin_ex2$coefficients[2]*exogenous_test$pdo + lin_ex2$coefficients[3]*exogenous_test$upwell)
        last_value = tail(eureka_train, n = 1)[1]
        super_dumb.forecast = max(lm(eureka_train ~ 1)$coefficients[1])
        
        #arima_ex3.forecast = forecast.Arima(arima_ex3, xreg = exogenous_test, h=1)
        #print(kinda_dumb.forecast)
        #print(arima_ex3.forecast)
        print(last_value)
        print('Generating results for:')
        print(test_yr)        
        print('Actual observation:')
        print(eureka_test)
        #model = kinda_dumb.forecast$method
        # doesnt always work!::
        #pred <- predict(arima1)$pred[1]
        #pred = kinda_dumb.forecast$mean[1]
        # print(arima1.forecast$mean[1])
        year_vec = c(year_vec, test_yr)
        #model_vec = c(model_vec, model)
        arima_ex2_aic_model = forecast.Arima(arima_ex2_aic, xreg = exogenous_test, h=1)$method
        m1_model_vec = c(m1_model_vec, arima_ex2_aic_model)
        m1_pred_vec = c(m1_pred_vec, arima_ex2_aic.forecast) 
        m2_pred_vec = c(m2_pred_vec, arima_ex2_bic.forecast)
        m3_pred_vec = c(m3_pred_vec, arima_100_mean.forecast)
        m4_pred_vec = c(m4_pred_vec, arima_001_mean.forecast)
        m5_pred_vec = c(m5_pred_vec, lin_ex2.forecast)
        m6_pred_vec = c(m6_pred_vec, last_value)
        m7_pred_vec = c(m7_pred_vec, super_dumb.forecast)
        
        real_vec = c(real_vec, eureka_test)
        MAE1_vec = c(MAE1_vec, mean(abs(arima_ex2_aic$residuals)))
        MAE2_vec = c(MAE2_vec, mean(abs(arima_ex2_bic$residuals)))
        MAE3_vec = c(MAE3_vec, mean(abs(arima_100_mean$residuals)))
        MAE4_vec = c(MAE4_vec, mean(abs(arima_001_mean$residuals)))
        MAE5_vec = c(MAE5_vec, mean(abs(lin_ex2$resid)))
        MAE6_vec = c(MAE6_vec, mean(abs(diff(eureka_train))))
        MAE7_vec = c(MAE7_vec, mean(abs(super_dumb$resid)))
        
        start_yr = start_yr + 1
}


print('Roling Origin ARIMA model results:')
print('in-sample MAE:')

mean(MAE1_vec)
mean(MAE2_vec)
mean(MAE3_vec)
mean(MAE4_vec)
mean(MAE5_vec)
mean(MAE6_vec)
mean(MAE7_vec)

print('out-of-sample MAE:')
mae(sim = m1_pred_vec, obs = real_vec)
mae(sim = m2_pred_vec, obs = real_vec)
mae(sim = m3_pred_vec, obs = real_vec)
mae(sim = m4_pred_vec, obs = real_vec)
mae(sim = m5_pred_vec, obs = real_vec)
mae(sim = m6_pred_vec, obs = real_vec)
mae(sim = m7_pred_vec, obs = real_vec)

plot(c(arima_ex2_aic$residuals))
acf(arima_ex2_aic$residuals)
Box.test(arima_ex2_aic$residuals, lag=18, type="Ljung-Box")




