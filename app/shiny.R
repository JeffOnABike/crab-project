library(shiny)
library(ggplot2)
library(forecast)
library(hydroGOF)
library(TTR)
library(tseries)

shinyServer(function(input, output) {
        
        areas_seasonal <- read.csv('datasets/areas_seasonal.csv', header = TRUE)
        eureka_data <- areas_seasonal$Eureka
        eureka_years <- areas_seasonal$Season
        eureka_ts <- ts(eureka_data, start = eureka_years[1])
        
        
        pdo_lagged <- read.csv('datasets/pdo_resampled_lag4.csv', header = FALSE)
        pdo_data <- pdo_lagged$V2
        pdo_years <- pdo_lagged$V1
        pdo_ts <- ts(pdo_data, start = pdo_years[1])
        
        upwell_lagged <- read.csv('datasets/upwell_resampled_lag3.csv', header = FALSE)
        upwell_data <- upwell_lagged$V2
        upwell_years <- upwell_lagged$V1
        upwell_ts <- ts(upwell_data, start = upwell_years[1])
        
        merged_ts <- ts.intersect(landings = land_ts, pdo = pdo_ts, upwell = upwell_ts, dframe = TRUE)
        start_yr <- max(c(upwell_years[1], pdo_years[1], eureka_years[1]))
        
        year_vec <- numeric()
        real_vec <- numeric()
        
        m1_model_vec <- character()
        
        m1_pred_vec <- numeric()
        
        for (end_yr in 1964:2013) { 
                # set training on exogenous and target variables:
                pdo_train = window(merged_ts$pdo, start = start_yr, end_yr)
                upwell_train = window(merged_ts$upwell, start = start_yr, end = end_yr)
                exogenous_train = data.frame(pdo = pdo_train, upwell = upwell_train)
                eureka_train = window(eureka_ts, start = start_yr, end = end_yr)
                
                test_yr = end_yr + 1
                # set test:
                eureka_test = window(eureka_ts,start = test_yr)[1]
                ## COME BACK TO SET TEST EXOGENOUS
                pdo_test = window(pdo_ts,start = test_yr)[1]
                upwell_test = window(upwell_ts,start = test_yr)[1]
                exogenous_test = data.frame(pdo = pdo_test, upwell = upwell_test)
                
                # MOST COMPLEX MODELS:
                arima_ex2_aic = auto.arima(eureka_train, trace = FALSE, xreg = exogenous_train, ic ='aicc', test = 'adf')
                arima_ex2_aic.forecast = forecast.Arima(arima_ex2_aic, xreg = exogenous_test, h=1)$mean[1]
                
                year_vec = c(year_vec, test_yr)
                m1_pred_vec = c(m1_pred_vec, arima_ex2_aic.forecast) 
                real_vec = c(real_vec, eureka_test)
        }
        real_ts = ts(real_vec, start = year_vec[1], end=tail(year_vec, n = 1))
        pred_ts = ts(m1_pred_vec, start = year_vec[1], end=tail(year_vec, n = 1))
        # Expression that generates a histogram. The expression is
        # wrapped in a call to renderPlot to indicate that:
        #
        #  1) It is "reactive" and therefore should re-execute automatically
        #     when inputs change
        #  2) Its output type is a plot
        
        output$tsPlot <- renderPlot({
                #x    <- faithful[, 2]  # Old Faithful Geyser data
                #bins <- seq(min(x), max(x), length.out = input$bins + 1)
                main = "Eureka Landings"
                gpars = list(xlab = 'season', ylab = 'millions of pounds')
                ts.plot(real_ts, type = 'l', col = 1, gpars = gpars)
                
                lines(window(pred_ts, end =input$Season), type = 'l', col = 2)
                abline(v = input$Season)
                # draw the histogram with the specified number of bins
                #hist(rnorm(input$Season))

                #abline(v = input$Season)
                #hist(x, breaks = bins, col = 'darkgray', border = 'white')
        })
})