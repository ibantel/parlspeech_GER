library(partycoloR)
library(shiny)
library(shinyjqui)
library(tidyverse)
library(zoo)

# Load data
{
  
  speeches_num <- 
    read_csv("./data/2022-09-10-1503_bt_all_debates_emo_agenda_numeric.csv") %>% 
    select(-`...1`) %>% 
    mutate(abs_neg_emo = (neg_emo / speech_terms * 100),
           agg_emo     = (pos_emo / speech_terms * 100) + (( -1 * neg_emo) / speech_terms * 100),
           neg_emo     = (neg_emo / speech_terms * 100) * -1,
           pos_emo     = (pos_emo / speech_terms * 100)) %>% 
    # select columns
    select(c(date, speaker, origin_pty, abs_neg_emo, pos_emo, neg_emo, agg_emo))
  
  
  # Define needed objects
  dict_vars <- c("agg_emo"="Aggregate", 
                 "abs_neg_emo"="Negative", 
                 "negpos_emo" = "Neg. & pos. appeals",
                 "neg_emo" = "Negative appeals",
                 "pos_emo"="Positive")
  
  scale_f_pties <- 
    scale_fill_manual(
      labels=c("CDU/CSU", "SPD", "Greens", "FDP", "Left", "AfD"),
      values=c("cxu"=partycolor(1375), 
               "spd"=partycolor( 383), 
               "b90"=partycolor(1816), 
               "fdp"=partycolor( 573), 
               "lnk"=partycolor(1545), 
               "afd"=partycolor(1976))
    )
  
  scale_c_pties <- 
    scale_color_manual(
      labels=c("CDU/CSU", "SPD", "Greens", "FDP", "Left", "AfD"),
      values=c("cxu"=partycolor(1375), 
               "spd"=partycolor( 383), 
               "b90"=partycolor(1816), 
               "fdp"=partycolor( 573), 
               "lnk"=partycolor(1545), 
               "afd"=partycolor(1976))
    )
  
  
  
}

# Define UI for application that draws a histogram
{
ui <- fluidPage(
  
  
  # Application title
  titlePanel("Emotive parliamentary speech in the German Bundestag"),
  #helpText("Plot occurrence of emotive parliamentary speech over time"),
  helpText(HTML("For background, see <a href='https://github.com/ibantel/parlspeech_GER' target='_blank'>https://github.com/ibantel/parlspeech_GER</a>.")),
  br(),
  
  # Sidebar
  sidebarLayout(
    # Sidebar panel
    {
      sidebarPanel(
        width = 3,
        
        # GEN - date range----
        sliderInput(inputId="gen_daterange", label=h4("Date range:"),
                    min = as.Date("2009-10-27"), # speeches_num$date %>% min(), 
                    max = as.Date("2018-12-14"), # speeches_num$date %>% max(),
                    value = c(as.Date("2010-01-01", "%Y-%m-%d"), as.Date("2017-01-01", "%Y-%m-%d")),
                    timeFormat="%m/%Y"),
        br(),
        
        # GEN - plot type----
        radioButtons(inputId="gen_plottype", label=h4("Plot type:"),
                     choices=c("Simple frequency (histogram)"="freq_simp_hist",
                               "Simple frequency (density)"="freq_simp_dens",
                               "Over-time frequency"="freq_time",
                               "Speaker-level plot"="spkr_simp"),
                     selected="freq_simp_hist"),
        
        # versions - variable of interest----
        
        # freq_simp_* - variable of interest
        conditionalPanel(condition="input.gen_plottype == 'freq_simp_hist' || input.gen_plottype == 'freq_simp_dens'",
                         radioButtons(inputId="freq_simp_var", label=h4("Measure:"),
                                      choices = c("Aggregate appeals (positive minus negative)" = "agg_emo",
                                                  "Negative appeals" = "abs_neg_emo",
                                                  "Positive appeals" = "pos_emo"),
                                      selected="agg_emo")
        ),
        
        # freq_time - variable of interest
        conditionalPanel(condition="input.gen_plottype == 'freq_time'",
                         radioButtons(inputId="freq_time_var", label=h4("Measure:"),
                                      choices=c("Aggregate appeals (positive minus negative)" = "agg_emo",
                                                "Neg. & pos. appeals" = "negpos_emo",
                                                "Negative appeals" ="neg_emo",
                                                "Positive appeals" = "pos_emo"),
                                      selected="agg_emo")
        ),
        #helpText("* pos. - neg. appeals"),
        
        # spkr_simp - variable of interest
        conditionalPanel(condition = "input.gen_plottype == 'spkr_simp'",
                         radioButtons(inputId="spkr_simp_var", label=h4("Measure:"),
                                      choices = c("Aggregate appeals (positive minus negative)" = "agg_emo",
                                                  "Negative appeals" = "abs_neg_emo",
                                                  "Positive appeals" = "pos_emo"),
                                      selected="agg_emo")),
        
        # GEN - origin party----
        h4("Speaker parties"),
        orderInput(inputId = "gen_originpty_display", label=HTML("<h5>Display (order-sensitive):</h5>"), 
                   placeholder="Drag items here...",
                   width="100%",
                   connect="gen_originpty_discard",
                   items = c("CDU/CSU" = "cxu",
                             "SPD" = "spd", 
                             "B90/Gruene" = "b90", 
                             "FDP" = "fdp", 
                             "Die Linke" = "lnk", 
                             "AfD" = "afd")
        ),
        orderInput(inputId = "gen_originpty_discard", label=HTML("<h5>Ignore:</h5>"), 
                   placeholder="Drag items here...",
                   width="100%", 
                   connect="gen_originpty_display",
                   items = NULL),
        
        # FREQ - bounds----
        conditionalPanel(condition="input.gen_plottype == 'freq_simp_hist' || input.gen_plottype == 'freq_simp_dens'",
                         sliderInput(inputId="freq_cutoffs", label = HTML("<h4>Bounds</h4><h5>(appeals per 100 words)</h5>"),
                                     min =     1,
                                     max =    25,
                                     value = c(1, 10))
        ),
        
        # FREQ::HIST - histogram breaks (conditional panel)----
        conditionalPanel(condition="input.gen_plottype == 'freq_simp_hist'",
                         sliderInput(inputId="hist_bins", label = h4("No. of bins:"),
                                     min =   3,
                                     max =  25,
                                     value =15,
                                     ticks=FALSE)
        ),
        # SPKR - top_x speakers----
        conditionalPanel(condition="input.gen_plottype == 'spkr_simp'",
                         sliderInput(inputId="topx_spkr", label = h4("No. of speakers to display:"),
                                     min   =  2,
                                     max   = 25,
                                     value = 10
                                     )),
        
        # SPKR - speaker by name----
        conditionalPanel(condition="input.gen_plottype == 'spkr_simp'",
                         textInput(inputId="text_spkr", label = h4("Search additional speaker to display:"),
                                   value = "",
                                   placeholder = "Type here to add"
                         )),
        conditionalPanel(condition="input.gen_plottype == 'spkr_simp'",
                         sliderInput(inputId="textspkr_no", label=h4("Number of found speakers to display"),
                                     min=0, max=5,
                                     value=2))
        
        
      )
      },
    
    # Main panel
    {
      # Show a plot of the generated distribution
      mainPanel(
        conditionalPanel(condition="input.gen_plottype == 'freq_simp_hist' || input.gen_plottype == 'freq_simp_dens'",
                         jqui_resizable(plotOutput("freq_plot"))
        ),
        
        conditionalPanel(condition="input.gen_plottype == 'freq_time'",
                         jqui_resizable(plotOutput("time_plot"))
        ),
        
        conditionalPanel(condition="input.gen_plottype == 'spkr_simp'",
                         jqui_resizable(plotOutput("spkr_plot"))
        )
        
        
      )
      }  
  )
)
}

