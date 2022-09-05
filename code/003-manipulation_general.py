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
    "Tagesordnungspunkt(e|en|es)?": "",
    "Einzelplan(s)?" : "",
    "Drucksache(n)?" : "",
    "Zusatzpunkt": "",
    "ZP": "",
    # Numbers
    "\d+" : "",
    "\b(I\.*|II\.*|III\.*|IV\.*|V\.*|VI\.*|VII\.*|VIII\.*|IX\.*|X\.*|XI\.*|XII\.*)\b" : "",
    "[a-z]\)\s*" : "",
    "\s*:": "",


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

"""
matcher_meta:
    "Beratung"
    "Beschlussempfehlung"
    "Bericht(s)" 
    "Fragestunde"
    "Befragung"
    "Aktuelle\s*Stunde"
    "Regierungserklärung"
    "Antwort"
    "Wahl"
    "Eidesleistung"

matcher_BReg:
    "Bundesregierung"

matcher_Antrag:
    Antrag von [fraktion]

Thema:
    Ausschuss für x
"""

lst = bt_long['agenda'].head(100000).replace(dict_agenda_cleaning, regex=True).unique().tolist()

for i in lst:
    print(i, end='\n\n')


# analyse agenda points to different topics


print("i")