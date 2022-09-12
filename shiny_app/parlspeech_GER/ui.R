#
# This is the user-interface definition of a Shiny web application. You can
# run the application by clicking 'Run App' above.
#
# Find out more about building applications with Shiny here:
#
#    http://shiny.rstudio.com/
#

library(shiny)

# Define UI for application that draws a histogram
shinyUI(fluidPage(

    # Application title
    titlePanel("Emotive parliamentary speech in the German", em("Bundestag")),

    # Sidebar with a slider input for number of bins
    sidebarLayout(
        sidebarPanel(
          sliderInput("date_range",
                      label = h3("Date range:"),
                      min = as.Date("2005-01-01", "%Y-%m-%d"), #speeches_num$date %>% min(),
                      max = as.Date("2023-01-01", "%Y-%m-%d"), #speeches_num$date %>% max()
                      value = c(as.Date("2010-01-01", "%Y-%m-%d"),
                                as.Date("2020-01-01", "%Y-%m-%d")),
                      timeFormat="%m/%Y"),
          helpText("Plot occurrence of emotive parliamentary speech over time")
        ),
        # Show a plot of the generated distribution
        mainPanel(
            plotOutput("hist_plot")
        )
    )
))

if(FALSE){
ui <- fluidPage(
  sidebarLayout(
    sidebarPanel(
      helpText("Create demographic maps with 
        information from the 2010 US Census."),
      
      selectInput("var", 
                  label = "Choose a variable to display",
                  choices = c("Percent White", "Percent Black",
                              "Percent Hispanic", "Percent Asian"),
                  selected = "Percent White"),
      
      sliderInput("range", 
                  label = "Range of interest:",
                  min = 0, max = 100, value = c(0, 100))
    ),
    
    mainPanel(plotOutput("map"))
  )
)
}