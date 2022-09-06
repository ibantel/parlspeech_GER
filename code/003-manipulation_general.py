"""
    This script:
        takes in data frame with looked up sentences that contain detected emotions
        performs data manipulation to transform the raw data into dyadic data
        xxxx # TODO
"""


# %% Load packages & import costum helpers
from datetime import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import spacy

nlp = spacy.load("de_core_news_lg")

try:
    from helpers.parties_patterns import *
except ModuleNotFoundError:
    print("failed to load modules. do so manually and fix")

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

# %% Cleaning (tmp, discarded)
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

lst = bt_long['agenda'].head(10).replace(dict_agenda_cleaning, regex=True).unique().tolist()

for i in lst:
    print(i, end='\n\n')

# %% Matcher: meta (what kind of debate?)

agenda_matcher_meta = spacy.matcher.Matcher(nlp.vocab)  # instantiate Matcher

agenda_patterns_meta_beratung: list = [[{'LOWER': {'IN': ['Beratung']}, 'POS': 'PROPN'}]]
agenda_patterns_meta_beschlem: list = [[{'LOWER': {'IN': ['Beschlussempfehlung', 'Beschlussempfehlungen']}, 'POS': 'PROPN'}]]
agenda_patterns_meta_bericht_: list = [[{'LOWER': {'IN': ['Bericht', 'Berichts', 'Berichtes']}, 'POS': 'PROPN'}]]
agenda_patterns_meta_fragstun: list = [[{'LOWER': {'IN': ['Fragestunde', 'Fragestunden']}, 'POS': 'PROPN'}]]
agenda_patterns_meta_befragun: list = [[{'LOWER': {'IN': ['Befragung', 'Befragungen']}, 'POS': 'PROPN'}]]
agenda_patterns_meta_aktustnd: list = [[{'LOWER': 'Aktuelle'}, {'LOWER': 'Stunde'}]]
agenda_patterns_meta_regerklr: list = [[{'LOWER': {'IN': ['Regierungserklärung']}, 'POS': 'PROPN'}]]
agenda_patterns_meta_antwort_: list = [[{'LOWER': {'IN': ['Antwort']}, 'POS': 'PROPN'}]]
agenda_patterns_meta_wahl____: list = [[{'LOWER': {'IN': ['Wahl', 'Wahlen']}, 'POS': 'PROPN'}]]
agenda_patterns_meta_eidleist: list = [[{'TEXT':  {'REGEX': '(E|e)id(es)?leistung(en)?'}}]]

# add matcher patterns
agenda_matcher_meta.add(101, agenda_patterns_meta_beratung)
agenda_matcher_meta.add(102, agenda_patterns_meta_beschlem)
agenda_matcher_meta.add(103, agenda_patterns_meta_bericht_)
agenda_matcher_meta.add(104, agenda_patterns_meta_fragstun)
agenda_matcher_meta.add(105, agenda_patterns_meta_befragun)
agenda_matcher_meta.add(106, agenda_patterns_meta_aktustnd)
agenda_matcher_meta.add(107, agenda_patterns_meta_regerklr)
agenda_matcher_meta.add(108, agenda_patterns_meta_antwort_)
agenda_matcher_meta.add(109, agenda_patterns_meta_wahl____)
agenda_matcher_meta.add(110, agenda_patterns_meta_eidleist)

meta_values: tuple = tuple([i for i in range(101, 111)])
meta_column_mapper: dict = {101: "beratung",
                            102: "beschlem",
                            103: "bericht_",
                            104: "fragstun",
                            105: "befragun",
                            106: "aktustnd",
                            107: "regerklr",
                            108: "antwort_",
                            109: "wahl____",
                            110: "eidleist"}


# %% Matcher: BReg (was gov't mentioned?)

agenda_matcher_breg = spacy.matcher.Matcher(nlp.vocab)  # instantiate Matcher

agenda_patterns_breg_breg: list = [[{'TEXT':  {'REGEX': '(Bundes)?(R|r)egierung'}}]]
agenda_patterns_breg_coal: list = [[{'TEXT':  {'REGEX': '(Regierungs)?(K|k)oalition'}}]]

# add matcher patterns
agenda_matcher_breg.add(  1, agenda_patterns_breg_breg)
agenda_matcher_breg.add(  1, agenda_patterns_breg_coal)

breg_values: tuple = (1, 1)
breg_column_mapper: dict = {  1: "govt"}

# %% Matcher: faction (whose topic is debated?)

agenda_matcher_fctn = spacy.matcher.Matcher(nlp.vocab)  # instantiate Matcher

agenda_patterns_fctn_afd: list = [[{'LOWER':  {'IN':    ['AfD', 'AFD', 'afd', 'Alternative für Deutschland']}}]]
agenda_patterns_fctn_b90: list = [[{'LOWER':  {'IN':    ['(BÜNDNIS 90', 'DIE GRÜNEN)']}}]]
agenda_patterns_fctn_cxu: list = [[{'TEXT' :  {'REGEX':  '(C|c)(D|d|S|s)(U|u)'}}],
                                  [{'TEXT' :  {'REGEX':  'CDU/\s*CSU'}}],
                                  [{'TEXT' :  {'REGEX':  'Union(s)?(\-)?\s*(F|f)raktion'}}]]
agenda_patterns_fctn_fdp: list = [[{'LOWER':  {'IN':    ['FDP']}}]]
agenda_patterns_fctn_lnk: list = [[{'LOWER':  {'IN':    ['DIE LINKE']}}]]
agenda_patterns_fctn_spd: list = [[{'LOWER':  {'IN':    ['SPD']}}]]

# add matcher patterns
agenda_matcher_fctn.add(101, agenda_patterns_fctn_afd)
agenda_matcher_fctn.add(102, agenda_patterns_fctn_b90)
agenda_matcher_fctn.add(103, agenda_patterns_fctn_cxu)
agenda_matcher_fctn.add(104, agenda_patterns_fctn_fdp)
agenda_matcher_fctn.add(105, agenda_patterns_fctn_lnk)
agenda_matcher_fctn.add(106, agenda_patterns_fctn_spd)

fctn_values: tuple = tuple([i for i in range(101, 107)])
fctn_column_mapper: dict = {101: "afd",
                            102: "b90",
                            103: "cxu",
                            104: "fdp",
                            105: "lnk",
                            106: "spd"}

# %% Matcher topic (which committee?)
print("", end="")
# Thema: Ausschuss für x
# analyse agenda points to different topics
print("", end="")

# %% Apply matcher

bt_long['agenda_processed'] = \
    [doc for doc in nlp.pipe(bt_long['agenda'].tolist())]  # faster than apply

bt_long['matches_meta'] = bt_long['agenda_processed'].apply(agenda_matcher_meta)  # match patterns
bt_long['matches_breg'] = bt_long['agenda_processed'].apply(agenda_matcher_breg)  # match patterns
bt_long['matches_fctn'] = bt_long['agenda_processed'].apply(agenda_matcher_fctn)  # match patterns

print("")