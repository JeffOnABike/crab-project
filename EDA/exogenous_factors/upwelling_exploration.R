# explore upwelling:
library(TTR)
upwell <- read.csv('csv_data/upwell.csv', header = TRUE)
upwell

eureka_monthly <- read.csv('csv_data/eureka_monthly.csv', header = FALSE)
dates = eureka_monthly[1]
dates
eureka_start = c(1928,1)
eureka_end = c(2015,7)
upwell_start = c(1946,1)
upwell_end = c(2015,12)
window_start = upwell_start
window_end = eureka_end

eureka_monthly_ts <- ts(eureka_monthly[2], start = eureka_start, end = eureka_end, frequency = 12)
eureka_window <- window(eureka_monthly_ts, start = window_start, end = window_end)

upwell_42_ts <- ts(upwell[2], start = upwell_start, end=upwell_end, frequency = 12)
upwell_window <- window(upwell_42_ts, start = window_start, end = window_end)

ccf(c(upwell_window), c(eureka_window))
acf(upwell_window)
pacf(upwell_window)
acf(eureka_monthly_ts)
pacf(eureka_monthly_ts)

new_window_start = c(1946, 11)
components = decompose(upwell_window)

upwell_trend_ts = window(components$trend, 1947, 2014)
eureka_ccf_window = window(eureka_window, 1947, 2014)

ccf(c(upwell_trend_ts), c(eureka_ccf_window))
