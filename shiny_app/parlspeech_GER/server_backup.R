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
library(partycoloR)
library(zoo)

speeches_num <- 
  read_csv("C:/Users/bantel/Documents/GitHub-repos/parlspeech_GER/shiny_app/parlspeech_GER/data/2022-09-10-1503_bt_all_debates_emo_agenda_numeric.csv") %>% 
  select(-`...1`) %>% 
  mutate(abs_neg_emo = neg_emo,
         neg_emo = neg_emo * -1,
         agg_emo = pos_emo + neg_emo)

hist_vars <- c("agg_emo"="Aggregate", "abs_neg_emo"="Negative", "pos_emo"="Positive")

# Define server logic required to draw a histogram
shinyServer(function(input, output, session) {
  
  # dynamically update "hist_bins"-scale
  observeEvent(
    input$hist_cutoffs,
    {updateSliderInput(session = session, inputId = "hist_bins", max = input$hist_cutoffs[2]-input$hist_cutoffs[1])}
  )
  
  # data
  datasetInput <- reactive({
    speeches_num %>% 
      # filter
      filter(origin_pty %in% input$hist_originpty) %>% 
      filter( (date > input$hist_daterange[1]) & (date < input$hist_daterange[2]))
    })
  
  # generate a summary of the dataset
  output$summary <- renderPrint({
    dataset <- datasetInput()
    summary(dataset$neg_emo)
  })
  
  # plot
  output$freq_plot <-
    renderPlot({
      dataset <- datasetInput()
      
      ggplot(data=dataset, aes(x=.data[[input$hist_var]], fill=origin_pty)) +
        #geom_histogram(bins = input$hist_bins + 2, size=0) + 
        geom_density(position = "stack") + 
        
        scale_fill_manual(
          labels=c("CDU/CSU", "SPD", "Greens", "FDP", "Left", "AfD"),
          values=c("cxu"=col_cxu, "spd"=col_spd, "b90"=col_b90, "fdp"=col_fdp, "lnk"=col_lnk, "afd"=col_afd)) + 
        
        ylab("Count") + 
        scale_x_continuous(name=paste0(hist_vars[input$hist_var], " emotive appeals per speech"),
                           limits=c(input$hist_cutoffs[1]-1, input$hist_cutoffs[2]+1),
                           breaks=seq(input$hist_cutoffs[1], input$hist_cutoffs[2], 1)) +
        
        ggtitle(paste0(hist_vars[input$hist_var], " emotive appeals per speech\n(", 
                       input$hist_daterange[1] %>% as.yearmon(.), "\u2013",
                       input$hist_daterange[2] %>% as.yearmon(.), ")")) +
        labs(caption=paste0("n = ", nrow(dataset), " speeches")) + 
        ggthemes::theme_clean() +
        theme(legend.position="bottom") + 
        guides(fill=guide_legend(title = "Speaker party", nrow=1,byrow=TRUE))
          
    })
})