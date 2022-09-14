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
shinyUI(
  fluidPage(
    # Application title
    titlePanel("Emotive parliamentary speech in the German Bundestag"),
    helpText("Plot occurrence of emotive parliamentary speech over time"),
    br(),
    
    # Sidebar
    sidebarLayout(
      
      # sidebar panel
      sidebarPanel(
        # GEN - date range----
        sliderInput(inputId="gen_daterange", label=h4("Date range:"),
                    min = speeches_num$date %>% min(),
                    max = speeches_num$date %>% max(),
                    value = c(as.Date("2010-01-01", "%Y-%m-%d"), as.Date("2020-01-01", "%Y-%m-%d")),
                    timeFormat="%m/%Y"),
        br(),
        # GEN - variable of interest----
        radioButtons(inputId="freq_var", label=h4("Measure:"),
                     choices = c("Aggregate appeals (positive - negative)" = "agg_emo",
                                 "Negative appeals" = "abs_neg_emo",
                                 "Positive appeals" = "pos_emo")),
        # FREQ - upper bound----
        sliderInput(inputId="freq_cutoffs", label = h4("Bounds:"),
                    min =    1,
                    max =   80,
                    value = c(1, 25)),
        
        # FREQ::HIST - histogram breaks (conditional panel)----
        conditionalPanel("input.freq_plottype == 'hist'",
                         sliderInput(inputId="hist_bins", label = h4("No. of bins:"),
                                     min =   3,
                                     max =  50,
                                     value =15)
        ),
        
        # GEN - origin party----
        checkboxGroupInput(inputId = "gen_originpty", label = "Speaker party:",
                           choices = c("Conservatives (CDU/CSU)" = "cxu",
                                       "Social Democrats (SPD)" = "spd", 
                                       "Greens (B90/Gruene)" = "b90", 
                                       "Liberals (FDP)" = "fdp", 
                                       "Left (Die Linke)" = "lnk", 
                                       "Radical Right (AfD)" = "afd"),
                           selected = c("cxu", "spd", "b90", "fdp", "lnk", "afd"))
      ),
      
      # main panel----
      mainPanel(
        tabsetPanel(
          type="tabs",
          tabPanel(title = "Frequency plot", value="tab_freq_plot",
                   fluidRow(
                     br(),
                     column(width=12, align="center",
                       radioButtons(inputId="freq_plottype", label=h4("Visualize frequencies as:"),
                                    choices = c("Histogram"     = "hist", "Density plot"= "dens"),
                                    inline=TRUE)
                       )
                             ),
                   plotOutput("freq_plot")
          ),
          tabPanel(title="Time series plot", value="tab_time_plot",
                   fluidRow(
                     br(),
                     column(width=12, align="center",
                            radioButtons(inputId="time_var", label=h4("Var to display"),
                                         choices=c("Aggregate"="agg",
                                                   "Neg and Pos"="neg_pos",
                                                   "Neg"="neg",
                                                   "Pos"="pos"),
                                         inline=TRUE,
                                         selected="agg")
                     )
                   ),
                   
                   
                   plotOutput("time_plot"))
        )
      )
    )
  )
)

