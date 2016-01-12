library(shiny)

# Define UI for application that draws a histogram
shinyUI(fluidPage(
        
        # Application title
        titlePanel(h2("Northern California Dungeness Crab Landings", align = "center")),
        
        # Sidebar with a slider input for the number of bins
        sidebarLayout(
                sidebarPanel(
                        sliderInput("Season",
                                    "Choose A Season to Predict:",
                                    min = 1949,
                                    max = 2015,
                                    value = 1965),
                        'Put the Bar Graph Here of latest Prediction'
                ),
                
                # Show a plot of the generated distribution
                mainPanel('Put the time series plot here'
                        #plotOutput("distPlot")
                )
        )
))
