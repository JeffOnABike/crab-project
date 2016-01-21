# pdo exploration in R
library(astsa)

# Load pdo resampled by season
pdo_resampled <- read.csv('csv_data/pdo_resampled.csv', header = FALSE)
pdo_years = pdo_resampled$V1
pdo_data = pdo_resampled$V2
pdo_start <- pdo_years[1]
pdo_end <- pdo_years[length(pdo_years)]
pdo_ts <- ts(pdo_data, start = pdo_start, end = pdo_end, frequency = 1)

# Load all port areas summarized by season
areas_seasonal <- read.csv('csv_data/areas_seasonal.csv', header = TRUE)
eureka_data <- areas_seasonal$Eureka
eureka_years <- areas_seasonal$Season
eureka_start <- eureka_years[1]
eureka_end <- eureka_years[length(eureka_years)]
eureka_ts <- ts(eureka_data, start = eureka_start, end = eureka_end, frequency = 1)

# align eureka and pdo timeseries to start and end on same season
window_start = max(pdo_start, eureka_start)
window_end = min(pdo_end, eureka_end)
pdo <- window(pdo_ts, start = window_start, end = window_end)
eureka <- window(eureka_ts, start = window_start, end = window_end)

# visualize cross correlation and lagplots
par(mfrow = c(1,1))
ccf(c(pdo), c(eureka), main = "Cross Correlation: PDO(lagged) vs. Eureka")
lag2.plot(c(pdo), c(eureka), max.lag = 5, smooth = TRUE)




