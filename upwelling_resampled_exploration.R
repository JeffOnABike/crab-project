# explore upwelling:
library(TTR)
library(astsa)
library(forecast)
upwell <- read.csv('csv_data/upwell_resampled.csv', header = FALSE)
upwell_years <- upwell$V1
upwell_data <- upwell$V2
upwell_start <- upwell_years[1]
upwell_end <- upwell_years[length(upwell_years)]
upwell_ts <- ts(upwell_data, start = upwell_start, end = upwell_end, frequency = 1)

#eureka_monthly <- read.csv('csv_data/eureka_monthly.csv', header = FALSE)
areas_seasonal <- read.csv('csv_data/areas_seasonal.csv', header = TRUE)
eureka_data <- areas_seasonal$Eureka
eureka_years <- areas_seasonal$Season
eureka_start <- eureka_years[1]
eureka_end <- eureka_years[length(eureka_years)]
eureka_ts <- ts(eureka_data, start = eureka_start, end = eureka_end, frequency = 1)

window_start = max(eureka_start, upwell_start)
window_end = min(eureka_end, upwell_end)

upwell_window <- window(upwell_ts, start = window_start, end = window_end)
eureka_window <- window(eureka_ts, start = window_start, end = window_end)
ccf(c(upwell_window), c(eureka_window))


acf(upwell_window)
pacf(upwell_window)

acf(eureka_ts)
pacf(eureka_ts)

##new_window_start = c(1946, 11)
#components = decompose(upwell_window)

#upwell_trend_ts = window(components$trend, 1947, 2014)
#eureka_ccf_window = window(eureka_window, 1947, 2014)
## SAVE THIS!!!
lag2.plot(c(upwell_window), c(eureka_window), max.lag = 5, smooth = TRUE)

#arima(eureka_window, order= c(1,0,1))
