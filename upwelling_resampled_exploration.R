# explore upwelling resampled by lagging against the response variable
library(astsa)
library(stats)

# Load upwelling resampled by season
upwell <- read.csv('csv_data/upwell_resampled.csv', header = FALSE)
upwell_years <- upwell$V1
upwell_data <- upwell$V2
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
window_start = max(eureka_start, upwell_start)
window_end = min(eureka_end, upwell_end)
upwell <- window(upwell_ts, start = window_start, end = window_end)
eureka <- window(eureka_ts, start = window_start, end = window_end)

# this is a customized version of lag2.plot from {astsa} to control layout
lag2custom.plot <-
        function(series1,series2,max.lag=0,corr=TRUE,smooth=TRUE){ 
                name1=paste(deparse(substitute(series1)),"(t-",sep="")
                name2=paste(deparse(substitute(series2)),"(t)",sep="")
                series1=as.ts(series1)
                series2=as.ts(series2)
                max.lag=as.integer(max.lag)
                m1=max.lag+1
                prow= 2 #ceiling(sqrt(m1))
                pcol=3 #ceiling(m1/prow)
                a=stats::ccf(series1,series2,max.lag,plot=FALSE)$acf
                old.par <- par(no.readonly = TRUE)
                par(mfrow=c(prow,pcol), mar=c(2.5, 4, 2.5, 1), cex.main=1.1, font.main=1)
                for(h in 0:max.lag){                   
                        plot(lag(series1,-h), series2, xy.labels=FALSE, main=paste(name1,h,")",sep=""), ylab=name2, xlab="") 
                        if (smooth==TRUE) 
                                lines(stats::lowess(ts.intersect(lag(series1,-h),series2)[,1],
                                                    ts.intersect(lag(series1,-h),series2)[,2]), col="red")
                        if (corr==TRUE)
                                legend("topright", legend=round(a[m1-h], digits=2), text.col ="blue", bg="white", x.intersp=0)             
                        on.exit(par(old.par))
                }
        }

# Plot CCF of upwell and eureka
par(mfrow = c(1,1), mar = c(5,5,4,4))
ccf(c(upwell), c(eureka), main = "Cross Correlation: Upwell(lagged) vs. Eureka")

# show a 3x2 lagplot for 0-5 years of upwell lagged:
lag2custom.plot(upwell, eureka, max.lag = 5, smooth = TRUE)


