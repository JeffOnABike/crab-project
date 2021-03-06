### this script runs constant origin training 
### LOOCV testing is performed on 1965 - 2014
### insample MAE and testing MAE are returned 
### in addition to final model summary statistics
### and a few graphs of the different models

library(hydroGOF)
library(forecast)


##
## LOAD DATA HERE. change the PORT in <PORT>_annual.csv
##
areas_seasonal <- read.csv('csv_data/areas_seasonal.csv', header = TRUE)
port_area = 'Eureka'
land_data <- areas_seasonal[[port_area]]
land_years <- areas_seasonal$Season
land_ts <- ts(land_data, start = land_years[1])

pdo_lagged <- read.csv('csv_data/pdo_resampled_lag4.csv', header = FALSE)
pdo_data <- pdo_lagged$V2
pdo_years <- pdo_lagged$V1
pdo_ts <- ts(pdo_data, start = pdo_years[1])

upwell_lagged <- read.csv('csv_data/upwell_resampled_lag3.csv', header = FALSE)
upwell_data <- upwell_lagged$V2
upwell_years <- upwell_lagged$V1
upwell_ts <- ts(upwell_data, start = upwell_years[1])

# merge (timeseries intersect) all the data from 1949-2014
merged_ts <- ts.intersect(landings = land_ts, pdo = pdo_ts, upwell = upwell_ts, dframe = TRUE)
start_yr <- max(c(upwell_years[1], pdo_years[1], land_years[1]))

# initialize result vectors*
# * I know there's a better way to do this but it was helpful to keep separate for the models!
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
m8_pred_vec <- numeric()
m9_pred_vec <- numeric()
m0_pred_vec <- numeric()

MAE1_vec <- numeric()
MAE2_vec <- numeric()
MAE3_vec <- numeric()
MAE4_vec <- numeric()
MAE5_vec <- numeric()
MAE6_vec <- numeric()
MAE7_vec <- numeric()
MAE8_vec <- numeric()
MAE9_vec <- numeric()
MAE0_vec <- numeric()

