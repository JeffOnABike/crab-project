# EXPLORE WITH TIMES SERIES
library(TTR)
all_annual <- read.csv('R_data/all_annual.csv', header = FALSE)
annual_landings <- all_annual[2]
annual_ts <- ts(annual_landings, start = 1927)
eureka_monthly <- read.csv('R_data/eureka_monthly.csv', header = FALSE)
monthly_ts <- ts(eureka_monthly, start = c(1928-01), frequency = 12)

ts.plot(SMA(annual_ts, n=3))
ts.plot(SMA(annual_ts, n=8))

# 2 or less periods: no decomposing!
# doens't seem to work well for me even with monthly:
ts_components <- decompose(monthly_ts)

# take sample of monthly:
sample_monthly = window(x = monthly_ts, start = 1945, end = 1969)
sample_annually = window(x = annual_ts, start = 1945, end = 1969)
# To use HoltWinters() for simple exponential smoothing, we need to set the parameters beta=FALSE and gamma=FALSE in the HoltWinters() function 

HWforecaster <- HoltWinters(sample_annually, beta = FALSE, gamma = FALSE)
HWforecasts <- forecast.HoltWinters(HWforecaster, h=1)
plot(HWforecasts$residuals)
# check the ACF and ljung box test to see if there are non-zero correlations
acf(HWforecasts$residuals, lag.max=20)
Box.test(HWforecasts$residuals, lag=18, type="Ljung-Box")

plotForecastErrors <- function(forecasterrors)
{
        # make a histogram of the forecast errors:
        mybinsize <- IQR(forecasterrors)/4
        mysd   <- sd(forecasterrors)
        mymin  <- min(forecasterrors) - mysd*5
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

plotForecastErrors(HWforecasts$residuals)

# now accept a beta parameter:
HWexpforecaster <- HoltWinters(sample_annually, gamma = FALSE)
HWexpforecaster
HWexpforecasts <- forecast.HoltWinters(HWexpforecaster, h=1)
plot(HWexpforecasts$residuals)
# check the ACF and ljung box test to see if there are non-zero correlations
acf(HWexpforecasts$residuals, lag.max=20)
Box.test(HWforecasts$residuals, lag=18, type="Ljung-Box")