# Define server logic required to draw a histogram
{
server <- function(input, output, session) {
  
  # dynamically update "hist_bins"-scale
  observeEvent(
    input$freq_cutoffs,
    {updateSliderInput(session = session, inputId = "hist_bins", 
                       max = input$freq_cutoffs[2]-input$freq_cutoffs[1] - 1,
                       step = 1
                       )}
  )
  
  observeEvent(
    input$text_spkr,
    {
      if(input$text_spkr == ""){updateSliderInput(session = session, inputId = "textspkr_no", value = 0)}
      if(input$text_spkr != ""){updateSliderInput(session = session, inputId = "textspkr_no", value = 2)}
    }
  )
  
  # construct data_freq dataset
  dataset_freq <- reactive({
    speeches_num %>% 
      # filter rows
      filter(origin_pty %in% input$gen_originpty_display) %>% 
      filter( (date > input$gen_daterange[1]) & (date < input$gen_daterange[2])) %>% 
      # re-order factors
      mutate(origin_pty = fct_relevel(origin_pty, input$gen_originpty_display))})
  
  # construct data_time dataset
  dataset_time <- reactive({
    speeches_num %>% 
      # filter rows
      filter(origin_pty %in% input$gen_originpty_display) %>% 
      filter( (date > input$gen_daterange[1]) & (date < input$gen_daterange[2])) %>% 
      # re-order factors
      mutate(origin_pty = fct_relevel(origin_pty, input$gen_originpty_display)) %>% 
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
  
  # construct data_speaker dataset
  dataset_speaker <- reactive({
    speeches_num %>% 
      # filter rows on date
      filter( (date > input$gen_daterange[1]) & (date < input$gen_daterange[2])) %>% 
      # re-order factors
      mutate(origin_pty = fct_relevel(origin_pty, input$gen_originpty_display)) %>% 
      group_by(speaker, origin_pty) %>% 
      summarize(pos_emo=mean(pos_emo), abs_neg_emo=mean(abs_neg_emo), agg_emo=mean(agg_emo), .groups = 'keep') %>% 
      ungroup() %>% 
      # other operations
      pivot_longer(cols=c("pos_emo", "abs_neg_emo", "agg_emo"), names_to="appeal_valence", values_to="appeal_number") %>% 
      filter(appeal_valence == input$spkr_simp_var)
  })
  
  # plots
  {
    # freq_plot
    output$freq_plot <-
      renderPlot({
        dataset <- dataset_freq()
        
        # initialize freq_plot
        freq_p <- 
          ggplot(data=dataset, aes(x=.data[[input$freq_simp_var]], fill=origin_pty))
        
        # pick freq_plot type depending on radio button selection
        if(input$gen_plottype=="freq_simp_hist"){
          freq_p <- freq_p + geom_histogram(bins = input$hist_bins + 2, size=0)
        }
        if(input$gen_plottype=="freq_simp_dens"){
          freq_p <- freq_p + geom_density(position = "stack", size=0)
        }
        
        # finish freq_plot
        freq_p +
          
          # additional manipulations (axes etc.)
          scale_f_pties + 
          scale_x_continuous(name=paste0(dict_vars[input$freq_simp_var], " emotive appeals per 100 words"),
                             limits=  c(input$freq_cutoffs[1], input$freq_cutoffs[2]+1),
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
          labs(y="Count", caption=paste0("n = ", nrow(dataset), " speeches\n")) + 
          ggtitle(paste0(dict_vars[input$freq_simp_var], " emotive appeals per 100 words\n(", input$gen_daterange[1] %>% as.yearmon(.), "\u2013", input$gen_daterange[2] %>% as.yearmon(.), ")")) +
          theme_minimal() +
          theme(legend.position="bottom") + 
          guides(fill=guide_legend(title = "Speaker party", nrow=1, byrow=TRUE))
        
      })
    
    # over-time plot
    output$time_plot <-
      renderPlot({
        
        # variable selection
        {
        if(input$freq_time_var=="agg_emo"){
          dataset <- dataset_time() %>% filter(appeal_valence == "aggregated")
        }
        if(input$freq_time_var=="negpos_emo"){
          dataset <- dataset_time() %>% filter(appeal_valence %in% c("positive", "negative"))
        }
        if(input$freq_time_var=="neg_emo"){
          dataset <- dataset_time() %>% filter(appeal_valence == "negative")
        }
        if(input$freq_time_var=="pos_emo"){
          dataset <- dataset_time() %>% filter(appeal_valence == "positive")
        }
        }
        
        ggplot(data=dataset, aes(x=date, y=appeal_number, color=appeal_valence, fill=origin_pty)) + 
          geom_bar(stat = "identity", size=0) +
          geom_hline(yintercept = 0, color="white", size=1) +
          
          scale_f_pties +
          scale_color_discrete(guide="none") + 
          labs(x="Date", y="Appeals per 100 words") + 
          ggtitle(paste0(dict_vars[input$freq_time_var], " emotive appeals per 100 words\n(", input$gen_daterange[1] %>% as.yearmon(.), "\u2013", input$gen_daterange[2] %>% as.yearmon(.), ")")) +
          theme_minimal() +
          theme(legend.position="bottom") +
          guides(fill=guide_legend(title = "Speaker party", nrow=1, byrow=TRUE))
        
      })
    
    # speaker level lollipop plot
    output$spkr_plot <-
      renderPlot({
        
        dataset <- 
          bind_rows(
            # top_x speakers
            dataset_speaker() %>% 
              filter(origin_pty %in% input$gen_originpty_display) %>% 
              arrange(appeal_number %>% desc()) %>% # arrange by values
              head(input$topx_spkr) # get top X
            ,
            
            # specified speaker
            dataset_speaker() %>%
              filter(str_detect(speaker, input$text_spkr)) %>% 
              arrange(speaker %>% desc()) %>% 
              head(input$textspkr_no)
          ) %>% 
          
          arrange(appeal_number %>% desc()) %>% # arrange by values
          mutate(speaker = as_factor(speaker) %>% fct_relevel(., 
                                                              # names of manually selected speakers
                                                              c(
                                                                dataset_speaker() %>% 
                                                                  filter(str_detect(speaker, input$text_spkr)) %>% 
                                                                  arrange(appeal_number) %>% 
                                                                  head(input$textspkr_no) %>% 
                                                                  select(speaker)
                                                                ), 
                                                              after = Inf # move to the end
                                                              )) # save order in factor levels
        

        ggplot(data=dataset, aes(y=speaker, x=appeal_number, color=origin_pty)) +
          
          geom_segment(aes(yend=speaker, xend=0)) +
          geom_point(size=5) +
          scale_c_pties +
          scale_y_discrete(limits = rev) +
          theme_bw() +
          ggtitle(paste0(dict_vars[input$spkr_simp_var], " emotive appeals\n(", input$gen_daterange[1] %>% as.yearmon(.), "\u2013", input$gen_daterange[2] %>% as.yearmon(.), ")")) +
          
          labs(y="", x = paste0(dict_vars[input$spkr_simp_var], " emotive appeals per 100 words ")) +
          theme(
            axis.text.y = element_text(size=14),
            legend.position="bottom") +
          guides(color=guide_legend(title = "Speaker party", nrow=1, byrow=TRUE))
      })
  
  
    
    }
  }
}

# Run the application 
shinyApp(ui = ui, server = server)

# 
# speakers
# gov't / opposition dynamics
# formats
# proposals by party X