for (end_yr in 1964:2013) { 
        # set training on exogenous and target variables:
        pdo_train = window(merged_ts$pdo, start = start_yr, end_yr)
        upwell_train = window(merged_ts$upwell, start = start_yr, end = end_yr)
        exogenous_train = data.frame(pdo = pdo_train, upwell = upwell_train)
        land_train = window(land_ts, start = start_yr, end = end_yr)
        
        test_yr = end_yr + 1
        # set test:
        land_test = window(land_ts, start = test_yr)[1]
        pdo_test = window(pdo_ts,start = test_yr)[1]
        upwell_test = window(upwell_ts,start = test_yr)[1]
        exogenous_test = data.frame(pdo = pdo_test, upwell = upwell_test)
        
        ##
        ## Model training
        ##
        # AUTO ARIMAS, various optimization parameters (m1 - m3):
        arima_ex2_aicc = auto.arima(land_train, trace = TRUE, xreg = exogenous_train, ic ='aicc', test = 'adf')
        arima_ex2_aic = auto.arima(land_train, trace = TRUE, xreg = exogenous_train, ic ='aicc', test = 'adf')
        arima_ex2_bic = auto.arima(land_train, trace = TRUE, xreg = exogenous_train, ic ='bic', test = 'adf')
        # MA-1 model with exogenous (m4):
        arima_001_mean = Arima(x = land_train, order = c(0,0,1), xreg = exogenous_train)
        # linear regression (m5):
        lin_ex2 <- lm(land_train ~ exogenous_train$pdo + exogenous_train$upwell)
        # plain vanilla autofit arima (m6)
        base_arima = auto.arima(land_train, trace = TRUE, ic ='aicc', test = 'adf')
        ETSmodel <- ets(land_train, opt.crit = 'mae', ic = 'aicc')
        # m8: Arima 100 always
        arima_100_mean = Arima(x = land_train, order = c(1,0,0), include.mean = TRUE)
        #m9:no entry, doesn't need a model (guesses last value)
        # m0:'naive' - guesses cumulative mean
        super_dumb <- lm(land_train ~ 1)
        
        
        ##
        ## Model Forecasting 
        ##
        arima_ex2_aicc.forecast = forecast.Arima(arima_ex2_aic, xreg = exogenous_test, 
                                                 level = c(68.2, 95), h=1)$mean[1]
        arima_ex2_aic.forecast = forecast.Arima(arima_ex2_aicc, xreg = exogenous_test, 
                                                level = c(68.2, 95), h=1)$mean[1]
        arima_ex2_bic.forecast = forecast.Arima(arima_ex2_bic, xreg = exogenous_test, 
                                                level = c(68.2, 95), h=1)$mean[1]
        arima_001_mean.forecast = forecast.Arima(arima_001_mean, xreg = exogenous_test, h = 1)$mean[1]
        lin_ex2.forecast = max(lin_ex2$coefficients[1] + lin_ex2$coefficients[2]*exogenous_test$pdo + 
                                       lin_ex2$coefficients[3]*exogenous_test$upwell)
        base_arima.forecast = forecast.Arima(base_arima)$mean[1]
        ETSmodel.forecast =  predict(ETSmodel)$mean[1]
        arima_100_mean.forecast = forecast.Arima(arima_100_mean, h = 1)$mean[1]
        last_value = tail(land_train, n = 1)[1]
        super_dumb.forecast = max(lm(land_train ~ 1)$coefficients[1])
        
        # show progress on fitting
        print('Generating results for:')
        print(test_yr)        
        print('Actual observation:')
        print(land_test)

        year_vec = c(year_vec, test_yr)
        
        
        # append predictions and real values
        m1_pred_vec = c(m1_pred_vec, arima_ex2_aicc.forecast)
        m2_pred_vec = c(m2_pred_vec, arima_ex2_aic.forecast)
        m3_pred_vec = c(m3_pred_vec, arima_ex2_bic.forecast)
        m4_pred_vec = c(m4_pred_vec, arima_001_mean.forecast)
        m5_pred_vec = c(m5_pred_vec, lin_ex2.forecast)
        m6_pred_vec = c(m6_pred_vec, base_arima.forecast)
        m7_pred_vec = c(m7_pred_vec, ETSmodel.forecast)
        m8_pred_vec = c(m8_pred_vec, arima_100_mean.forecast)
        m9_pred_vec = c(m9_pred_vec, last_value)
        m0_pred_vec = c(m0_pred_vec, super_dumb.forecast)     
        real_vec = c(real_vec, land_test)
        
        # append in-sample MAE 
        MAE1_vec = c(MAE1_vec, mean(abs(arima_ex2_aicc$residuals)))
        MAE2_vec = c(MAE2_vec, mean(abs(arima_ex2_aic$residuals)))
        MAE3_vec = c(MAE3_vec, mean(abs(arima_ex2_bic$residuals))) 
        MAE4_vec = c(MAE4_vec, mean(abs(arima_001_mean$residuals)))
        MAE5_vec = c(MAE5_vec, mean(abs(lin_ex2$resid)))
        MAE6_vec = c(MAE6_vec, mean(abs(base_arima$residuals)))
        MAE7_vec = c(MAE7_vec, mean(abs(ETSmodel$residuals)))
        MAE8_vec = c(MAE8_vec, mean(abs(arima_100_mean$residuals)))
        MAE9_vec = c(MAE9_vec, mean(abs(diff(land_train))))
        MAE0_vec = c(MAE0_vec, mean(abs(super_dumb$resid)))
        
        
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
mean(MAE8_vec)
mean(MAE9_vec)
mean(MAE0_vec)

print('out-of-sample MAE:')
mae(sim = m1_pred_vec, obs = real_vec)
mae(sim = m2_pred_vec, obs = real_vec)
mae(sim = m3_pred_vec, obs = real_vec)
mae(sim = m4_pred_vec, obs = real_vec)
mae(sim = m5_pred_vec, obs = real_vec)
mae(sim = m6_pred_vec, obs = real_vec)
mae(sim = m7_pred_vec, obs = real_vec)
mae(sim = m8_pred_vec, obs = real_vec)
mae(sim = m9_pred_vec, obs = real_vec)
mae(sim = m0_pred_vec, obs = real_vec)

# are residuals of best model significantly different than those of the worst?
t.test(abs(m0_pred_vec-real_vec), abs(m1_pred_vec-real_vec), alternative = 'greater')

# summary and diagnostics on best model
summary(arima_ex2_aicc)
confint(arima_ex2_aicc)
ts.plot(arima_ex2_aicc$residuals, type = 'p', main = 'In-sample Residuals',
        xlab = 'Season', ylab = '(millions lbs)')
acf(arima_ex2_aicc$residuals, main = 'Auto Correlation of In-Sample Residuals')

#check on non-zero coefficients for auto-regressive in residuals:
Box.test(arima_ex2_aic$residuals, lag=20, type="Ljung-Box")

# look at error vec:
errors = real_vec - m1_pred_vec
ts.plot(ts(errors, start = year_vec[1]), type = 'p', main = 'Out of Sample Residuals', ylab = '(million lbs.)')
acf(errors, main = 'Auto Correlation of ARIMA w/ex OOS Errors')
Box.test(errors, type="Ljung-Box")

## GRAPH a few models:

ylab = 'Landings (million lbs.)'
xlab = 'Season'
main = 'Model Predictions vs. Actual'
model = 'ARIMA w/ex'
#the good:
real_ts = ts(real_vec, start = year_vec[1], end=tail(year_vec, n = 1))
ts.plot(real_ts, type = 'l', col = 1, main = main, xlab = xlab , ylab = ylab)
pred_ts = ts(m1_pred_vec, start = year_vec[1] ) #,end=tail(year_vec, n = 1)
lines(pred_ts, type = 'l', col = 'red')
legend('topright', c('Actual', model), lty = c(1,1), col = c(1,'red'))

model = 'OLS'
real_ts = ts(real_vec, start = year_vec[1], end=tail(year_vec, n = 1))
ts.plot(real_ts, type = 'l', col = 1, main = main, xlab = xlab , ylab = ylab)
pred_ts = ts(m5_pred_vec, start = year_vec[1], end=tail(year_vec, n = 1))
lines(pred_ts, type = 'l', col = 'red')
legend('topright', c('Actual', model), lty = c(1,1), col = c(1,'red'))

# the bad:
model = 'ARIMA'
real_ts = ts(real_vec, start = year_vec[1], end=tail(year_vec, n = 1))
ts.plot(real_ts, type = 'l', col = 1, main = main, xlab = xlab , ylab = ylab)
pred_ts = ts(m6_pred_vec, start = year_vec[1], end=tail(year_vec, n = 1))
lines(pred_ts, type = 'l', col = 'red')
legend('topright', c('Actual', model), lty = c(1,1), col = c(1,'red'))

# the ugly:
model = 'Naive'
real_ts = ts(real_vec, start = year_vec[1], end=tail(year_vec, n = 1))
ts.plot(real_ts, type = 'l', col = 1, main = main, xlab = xlab , ylab = ylab)
pred_ts = ts(m0_pred_vec, start = year_vec[1], end=tail(year_vec, n = 1))
lines(pred_ts, type = 'l', col = 'red')
legend('topright', c('Actual', model), lty = c(1,1), col = c(1,'red'))



