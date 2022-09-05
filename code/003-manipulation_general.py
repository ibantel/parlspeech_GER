"""
    This script:
        takes in data frame with looked up sentences that contain detected emotions
        performs data manipulation to transform the raw data into dyadic data
        xxxx # TODO
"""


# %% Load packages & import costum helpers
from datetime import datetime as dt
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# %% Load data
try:
    from helpers.folder_base import *
except ModuleNotFoundError:
    folder_base: str = 'C:\\Users\\Bantel\\Documents\\GitHub-repos\\parlspeech_GER'

folder_3_matching_out: str = '\\data\\3-matching-out'

bt_file: str = "\\" + [f for f in os.listdir(folder_base + folder_3_matching_out) if
                       f.endswith("bt_all_sents_no_matchwords_emo.csv")][-1]

bt_long: pd.DataFrame =\
    pd.read_csv(folder_base + folder_3_matching_out + bt_file).drop(columns=['Unnamed: 0', 'sentence'])

del bt_file

# %%

dict_agenda_cleaning: dict = {
    "Tagesordnungspunkt(e)?\s*\d*\s*((?![u])[a-z])?\s*(und|bis)?\s*\d*\s*((?![u])[a-z])?\s*:\s*": "",
     # matches:
     # Tagesordnungspunkt 23: l
     # Tagesordnungspunkt 23:l
     # Tagesordnungspunkt23: l
     # Tagesordnungspunkt: l
     # Tagesordnungspunkte 23 und 24: l
     # Tagesordnungspunkt 21a und 21b:l
     # Tagesordnungspunkt 21a und 21b: l
     # Tagesordnungspunkte 21 a und 21 b:
     # Tagesordnungspunkt 23: l
     # Tagesordnungspunkt 23: l
     # Tagesordnungspunkt 23: l
     # Tagesordnungspunkt 23: l
     # Tagesordnungspunkt 23: l
     # Tagesordnungspunkt 1: l
     # Tagesordnungspunkt 7 a bis 7 d: l
    "Beratung\s*(des|der)\s*(Antrags|Beschlussempfehlung)\s*(und)?\s*(des)?\s*(Bericht(s)?)?\s*(des|der)?\s*(Ausschuss(es)?\s*für\s*)?": "",
    # matches:
    # Beratung der Beschlussempfehlung und des Berichts des
    # Beratung des Antrags der
    # Beratung der Beschlussempfehlung und des Berichts des Ausschusses für
    "Dr\.\s*" : "",
    "Abgeordneten\s*(.+)\s*weiterer\s*Abgeordneter\s*und\s*der\s*Fraktion\s*(der)?\s*(CDU\/CSU|SPD|FDP|AfD|DIE\s*LINKE|Die\s*Linke|BÜNDNIS\s*90\/DIE\s*GRÜNEN|Bündnis\s*90\/Die\s*Grünen)?\s*" : "",
    # matches "Abgeordneten\s*[anything]\s*weiterer" (usw.)
    # "1) Anlage 7  "
    # "U+00AD"

     }

# Drucksachen
# Antwort
# Bundesregierung


lst = bt_long['agenda'].replace(dict_agenda_cleaning, regex=True).unique().tolist()

for i in lst:
    if i.startswith("Beratung"):
        print(i, end='\n\n')


# analyse agenda points to different topics
