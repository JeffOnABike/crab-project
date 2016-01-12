# pdo exploration in R
library(astsa)
#library(stats)

pdo_resampled <- read.csv('../csv_data/pdo_resampled.csv', header = FALSE)
pdo_resampled_start = c(1900)
pdo_resampled_end = c(2016)
pdo_resampled_data <- pdo_resampled[2]
pdo_resampled_ts <- ts(pdo_resampled_data, start = pdo_resampled_start, end = pdo_resampled_end)
pdo_resampled_ts


areas_seasonal <- read.csv('../csv_data/areas_seasonal.csv', header = TRUE)
areas_seasonal_start = c(1927)
areas_seasonal_end = c(2014)
areas_seasonal_years <- areas_seasonal[1]
eureka_seasonal <- areas_seasonal[2]
eureka_seasonal_ts <- ts(eureka_seasonal, start = areas_seasonal_start, end = areas_seasonal_end)

window_start = max(pdo_resampled_start, areas_seasonal_start)
window_end = min(pdo_resampled_end, areas_seasonal_end)


eureka = window(eureka_seasonal_ts, start = window_start, end = window_end)
pdo = window(pdo_resampled_ts, start = window_start, end = window_end)

# want to save this!
ccf(c(pdo), c(eureka))
lag2.plot(c(pdo), c(eureka), max.lag = 5, smooth = TRUE)
