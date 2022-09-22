library(here)
library(partycoloR)
library(shiny)
library(shinyjqui)
library(tidyverse)
library(zoo)


# Load data
{
  
  # load general data
  speeches_num <- 
    read_csv("./data/2022-09-10-1503_bt_all_debates_emo_agenda_numeric.csv") %>% 
    # preparation emotions
    mutate(abs_neg_emo = (neg_emo / speech_terms * 100),
           agg_emo     = (pos_emo / speech_terms * 100) + (( -1 * neg_emo) / speech_terms * 100),
           neg_emo     = (neg_emo / speech_terms * 100) * -1,
           pos_emo     = (pos_emo / speech_terms * 100)) %>% 
    # preparation plot type of debate
    mutate(across(c(starts_with("meta_"), starts_with("fctn_"), "govt"), ~ case_when(. > 0 ~ 1, TRUE ~ 0)),
           meta_other___ = case_when(
             ((meta_beratung == 0) & (meta_beschlem == 0) & (meta_bericht_ == 0) & (meta_fragstun == 0) & (meta_befragun == 0) &
                (meta_aktustnd == 0) & (meta_regerklr == 0) & (meta_antwort_ == 0) & (meta_wahl____ == 0) & (meta_eidleist == 0)) ~ 1,
             TRUE ~ 0),
           fctn_oth = case_when(
             ((fctn_afd==0) & (fctn_b90==0) & (fctn_cxu==0) & (fctn_fdp==0) & (fctn_lnk==0) & (fctn_spd==0) & (govt == 0)) ~ 1,
             TRUE ~ 0)
           ) %>% 
    # select columns
    select(-c(`...1`, speechnumber, speech_terms))
  
  # combine data for "type of agenda point"-visualization
  speeches_meta <- 
    bind_rows(speeches_num %>% filter(meta_beratung == 1) %>% select(-starts_with("meta_")) %>% mutate(meta='Consultation'),
              speeches_num %>% filter(meta_beschlem == 1) %>% select(-starts_with("meta_")) %>% mutate(meta='Resolution'),
              speeches_num %>% filter(meta_bericht_ == 1) %>% select(-starts_with("meta_")) %>% mutate(meta='Report'),
              speeches_num %>% filter(meta_fragstun == 1) %>% select(-starts_with("meta_")) %>% mutate(meta="Questioning gov't"),
              speeches_num %>% filter(meta_befragun == 1) %>% select(-starts_with("meta_")) %>% mutate(meta="Questioning gov't"),
              speeches_num %>% filter(meta_aktustnd == 1) %>% select(-starts_with("meta_")) %>% mutate(meta='Current affairs debate'),
              speeches_num %>% filter(meta_regerklr == 1) %>% select(-starts_with("meta_")) %>% mutate(meta="Gov't statement"),
              speeches_num %>% filter(meta_antwort_ == 1) %>% select(-starts_with("meta_")) %>% mutate(meta='Response'),
              speeches_num %>% filter(meta_wahl____ == 1) %>% select(-starts_with("meta_")) %>% mutate(meta='Election'),
              speeches_num %>% filter(meta_eidleist == 1) %>% select(-starts_with("meta_")) %>% mutate(meta='Swearing in'),
              speeches_num %>% filter(meta_other___ == 1) %>% select(-starts_with("meta_")) %>% mutate(meta='Other'))
  
  speeches_meta_sponsor <-
    bind_rows(speeches_meta %>% filter(fctn_afd == 1) %>% select(-c(starts_with("fctn_"), govt)) %>% mutate(sponsor="afd"),
              speeches_meta %>% filter(fctn_b90 == 1) %>% select(-c(starts_with("fctn_"), govt)) %>% mutate(sponsor="b90"),
              speeches_meta %>% filter(fctn_cxu == 1) %>% select(-c(starts_with("fctn_"), govt)) %>% mutate(sponsor="cxu"),
              speeches_meta %>% filter(fctn_fdp == 1) %>% select(-c(starts_with("fctn_"), govt)) %>% mutate(sponsor="fdp"),
              speeches_meta %>% filter(fctn_lnk == 1) %>% select(-c(starts_with("fctn_"), govt)) %>% mutate(sponsor="lnk"),
              speeches_meta %>% filter(fctn_spd == 1) %>% select(-c(starts_with("fctn_"), govt)) %>% mutate(sponsor="spd"),
              speeches_meta %>% filter(fctn_oth == 1) %>% select(-c(starts_with("fctn_"), govt)) %>% mutate(sponsor="oth"),
              speeches_meta %>% filter(govt     == 1) %>% select(-c(starts_with("fctn_"), govt)) %>% mutate(sponsor="gov")) %>% 
    select(-speaker) %>% 
    arrange(date) %>% 
    group_by(date, origin_pty, meta, sponsor) %>% 
    summarize(.groups="keep", 
              neg_emo=mean(neg_emo, na.rm=T),
              pos_emo=mean(pos_emo, na.rm=T),
              abs_neg_emo=mean(abs_neg_emo, na.rm=T),
              agg_emo=mean(agg_emo, na.rm=T)
    ) %>% 
    ungroup()
  
  
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

# Define UI for application
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
        sliderInput(inputId="gen_daterange", label=h4("Date range"),
                    min = as.Date("2009-10-27"), # speeches_num$date %>% min(), 
                    max = as.Date("2018-12-14"), # speeches_num$date %>% max(),
                    value = c(as.Date("2010-01-01", "%Y-%m-%d"), as.Date("2017-01-01", "%Y-%m-%d")),
                    timeFormat="%m/%Y"),
        br(),
        
        # GEN - plot type----
        radioButtons(inputId="gen_plottype", label=h4("Plot type"),
                     choices=c("Simple frequency (histogram)"="freq_simp_hist",
                               "Simple frequency (density)"="freq_simp_dens",
                               "Over-time frequency"="freq_time",
                               "Speaker-level plot"="spkr_simp",
                               "Agenda item differentiation"="meta"),
                     selected="freq_simp_hist"),
        
        # versions - variable of interest----
        
        # freq_simp_* - variable of interest
        conditionalPanel(condition="input.gen_plottype == 'freq_simp_hist' || input.gen_plottype == 'freq_simp_dens' ||  input.gen_plottype == 'meta'",
                         radioButtons(inputId="simp_var", label=h4("Measure"),
                                      choices = c("Aggregate appeals (positive minus negative)" = "agg_emo",
                                                  "Negative appeals" = "abs_neg_emo",
                                                  "Positive appeals" = "pos_emo"),
                                      selected="agg_emo")
        ),
        
        # freq_time - variable of interest
        conditionalPanel(condition="input.gen_plottype == 'freq_time'",
                         radioButtons(inputId="freq_time_var", label=h4("Measure"),
                                      choices=c("Aggregate appeals (positive minus negative)" = "agg_emo",
                                                "Neg. & pos. appeals" = "negpos_emo",
                                                "Negative appeals" ="neg_emo",
                                                "Positive appeals" = "pos_emo"),
                                      selected="agg_emo")
        ),
        #helpText("* pos. - neg. appeals"),
        
        # spkr_simp - variable of interest
        conditionalPanel(condition = "input.gen_plottype == 'spkr_simp'",
                         radioButtons(inputId="spkr_simp_var", label=h4("Measure"),
                                      choices = c("Aggregate appeals (positive minus negative)" = "agg_emo",
                                                  "Negative appeals" = "abs_neg_emo",
                                                  "Positive appeals" = "pos_emo"),
                                      selected="agg_emo")),
        
        # GEN - origin party----
        h4("Speaker parties"),
        orderInput(inputId = "gen_originpty_display", label=HTML("<h5>Display (order-sensitive)</h5>"), 
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
        orderInput(inputId = "gen_originpty_discard", label=HTML("<h5>Ignore</h5>"), 
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
                         sliderInput(inputId="hist_bins", label = h4("No. of bins"),
                                     min =   3,
                                     max =  25,
                                     value =15,
                                     ticks=FALSE)
        ),
        # SPKR - top_x speakers----
        conditionalPanel(condition="input.gen_plottype == 'spkr_simp'",
                         sliderInput(inputId="topx_spkr", label = h4("No. of speakers to display"),
                                     min   =  2,
                                     max   = 25,
                                     value = 10
                                     )),
        
        # SPKR - speaker by name----
        conditionalPanel(condition="input.gen_plottype == 'spkr_simp'",
                         textInput(inputId="text_spkr", label = h4("Search additional speaker to display"),
                                   value = "",
                                   placeholder = "Type here to add"
                         )),
        conditionalPanel(condition="input.gen_plottype == 'spkr_simp'",
                         sliderInput(inputId="textspkr_no", label=h4("Number of found speakers to display"),
                                     min=0, max=5,
                                     value=2)),
        
        # META - format of debate & sponsor----
        conditionalPanel(
          # debate format
          condition="input.gen_plottype == 'meta'",
          orderInput(inputId="meta_format_display", label=h4("Debate formats to display (order-sensitive)"),
                     placeholder = "Drag items here..",
                     width="100%",
                     connect = "meta_format_ignore",
                     items = c('Consultation',
                               'Resolution',
                               'Report',
                               "Questioning gov't",
                               'Current affairs',
                               "Gov't statement",
                               'Response',
                               'Election',
                               'Swearing in',
                               'Other')
          ),
          orderInput(inputId="meta_format_ignore", label=h4("Debate formats to display (order-sensitive)"),
                     placeholder = "Drag items here..",
                     width="100%",
                     connect = "meta_format_display",
                     items=NULL
          ),
          # sponsor
          orderInput(inputId="meta_sponsor_display", label=h4("Debate sponsors to display"),
                     placeholder = "Drag items here..",
                     width="100%",
                     connect = "meta_sponsor_ignore",
                     items = c("CDU/CSU" = "cxu",
                               "SPD" = "spd", 
                               "B90/Gruene" = "b90", 
                               "FDP" = "fdp", 
                               "Die Linke" = "lnk", 
                               "AfD" = "afd",
                               "Gov't coalition" = 'gov',
                               "Uncategorized" = "oth")
          ),
          orderInput(inputId="meta_sponsor_ignore", label=h4("Debate sponsors to display (order-sensitive)"),
                     placeholder = "Drag items here..",
                     width="100%",
                     connect = "meta_sponsor_display",
                     items=NULL
          )
                         
                         
        )
        
        
                          
        
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
        ),
        
        conditionalPanel(condition="input.gen_plottype == 'meta'",
                         jqui_resizable(plotOutput("meta_plot")),
                         # explanations
                         #br(),
                         #helpText(HTML(paste0("Key to official German terminology: ",
                         #                     "Consultation: <i>Beratung</i>, ",
                         #                     "Resolution: <i>Beschlussempfehlung</i>, ",
                         #                     "Report: <i>Bericht</i>, ",
                         #                     "Questioning gov't: <i>Fragestunde</i> & <i>Regierungsbefragung</i>, ",
                         #                     "Current affairs: <i>Aktuelle Stunde</i>, ",
                         #                     "Gov't statement: <i>Regierungserklärung</i>, ",
                         #                     "Response: <i>Antwort</i>, ",
                         #                     "Election: <i>Wahl</i>, ",
                         #                     "Swearing in: <i>Eidleistung</i>")))
                         
        )
      )
      }  
  )
)
}

