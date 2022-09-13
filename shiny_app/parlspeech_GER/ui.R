#
# This is the user-interface definition of a Shiny web application. 
# 
#
# 
#
# 
#

library(shiny)

# Define UI for application that draws a histogram
shinyUI(fluidPage(
  
  # Application title
  titlePanel("Emotive parliamentary speech in the German Bundestag"),
  
  # Sidebar with a slider input for number of bins
  sidebarLayout(
    sidebarPanel(
      helpText("Plot occurrence of emotive parliamentary speech over time"),
      br(),
      sliderInput("date_range",
                  label = h4("Date range:"),
                  min = as.Date("2005-01-01", "%Y-%m-%d"), #speeches_num$date %>% min(),
                  max = as.Date("2023-01-01", "%Y-%m-%d"), #speeches_num$date %>% max()
                  value = c(as.Date("2010-01-01", "%Y-%m-%d"),
                            as.Date("2020-01-01", "%Y-%m-%d")),
                  timeFormat="%m/%Y"),
      br(),
      sliderInput("n_breaks_hist",
                  label = h4("Number of breaks:"),
                  min = 1,
                  max = 100,
                  value = 50),
      checkboxGroupInput(inputId = "origin_pty",
                         label = "Speaker party:",
                         choices = c("CDU/CSU" = "cxu",
                                     "SPD" = "spd", 
                                     "FDP" = "fdp", 
                                     "Die Linke" = "lnk", 
                                     "B.90/Gruene" = "b90", 
                                     "AfD" = "afd"),
                         selected = "cxu")
      
    ),
    
    # Show a plot of the generated distribution
    mainPanel(
      plotOutput("bar_plot")
    )
  )
))