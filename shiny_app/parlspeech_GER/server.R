#
# This is the server logic of a Shiny web application. You can run the
# application by clicking 'Run App' above.
#
# Find out more about building applications with Shiny here:
#
#    http://shiny.rstudio.com/
#

library(shiny)
library(tidyverse)

speeches_num <- 
  read_csv("C:/Users/bantel/Documents/GitHub-repos/parlspeech_GER/shiny_app/parlspeech_GER/data/2022-09-10-1503_bt_all_debates_emo_agenda_numeric.csv") %>% select(-`...1`)

# Define server logic required to draw a histogram
shinyServer(function(input, output) {
  # data
  datasetInput <- reactive({
    speeches_num %>% 
      # filter
      filter(origin_pty %in% input$origin_pty)
      #filter(date > as.Date(input$date_range[1]) & date < as.Date(input$date_range[2]))
    })
  
  # generate a summary of the dataset
  output$summary <- renderPrint({
    dataset <- datasetInput()
    summary(dataset$neg_emo)
  })
  
  # plot
  output$bar_plot <-
    renderPlot({
      dataset <- datasetInput()
      
      ggplot(data=dataset, aes(x=neg_emo)) +
        geom_histogram(bins = input$n_breaks_hist) + 
        ggtitle(paste0("Histogram of ", "neg_emo ", "between ", 
                       as.Date(input$date_range[1]) %>% format(., "%d %B %Y"), " and ",
                       as.Date(input$date_range[2]) %>% format(., "%d %B %Y"))) +
        theme_bw()
    })
})