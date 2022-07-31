#.######################################################.#
# This script loads the RDS file "Corp_Bundestag_V2.rds" #
#  selects the needed rows (from 2009 onwards)           #
#  and makes it available for use in python by exporting #
#  it as csv file.                                       #
#.######################################################.#

# data available from: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/L4OAKN

library(tidyverse)
#library(stringr)
setwd("C:/Users/bantel/Documents/GitHub-repos/parlspeech_GER")

# -BUNDESTAG----
# load Bundestag Data from ParlSpeech as tibble
bundestag_full <- read_rds("./data/0-Corp_Bundestag_V2.rds") %>% tibble() 

# parse date column
bundestag_full <- bundestag_full %>% mutate(date = lubridate::ymd(date)) 

# remove unneeded columns & rows
bundestag <- bundestag_full %>% 
  filter(
    date > "2009-01-10", # only keep newest legislatures
    chair == FALSE) %>% # drop "speeches" by the Bundestagspräside:innen
  select(-c(party.facts.id, chair, parliament, iso3country)) # remove unneeded columns

# overview of speeches
ggplot(bundestag, aes(x = date)) + 
  labs(title="Speeches in German Bundestag (excl. chair interventions)", x="Date", y = "Number of speeches", caption = paste("N =", dim(bundestag)[1], "speeches")) + 
  geom_histogram(binwidth = 120) + theme_minimal() # inspect dates; 10 years * 12 months ~ monthly breaks

dim(bundestag)
min(bundestag$date)
max(bundestag$date)

# write data
bundestag %>% 
  write_csv(file = "./data/1-R-preproc_Corp_Bundestag_V2-nochairinterv-2009ff.csv") 
# correctly writes Umlaute. Excel only displays them wrongly.

rm(bundestag, bundestag_full)
