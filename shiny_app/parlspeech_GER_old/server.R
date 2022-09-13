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
# speeches_full <- read_csv("C:/Users/bantel/Documents/GitHub-repos/parlspeech_GER/data/3-matching-out/2022-09-10-1503_bt_all_debates_emo_agenda_full.csv")

speeches_num <- 
  read_csv("./data/tst.csv") %>% select(-`...1`)

#  read_csv("./data/2022-09-10-1503_bt_all_debates_emo_agenda_numeric.csv") %>% select(-`...1`)

# Define server logic required to draw a histogram
shinyServer(function(input, output) {

    output$hist_plot <- renderPlot({
      ggplot(speeches_num # %>% filter(date > as.Date(input$date_range[1]) & date < as.Date(input$date_range[2]))
             ,
             aes(x=date, y=pos_emo)) +
        geom_bar(stat="identity")

    })

})

# next:
# - make barchart where pos_emo goes up, while neg_emo goes down
# - make linechart with smoothable mentions (two lines: pos & neg)
# - speaker differentiation


# aggregation level: date, speaker, party, format
