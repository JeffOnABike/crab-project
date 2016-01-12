library(fpp)
plot(a10, ylab="$ million", xlab="Year", main="Antidiabetic drug sales")
plot(log(a10), ylab="", xlab="Year", main="Log Antidiabetic drug sales")


k <- 60 # minimum data length for fitting a model
# total length is 204 datapoints (assume monthly for about 18 yrs)
n <- length(a10)
mae1 <- mae2 <- mae3 <- matrix(NA,n-k,12)
# tsp gets time series component out (e.g. 1991.5)
# (k-2)/12 is 4.8333 which is just under years of mininmum data len
# st is set to 1996.333
st <- tsp(a10)[1]+(k-2)/12

# this iterates for 1:144
for(i in 1:(n-k))
{
        #x short and xnext divide up the data
        xshort <- window(a10, end=st + i/12)
        xnext <- window(a10, start=st + (i+1)/12, end=st + (i+12)/12)
        fit1 <- tslm(xshort ~ trend + season, lambda=0)
        fcast1 <- forecast(fit1, h=12)
        #arima1 <- auto.arima(xshort, trace = FALSE, test = 'kpss', ic = 'aic')
        fit2 <- Arima(xshort, order=c(3,0,1), seasonal=list(order=c(0,1,1), period=12), 
                      include.drift=TRUE, lambda=0, method="ML")
        fcast2 <- forecast(fit2, h=12)
        fit3 <- ets(xshort,model="MMM",damped=TRUE)
        fcast3 <- forecast(fit3, h=12)
        mae1[i,1:length(xnext)] <- abs(fcast1[['mean']]-xnext)
        mae2[i,1:length(xnext)] <- abs(fcast2[['mean']]-xnext)
        mae3[i,1:length(xnext)] <- abs(fcast3[['mean']]-xnext)
}

plot(1:12, colMeans(mae1,na.rm=TRUE), type="l", col=2, xlab="horizon", ylab="MAE",
     ylim=c(0.65,1.05))
lines(1:12, colMeans(mae2,na.rm=TRUE), type="l",col=3)
lines(1:12, colMeans(mae3,na.rm=TRUE), type="l",col=4)
legend("topleft",legend=c("LM","ARIMA","ETS"),col=2:4,lty=1)