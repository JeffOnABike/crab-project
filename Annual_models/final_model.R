library(forecast)

# Load all the data and transform to time series
port_area <- 'Eureka'
areas_seasonal <- read.csv('csv_data/areas_seasonal.csv', header = TRUE)
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

# merged timeseries has landings, pdo, and upwelling aligned with start year = 1949
merged_ts <- ts.intersect(landings = land_ts, pdo = pdo_ts, upwell = upwell_ts, dframe = TRUE)
start_yr <- max(c(upwell_years[1], pdo_years[1], land_years[1]))

# set result vectors to empty
year_vec <- numeric()
real_vec <- numeric() 
pred_vec <- numeric()
se_vec <- numeric()

for (end_yr in 1964:2014) { 
        # set training on exogenous and target variables:
        pdo_train = window(merged_ts$pdo, start = start_yr, end_yr)
        upwell_train = window(merged_ts$upwell, start = start_yr, end = end_yr)
        exogenous_train = data.frame(pdo = pdo_train, upwell = upwell_train)
        land_train = window(land_ts, start = start_yr, end = end_yr)
        
        # set test year as 1 past the end_yr for training window
        test_yr = end_yr + 1
        # set test year's exogneous variables
        pdo_test = window(pdo_ts, start = test_yr)[1]
        upwell_test = window(upwell_ts,start = test_yr)[1]
        exogenous_test = data.frame(pdo = pdo_test, upwell = upwell_test)
        
        # train and predict with best model
        arima_ex2_aicc = auto.arima(land_train, xreg = exogenous_train, ic ='aicc', test = 'adf')
        arima_ex2_aicc.forecast = forecast.Arima(arima_ex2_aicc, xreg = exogenous_test, h=1)$mean[1]
        se_val = sqrt(arima_ex2_aicc$sigma2)

        # append test results to vectors

        year_vec = c(year_vec, test_yr)
        pred_vec = c(pred_vec, arima_ex2_aicc.forecast) 
        se_vec = c(se_vec, se_val)
        
        # add test target to results
        if (end_yr < 2014) {
                land_test = window(land_ts, start = test_yr)[1]
                real_vec = c(real_vec, land_test)
        } else {
                real_vec = c(real_vec, 0)
        }
}

# make result vectors into timeseries
real_ts = ts(real_vec, start = year_vec[1], end = 2014)
pred_ts = ts(pred_vec, start = year_vec[1], end = tail(year_vec, n = 1))
se_ts = ts(se_vec, start = year_vec[1], end = tail(year_vec, n = 1))
oos_err_ts = window(real_ts - pred_ts, end = 2014)


# plot standard errors of training model fit over time
ts.plot(se_ts, type = 'p', main = 'Model Standard Error over Time', ylab = 'S.E. (Mlbs.)')

## From little book of R Time Series:
plotForecastErrors <- function(forecasterrors)
{
        # make a histogram of the forecast errors:
        mybinsize <- IQR(forecasterrors)/4
        mysd   <- sd(forecasterrors)
        mymin  <- min(forecasterrors) - mysd*3
        mymax  <- max(forecasterrors) + mysd*3
        # generate normally distributed data with mean 0 and standard deviation mysd
        mynorm <- rnorm(10000, mean=0, sd=mysd)
        mymin2 <- min(mynorm)
        mymax2 <- max(mynorm)
        if (mymin2 < mymin) { mymin <- mymin2 }
        if (mymax2 > mymax) { mymax <- mymax2 }
        # make a red histogram of the forecast errors, with the normally distributed data overlaid:
        mybins <- seq(mymin, mymax, mybinsize)
        hist(forecasterrors, col="red", freq=FALSE, breaks=mybins)
        # freq=FALSE ensures the area under the histogram = 1
        # generate normally distributed data with mean 0 and standard deviation mysd
        myhist <- hist(mynorm, plot=FALSE, breaks=mybins)
        # plot the normal curve as a blue line on top of the histogram of forecast errors:
        points(myhist$mids, myhist$density, type="l", col="blue", lwd=2)
}

plotForecastErrors(oos_err_ts)

summary(arima_ex2_aicc)
ts.plot(arima_ex2_aicc$residuals, type = 'p', main = 'In-sample Residuals', xlab = 'Season', ylab = '(millions lbs)')
acf(arima_ex2_aicc$residuals, main = 'Auto Correlation of In-Sample Residuals')

ts.plot(oos_err_ts, type = 'p', main = 'Out of Sample Residuals', ylab = '(million lbs.)')
acf(oos_err_ts, main = 'Auto Correlation of ARIMA w/ex OOS Errors')
Box.test(oos_err_ts, type="Ljung-Box")

# Compute R^2
SSEin = sum(arima_ex2_aicc$residuals**2)
SST = sum((real_ts - mean(real_ts))**2)
R_2 = 1 - (SSEin/SST)
print('R Squared:')
R_2

print('Mean Absolute Error out of sample residuals:')
mean(abs(oos_err_ts))

# plot predictions vs. actual landings
ylab = 'Landings (million lbs.)'
xlab = 'Season'
main = 'Model Predictions vs. Actual'
model = 'ARIMA w/ex'
ts.plot(window(real_ts, end = 2014), type = 'l', col = 1, 
        main = main, xlab = xlab , ylab = ylab)
lines(pred_ts, type = 'l', col = 'red')
legend('topright', c('Actual', model), lty = c(1,1), col = c(1,'red'))

