# explore upwelling:
library(astsa)

# Load upwell resampled by season
upwell_resampled <- read.csv('csv_data/upwell_resampled.csv', header = FALSE)
upwell_years = upwell_resampled$V1
upwell_data = upwell_resampled$V2
upwell_start <- upwell_years[1]
upwell_end <- upwell_years[length(upwell_years)]
upwell_ts <- ts(upwell_data, start = upwell_start, end = upwell_end, frequency = 1)

# Load all port areas summarized by season
areas_seasonal <- read.csv('csv_data/areas_seasonal.csv', header = TRUE)
eureka_data <- areas_seasonal$Eureka
eureka_years <- areas_seasonal$Season
eureka_start <- eureka_years[1]
eureka_end <- eureka_years[length(eureka_years)]
eureka_ts <- ts(eureka_data, start = eureka_start, end = eureka_end, frequency = 1)

# align eureka and upwell timeseries to start and end on same season
window_start = max(upwell_start, eureka_start)
window_end = min(upwell_end, eureka_end)
upwell <- window(upwell_ts, start = window_start, end = window_end)
eureka <- window(eureka_ts, start = window_start, end = window_end)

# visualize cross correlation and lagplots
par(mfrow = c(1,1))
ccf(c(upwell), c(eureka), main = "Cross Correlation: upwell(lagged) vs. Eureka")
lag2.plot(c(upwell), c(eureka), max.lag = 5, smooth = TRUE)


