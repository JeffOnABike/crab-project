library(shiny)
# Define UI for application that draws a histogram
shinyUI(fluidPage(
        
        # Application title
        titlePanel(h2("Northern California Dungeness Crab Landings", align = "center")),
        
        # Sidebar with a slider input for the number of bins
        sidebarLayout(
                sidebarPanel(
                        selectInput(inputId = 'PortArea', label = 'pick', choices = c('Eureka')),
                        sliderInput(inputId = "Season",
                                    label = "Browse Predictions by Season:",
                                    min = 1965,
                                    max = 2015,
                                    value = 1965,
                                    animate = TRUE,
                                    format = "####"),
                        plotOutput(outputId = "barPlot") 
                        
                ),
                
                # Show a plot of the generated distribution
                mainPanel(
                        plotOutput(outputId = "tsPlot")
                )
        )
))
