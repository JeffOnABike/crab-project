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
land_ts <- ts(eureka_data, start = eureka_years[1])


pdo_data <- read.csv('R_data/pdo.csv', header = FALSE)
pdo <- pdo_data[2]
pdo_dates <- pdo_data[1]
pdo_ts <- ts(pdo, start = pdo_dates$V1[1])

#merged_ts = ts.intersect(landings = land_ts, pdo = pdo_ts)
start_yr <- start_window <- 1945
pred_vec <- numeric()
year_vec <- numeric()
real_vec <- numeric()
MAE_vec <- numeric()
model_vec <- character()
# training on previous 20 years, make next year prediction
for (end_yr in 1970:2009) { 
        pdo_applic = window(pdo_ts, start = start_window, end = end_yr)
        land_applic = window(land_ts, start = start_window, end = end_yr)
        test_yr = end_yr + 1
        
        #data.train = window(ts.data, start = start_yr, end = end_yr)
        data.test = window(land_ts,start = test_yr)[1]
        pdo.test = window(pdo_ts,start = test_yr)[1]
        
        arima_ex = auto.arima(land_applic, trace = TRUE, xreg = pdo_applic, ic ='aic')
        
        arima_ex.forecast = forecast.Arima(arima_ex, xreg = pdo.test,h=1)
        print(arima_ex.forecast)
        model = arima_ex.forecast$method
        # doesnt always work!::
        #pred <- predict(arima1)$pred[1]
        pred = arima_ex.forecast$mean[1]
        # print(arima1.forecast$mean[1])
        year_vec = c(year_vec, test_yr)
        model_vec = c(model_vec, model)
        pred_vec = c(pred_vec, pred)
        real_vec = c(real_vec, data.test)
        MAE_vec = c(MAE_vec, mean(abs(arima_ex$residuals)))
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

##
## FOR ROLLING ORIGIN:
##

# Reset everything:
pred_vec <- numeric()
year_vec <- numeric()
real_vec <- numeric()
MAE_vec <- numeric()
model_vec <- character()

for (start_window in 1950:1989) { 
        end_window = start_window + 20
        pdo_applic = window(pdo_ts, start = start_window, end = end_window)
        land_applic = window(land_ts, start = start_window, end = end_window)
        test_yr = end_window + 1
        
        #data.train = window(ts.data, start = start_yr, end = end_yr)
        data.test = window(land_ts,start = test_yr)[1]
        pdo.test = window(pdo_ts,start = test_yr)[1]
        
        arima_ex = auto.arima(land_applic, trace = TRUE, xreg = pdo_applic, ic ='aic')
        
        arima_ex.forecast = forecast.Arima(arima_ex, xreg = pdo.test,h=1)
        print(arima_ex.forecast)
        model = arima_ex.forecast$method
        # doesnt always work!::
        #pred <- predict(arima1)$pred[1]
        pred = arima_ex.forecast$mean[1]
        # print(arima1.forecast$mean[1])
        year_vec = c(year_vec, test_yr)
        model_vec = c(model_vec, model)
        pred_vec = c(pred_vec, pred)
        real_vec = c(real_vec, data.test)
        MAE_vec = c(MAE_vec, mean(abs(arima_ex$residuals)))
}

print('Rolling Origin ARIMA model results:')
print('in-sample MAE:')
mean(MAE_vec)
plot(MAE_vec)

err_vec = real_vec - pred_vec
print('cross-validated MAE:')
mean(abs(err_vec))
err_vec = real_vec - pred_vec
plot(err_vec)
acf(err_vec)

## ROLLING ORIGIN IS GIVING A HIGHER IN SAMPLE MAE ON 
#AVERAGE BUT A BETTER PREDICTION RECORD FOR OUT_OF SAMPEL