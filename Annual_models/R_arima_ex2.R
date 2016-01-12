### this script runs constant origin and rolling origin training 
### Rolling origin is 25 years.
### LOOCV testing is performed on 1971 - 2010
### insample MAE and testing MAE are returned 

##
## LOAD DATA HERE. change the PORT in <PORT>_annual.csv
##


##
## LOAD DATA HERE. change the PORT in <PORT>_annual.csv
##
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

pred_vec <- numeric()
year_vec <- numeric()
real_vec <- numeric()
MAE_vec <- numeric()
model_vec <- character()

# CONSTANT ORIGIN
for (end_yr in 1970:2009) { 
        #pdo_applic = window(pdo_ts, start = start_window, end = end_yr)
        #land_applic = window(land_ts, start = start_window, end = end_yr)
        # set training on exogenous
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
        arima_ex2 = auto.arima(eureka_train, trace = FALSE, xreg = exogenous_train, ic ='bic')
        arima_ex3 = arima(x = eureka_train, xreg = exogenous_train, order = c(1,0,0))
        arima_ex2.forecast = forecast.Arima(arima_ex2, xreg = exogenous_test, h=1)
        arima_ex3.forecast = forecast.Arima(arima_ex3, xreg = exogenous_test, h=1)
        print(arima_ex2.forecast)
        print(arima_ex3.forecast)
        print 'Actual observation:'
        print(eureka_test)
        model = arima_ex2.forecast$method
        # doesnt always work!::
        #pred <- predict(arima1)$pred[1]
        pred = arima_ex2.forecast$mean[1]
        # print(arima1.forecast$mean[1])
        year_vec = c(year_vec, test_yr)
        model_vec = c(model_vec, model)
        pred_vec = c(pred_vec, pred)
        real_vec = c(real_vec, eureka_test)
        MAE_vec = c(MAE_vec, mean(abs(arima_ex2$residuals)))
}
print('Constant Origin ARIMA model results:')
print('in-sample MAE:')
mean(MAE_vec)
plot(MAE_vec)


err_vec = real_vec - pred_vec
print('cross-validated MAE:')
mean(abs(err_vec))
err_vec = real_vec - pred_vec
plot(err_vec)
acf(err_vec)
pacf(err_vec)







##
## FOR ROLLING ORIGIN:
##

# Reset everything:
pred_vec <- numeric()
year_vec <- numeric()
real_vec <- numeric()
MAE_vec <- numeric()
model_vec <- character()

start_yr <- 1949
for (end_yr in 1970:2009) { 
        # set training on exogenous
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
        arima_ex2 = auto.arima(eureka_train, trace = TRUE, xreg = exogenous_train, ic ='aic')
        
        arima_ex2.forecast = forecast.Arima(arima_ex2, xreg = exogenous_test, h=1)
        print(arima_ex2.forecast)
        model = arima_ex2.forecast$method
        # doesnt always work!::
        #pred <- predict(arima1)$pred[1]
        pred = arima_ex2.forecast$mean[1]
        # print(arima1.forecast$mean[1])
        year_vec = c(year_vec, test_yr)
        model_vec = c(model_vec, model)
        pred_vec = c(pred_vec, pred)
        real_vec = c(real_vec, eureka_test)
        MAE_vec = c(MAE_vec, mean(abs(arima_ex2$residuals)))
        start_yr <- start_yr + 1
}

print('Rolling Origin ARIMA model results:')
print('in-sample MAE:')
mean(MAE_vec)
plot(MAE_vec)

err_vec = real_vec - pred_vec
print('cross-validated MAE:')
mean(abs(err_vec))

plot(err_vec)
acf(err_vec)

## ROLLING ORIGIN IS GIVING A HIGHER IN SAMPLE MAE ON 
#AVERAGE BUT A BETTER PREDICTION RECORD FOR OUT_OF SAMPEL

#Ljung-Box test the residuals:
Box.test(arima_ex2$residuals, lag=10, type="Ljung-Box")
