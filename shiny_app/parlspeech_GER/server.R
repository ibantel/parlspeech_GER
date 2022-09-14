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
         agg_emo = pos_emo + neg_emo) %>% 
  mutate(origin_pty = fct_relevel(origin_pty, c("cxu", "spd", "b90", "fdp", "lnk", "afd")))


hist_vars <- c("agg_emo"="Aggregate", "abs_neg_emo"="Negative", "pos_emo"="Positive")

scale_f_pties <- 
  scale_fill_manual(
    labels=c("CDU/CSU", "SPD", "Greens", "FDP", "Left", "AfD"),
    values=c("cxu"=col_cxu, "spd"=col_spd, "b90"=col_b90, "fdp"=col_fdp, "lnk"=col_lnk, "afd"=col_afd)
  )

# Define server logic required to draw a histogram
shinyServer(function(input, output, session) {
  
  # dynamically update "hist_bins"-scale
  observeEvent(input$freq_cutoffs,
               {updateSliderInput(session = session, inputId = "hist_bins", max = input$freq_cutoffs[2]-input$freq_cutoffs[1])}
  )
  
  # data_freq
  dataset_freq <- reactive({
    speeches_num %>% 
      # select columns
      select(c(date, origin_pty, abs_neg_emo, pos_emo, agg_emo)) %>% 
      # filter rows
      filter(origin_pty %in% input$gen_originpty) %>% 
      filter( (date > input$gen_daterange[1]) & (date < input$gen_daterange[2]))
  })

  # data_time
  dataset_time <- reactive({
    speeches_num %>% 
      # select columns
      select(c(date, origin_pty, pos_emo, neg_emo, agg_emo)) %>% 
      # filter rows
      filter(origin_pty %in% input$gen_originpty) %>% 
      filter( (date > input$gen_daterange[1]) & (date < input$gen_daterange[2])) %>% 
      # group by month
      mutate(date = as.yearmon(date) %>% as.Date()) %>% 
      group_by(date, origin_pty) %>% 
      summarize(pos_emo=mean(pos_emo), neg_emo=mean(neg_emo), agg_emo=mean(agg_emo)) %>% 
      ungroup() %>% 
      # other operations
      rename(positive=pos_emo, negative=neg_emo, aggregated=agg_emo) %>% 
      pivot_longer(cols=c("positive", "negative", "aggregated"), names_to="appeal_valence", values_to="appeal_number") %>% 
      mutate(appeal_valence=fct_relevel(appeal_valence, "positive", "negative"))
    })
  
  
  # freq_plot
  output$freq_plot <-
    renderPlot({
      dataset <- dataset_freq()
      
      # initialize freq_plot
      freq_p <- 
        ggplot(data=dataset, aes(x=.data[[input$freq_var]], fill=origin_pty))
      
      # pick freq_plot type depending on radio button selection
      if(input$freq_plottype=="hist"){
        freq_p <- freq_p + geom_histogram(bins = input$hist_bins + 2, size=0)
      }
      if(input$freq_plottype=="dens"){
        freq_p <- freq_p + geom_density(position = "stack", size=0)
      }
      
      # finish freq_plot
      freq_p +
        scale_f_pties + 
        
        ylab("Count") + 
        scale_x_continuous(name=paste0(hist_vars[input$freq_var], " emotive appeals per speech"),
                           limits=  c(input$freq_cutoffs[1]-1, input$freq_cutoffs[2]+1),
                           # display the lower bound as tick; then in steps of five
                           breaks=c(
                             input$freq_cutoffs[1],
                             seq(
                             # start: lower bound - next lower step of five
                             (((input$freq_cutoffs[1] + 4) %/% 5) * 5),
                             # end: upper bound
                             input$freq_cutoffs[2],
                             # steps
                             5))) +
        
        ggtitle(paste0(hist_vars[input$freq_var], " emotive appeals per speech\n(", 
                       input$gen_daterange[1] %>% as.yearmon(.), "\u2013",
                       input$gen_daterange[2] %>% as.yearmon(.), ")")) +
        labs(caption=paste0("n = ", nrow(dataset), " speeches")) + 
        theme_minimal() +
        theme(legend.position="bottom") + 
        guides(fill=guide_legend(title = "Speaker party", nrow=1,byrow=TRUE))
          
    })
  
  # over-time plot
  output$time_plot <-
    renderPlot({
      
      if(input$time_var=="agg"){
        dataset <- dataset_time() %>% filter(appeal_valence == "aggregated")
      }
      if(input$time_var=="neg_pos"){
        dataset <- dataset_time() %>% filter(appeal_valence %in% c("positive", "negative"))
      }
      if(input$time_var=="neg"){
        dataset <- dataset_time() %>% filter(appeal_valence == "negative")
      }
      if(input$time_var=="pos"){
        dataset <- dataset_time() %>% filter(appeal_valence == "positive")
      }
      
      
      
      ggplot(data=dataset, aes(x=date, y=appeal_number, color=appeal_valence, fill=origin_pty)) + 
        geom_bar(stat = "identity", size=0) +
        
        geom_hline(yintercept = 0, color="white", size=1) +
        
        scale_color_discrete(guide="none") + 
        scale_f_pties + 
        theme_minimal()
      
      
      
    })
})