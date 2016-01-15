library(shiny)
library(ggplot2)
library(forecast)
library(hydroGOF)
#library(TTR)
#library(tseries)

shinyServer(function(input, output) {
        port_area <- 'Eureka'
        areas_seasonal <- read.csv('datasets/areas_seasonal.csv', header = TRUE)
        land_data <- areas_seasonal[[port_area]]
        land_years <- areas_seasonal$Season
        land_ts <- ts(land_data, start = eureka_years[1])
        
        pdo_lagged <- read.csv('datasets/pdo_resampled_lag4.csv', header = FALSE)
        pdo_data <- pdo_lagged$V2
        pdo_years <- pdo_lagged$V1
        pdo_ts <- ts(pdo_data, start = pdo_years[1])
        
        upwell_lagged <- read.csv('datasets/upwell_resampled_lag3.csv', header = FALSE)
        upwell_data <- upwell_lagged$V2
        upwell_years <- upwell_lagged$V1
        upwell_ts <- ts(upwell_data, start = upwell_years[1])
        
        merged_ts <- ts.intersect(landings = land_ts, pdo = pdo_ts, upwell = upwell_ts, dframe = TRUE)
        start_yr <- max(c(upwell_years[1], pdo_years[1], land_years[1]))
        
        year_vec <- numeric()
        real_vec <- numeric() 
        m1_pred_vec <- numeric()
        err_vec <- numeric()
        
        for (end_yr in 1964:2014) { 
                # set training on exogenous and target variables:
                pdo_train = window(merged_ts$pdo, start = start_yr, end_yr)
                upwell_train = window(merged_ts$upwell, start = start_yr, end = end_yr)
                exogenous_train = data.frame(pdo = pdo_train, upwell = upwell_train)
                land_train = window(land_ts, start = start_yr, end = end_yr)
                
                test_yr = end_yr + 1
                # set test:
                ## COME BACK TO SET TEST EXOGENOUS
                pdo_test = window(pdo_ts, start = test_yr)[1]
                upwell_test = window(upwell_ts,start = test_yr)[1]
                exogenous_test = data.frame(pdo = pdo_test, upwell = upwell_test)
                
                # MOST COMPLEX MODELS:
                arima_ex2_aic = auto.arima(land_train, trace = FALSE, xreg = exogenous_train, ic ='aicc', test = 'adf')
                arima_ex2_aic.forecast = forecast.Arima(arima_ex2_aic, xreg = exogenous_test, h=1)$mean[1]
                err_val = sqrt(arima_ex2_aicc$sigma2)
                
                year_vec = c(year_vec, test_yr)
                m1_pred_vec = c(m1_pred_vec, arima_ex2_aic.forecast) 
                err_vec = c(err_vec, err_val)

                if (end_yr < 2014) {
                        land_test = window(land_ts, start = test_yr)[1]
                        real_vec = c(real_vec, land_test)
                } else {
                        real_vec = c(real_vec, 0)
                }
        }
        real_ts = ts(real_vec, start = year_vec[1], end=tail(year_vec, n = 1))
        pred_ts = ts(m1_pred_vec, start = year_vec[1], end=tail(year_vec, n = 1))
        
        output$tsPlot <- renderPlot({

                main = input$PortArea
                gpars = list(xlab = 'season', ylab = 'millions of pounds')
                ts.plot(window(land_ts, start = 1949), main = main, type = 'l', col = 1, gpars = gpars)
                
                lines(window(pred_ts, end =input$Season), type = 'l', col = 2)
                abline(v = input$Season)              

        })
        output$barPlot <- renderPlot({
                index = match(input$Season, year_vec)
                plot <- barplot(height = c(m1_pred_vec[index], real_vec[index]), ylim = c(0,25), col = c('red','gray'))
                tops <- c(m1_pred_vec[index] + err_vec[index], 1.01 * (real_vec[index]))
                bots <- c(m1_pred_vec[index] - err_vec[index], real_vec[index])
                segments(plot,tops, plot, bots)
                arrows(plot, tops, plot, bots, lwd = 1.5, angle = 90,
                       code = 3, length = 0.05)
        })
})