# Define server logic 
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
  
  # construct data_meta dataset
  dataset_meta <- reactive({
    speeches_meta_sponsor %>% 
      # filter rows
      filter( (date > input$gen_daterange[1]) & (date < input$gen_daterange[2]),
              origin_pty %in% input$gen_originpty_display,
              sponsor %in% input$meta_sponsor_display,
              meta %in% input$meta_format_display) %>% 
      # re-order factors
      mutate(origin_pty = fct_relevel(origin_pty, input$gen_originpty_display),
             sponsor = fct_relevel(sponsor, input$meta_sponsor_display),
             meta = fct_relevel(meta, rev(input$meta_format_display)))
  })
  
  # plots
  {
    # freq_plot
    output$freq_plot <-
      renderPlot({
        dataset <- dataset_freq()
        
        # initialize freq_plot
        freq_p <- 
          ggplot(data=dataset, aes(x=.data[[input$simp_var]], fill=origin_pty))
        
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
          scale_x_continuous(name=paste0(dict_vars[input$simp_var], " emotive appeals per 100 words"),
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
          ggtitle(paste0(dict_vars[input$simp_var], " emotive appeals per 100 words\n(", input$gen_daterange[1] %>% as.yearmon(.), "\u2013", input$gen_daterange[2] %>% as.yearmon(.), ")")) +
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
          
          labs(y="", x = paste0(dict_vars[input$spkr_simp_var], " emotive appeals per 100 words, by speaker")) +
          theme(
            axis.text.y = element_text(size=14),
            legend.position="bottom") +
          guides(color=guide_legend(title = "Speaker party", nrow=1, byrow=TRUE))
      })
    
    # agenda item plot
    output$meta_plot <-
      renderPlot({
        # variable selection
        {
          if(input$simp_var=="agg_emo"){    dataset <- dataset_meta() %>% rename(var=agg_emo) %>% select(date, origin_pty, meta, sponsor, var)}
          if(input$simp_var=="abs_neg_emo"){dataset <- dataset_meta() %>% rename(var=abs_neg_emo) %>% select(date, origin_pty, meta, sponsor, var)}
          if(input$simp_var=="pos_emo"){    dataset <- dataset_meta() %>% rename(var=pos_emo) %>% select(date, origin_pty, meta, sponsor, var)}
        }
        
        ggplot(data=dataset %>% 
                 group_by(origin_pty, meta, sponsor) %>% 
                 summarize(.groups="keep", var=sum(var, na.rm=T)) %>% 
                 ungroup(), 
               aes(y=meta, x=var, fill=origin_pty)) +
          geom_bar(stat = 'identity') +
          scale_f_pties +
          labs(x="Appeals per 100 words", y="") + 
          ggtitle(paste0(dict_vars[input$simp_var], " emotive appeals per 100 words\n(", input$gen_daterange[1] %>% as.yearmon(.), "\u2013", input$gen_daterange[2] %>% as.yearmon(.), ")")) +
          theme_minimal() +
          theme(legend.position="bottom") +
          guides(fill=guide_legend(title = "Speaker party", nrow=1, byrow=TRUE)) +
          
          facet_wrap(~sponsor, ncol = 2, labeller = as_labeller(c("afd"="AfD-sponsored agenda items",
                                                                  "b90"="Greens-sponsored agenda items", 
                                                                  "cxu"="CDU/CSU-sponsored agenda items",
                                                                  "fdp"="FDP-sponsored agenda items",
                                                                  "lnk"="Left=sponsored agenda items",
                                                                  "spd"="SPD-sponsored agenda items",
                                                                  "gov"="Government-sponsored agenda items",
                                                                  "oth"="Unknown sponsor of agenda items")))
      })
  
  
    
    }
  }
}

# Run the application 
shinyApp(ui = ui, server = server)

