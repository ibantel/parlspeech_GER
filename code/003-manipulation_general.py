"""
    This script:
        takes in data frame with looked up sentences that contain detected emotions
        performs data manipulation to transform the raw data into dyadic data
        xxxx # TODO
"""


import spacy

import numpy as np
import os
import pandas as pd
# %% Load packages & import costum helpers
from datetime import datetime as dt

nlp = spacy.load("de_core_news_lg")

try:
    from helpers.ed8_patterns import *
    from helpers.parties_patterns import *
    from helpers.ed8_patterns import count_tup_first_values
    from helpers.validation_helpers import token_from_spacy_match
except ModuleNotFoundError:
    print("failed to load modules. do so manually and fix")

# %% Load data
try:
    from code.helpers.folder_base import *
except ModuleNotFoundError:
    folder_base: str = 'C:\\Users\\Bantel\\Documents\\GitHub-repos\\parlspeech_GER'

folder_3_matching_out: str = '\\data\\3-matching-out'

bt_file: str = "\\" + [f for f in os.listdir(folder_base + folder_3_matching_out) if
                       f.endswith("bt_all_sents_no_matchwords_emo.csv")][-1]

bt_long: pd.DataFrame =\
    pd.read_csv(folder_base + folder_3_matching_out + bt_file).drop(columns=['Unnamed: 0', 'sentence'])

del bt_file

# %% Group data by speech (aggregating xxx_emo)
bt_long_speeches: pd.DataFrame = \
    bt_long.groupby(['date', 'agenda', 'speechnumber', 'speaker', 'origin_pty', 'speech_terms']).sum().reset_index()

# %% Cleaning (tmp, discarded)
if False:
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

agenda_patterns_meta_beratung: list = [[{'LOWER': {'IN': ['beratung']}}]]
agenda_patterns_meta_beschlem: list = [[{'LOWER': {'IN': ['beschlussempfehlung', 'beschlussempfehlungen']}}]]
agenda_patterns_meta_bericht_: list = [[{'LOWER': {'IN': ['bericht', 'berichts', 'berichtes']}}]]
agenda_patterns_meta_fragstun: list = [[{'LOWER': {'IN': ['fragestunde', 'fragestunden']}}]]
agenda_patterns_meta_befragun: list = [[{'LOWER': {'IN': ['befragung', 'befragungen']}}]]
agenda_patterns_meta_aktustnd: list = [[{'LOWER': {'IN': ['aktuelle']}}]]
agenda_patterns_meta_regerklr: list = [[{'LOWER': {'IN': ['regierungserklärung']}}]]
agenda_patterns_meta_antwort_: list = [[{'LOWER': {'IN': ['antwort']}}]]
agenda_patterns_meta_wahl____: list = [[{'LOWER': {'IN': ['wahl', 'wahlen']}}]]
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
meta_column_mapper: dict = {101: "meta_beratung",
                            102: "meta_beschlem",
                            103: "meta_bericht_",
                            104: "meta_fragstun",
                            105: "meta_befragun",
                            106: "meta_aktustnd",
                            107: "meta_regerklr",
                            108: "meta_antwort_",
                            109: "meta_wahl____",
                            110: "meta_eidleist"}


# %% Matcher: govt (was gov't mentioned?)

agenda_matcher_govt = spacy.matcher.Matcher(nlp.vocab)  # instantiate Matcher

agenda_patterns_govt_breg: list = [[{'TEXT':  {'REGEX': '(Bundes)?(R|r)egierung'}}]]
agenda_patterns_govt_coal: list = [[{'TEXT':  {'REGEX': '(Regierungs)?(K|k)oalition'}}]]
agenda_patterns_govt_chnc: list = [[{'TEXT':  {'REGEX': '(Bundes)?(K|k)anzler(in)?'}}]]
agenda_patterns_govt_mnst: list = [[{'TEXT':  {'REGEX': '(Bundes)?(M|m)inister(in)?'}}]]

# add matcher patterns
agenda_matcher_govt.add(  1, agenda_patterns_govt_breg)
agenda_matcher_govt.add(  1, agenda_patterns_govt_coal)
agenda_matcher_govt.add(  2, agenda_patterns_govt_chnc)
agenda_matcher_govt.add(  3, agenda_patterns_govt_mnst)

govt_values: tuple = (1, 2, 3)
govt_column_mapper: dict = {  1: "govt_government",
                              2: "govt_chancellor",
                              3: "govt_minister"}


# %% Matcher: faction (whose topic is debated?)

agenda_matcher_fctn = spacy.matcher.Matcher(nlp.vocab)  # instantiate Matcher

agenda_patterns_fctn_afd: list = [[{'LOWER':  {'IN':    ['afd', 'alternative für deutschland']}}]]
agenda_patterns_fctn_b90: list = [[{'LOWER':  {'IN':    ['(bündnis 90', 'die grünen)']}}]]
agenda_patterns_fctn_cxu: list = [[{'TEXT' :  {'REGEX':  '(C|c)(D|d|S|s)(U|u)'}}],
                                  [{'TEXT' :  {'REGEX':  'CDU/\s*CSU'}}],
                                  [{'TEXT' :  {'REGEX':  'Union(s)?(\-)?\s*(F|f)raktion'}}]]
agenda_patterns_fctn_fdp: list = [[{'LOWER':  {'IN':    ['fdp']}}]]
agenda_patterns_fctn_lnk: list = [[{'LOWER':  {'IN':    ['die linke']}}]]
agenda_patterns_fctn_spd: list = [[{'LOWER':  {'IN':    ['spd']}}]]

# add matcher patterns
agenda_matcher_fctn.add(101, agenda_patterns_fctn_afd)
agenda_matcher_fctn.add(102, agenda_patterns_fctn_b90)
agenda_matcher_fctn.add(103, agenda_patterns_fctn_cxu)
agenda_matcher_fctn.add(104, agenda_patterns_fctn_fdp)
agenda_matcher_fctn.add(105, agenda_patterns_fctn_lnk)
agenda_matcher_fctn.add(106, agenda_patterns_fctn_spd)

fctn_values: tuple = tuple([i for i in range(101, 107)])
fctn_column_mapper: dict = {101: "fctn_afd",
                            102: "fctn_b90",
                            103: "fctn_cxu",
                            104: "fctn_fdp",
                            105: "fctn_lnk",
                            106: "fctn_spd"}

# %% Matcher topic (which committee?)
print("", end="")
# Thema: Ausschuss für x
# analyse agenda points to different topics
print("", end="")

# %% Clean agenda column

bt_long_speeches['agenda_clean'] = bt_long_speeches['agenda'].str.split(':', n=1, expand=False).str[1].str.lstrip()  # remove "Tagesordnungspunkt

bt_long_speeches['agenda_clean'].fillna(bt_long_speeches['agenda'], inplace=True)  # keep agenda points without ":"

del bt_long_speeches['agenda']

# %% Apply matchers

testing: bool = False
if testing:
    print("performing matching on subset for testing")
    bt_long_speeches_copy = bt_long_speeches.copy(deep=True)
    bt_long_speeches = bt_long_speeches_copy.head(1000)

    sample_str: str = "".join([i for i in (bt_long_speeches['agenda_clean'].tail(1))]).strip()
    sample_doc: spacy.tokens.doc.Doc = nlp(sample_str)
    sample_matches = agenda_matcher_meta(sample_doc)

bt_long_speeches.loc[:, 'agenda_processed'] = [doc for doc in nlp.pipe(bt_long_speeches['agenda_clean'].tolist())]  # faster than apply
bt_long_speeches.loc[:, 'matches_meta'] = bt_long_speeches['agenda_processed'].apply(agenda_matcher_meta)  # match patterns
bt_long_speeches.loc[:, 'matches_govt'] = bt_long_speeches['agenda_processed'].apply(agenda_matcher_govt)  # match patterns
bt_long_speeches.loc[:, 'matches_fctn'] = bt_long_speeches['agenda_processed'].apply(agenda_matcher_fctn)  # match patterns

# %% Clean matches

print("", end="")

# meta
bt_long_speeches = bt_long_speeches.join(bt_long_speeches['matches_meta'].apply(
    count_tup_first_values, args=(meta_values,)))  # aggregate emo matches: extract values & rejoin
bt_long_speeches = bt_long_speeches.rename(columns=meta_column_mapper)  # optional columns renaming

bt_long_speeches['matchwords_meta'] =\
        bt_long_speeches.apply(lambda x: token_from_spacy_match(x['matches_meta'], x['agenda_processed']), axis=1)

# govt
bt_long_speeches = bt_long_speeches.join(bt_long_speeches['matches_govt'].apply(
    count_tup_first_values, args=(govt_values,)))  # aggregate emo matches: extract values & rejoin
bt_long_speeches = bt_long_speeches.rename(columns=govt_column_mapper)  # optional columns renaming

bt_long_speeches['matchwords_govt'] =\
        bt_long_speeches.apply(lambda x: token_from_spacy_match(x['matches_govt'], x['agenda_processed']), axis=1)

# fctn
bt_long_speeches = bt_long_speeches.join(bt_long_speeches['matches_fctn'].apply(
    count_tup_first_values, args=(fctn_values,)))  # aggregate emo matches: extract values & rejoin
bt_long_speeches = bt_long_speeches.rename(columns=fctn_column_mapper)  # optional columns renaming

bt_long_speeches['matchwords_fctn'] =\
        bt_long_speeches.apply(lambda x: token_from_spacy_match(x['matches_fctn'], x['agenda_processed']), axis=1)

# combine govt
bt_long_speeches['govt'] = np.where(((bt_long_speeches['govt_government'] + bt_long_speeches['govt_chancellor'] + bt_long_speeches['govt_minister']) > 0), 1, 0)


# %% Save intermediary result
save_path_name: str = folder_base + "\data\\3-matching-out\\" + dt.now().strftime("%Y-%m-%d-%H%M")
filename: str = "_bt_all_debates_emo_agenda_"

# save full csv file
bt_long_speeches.to_csv(save_path_name + filename + "full.csv")

# save numeric columns only
bt_long_speeches.\
    drop(columns=['matchwords_meta', 'matchwords_govt', 'matchwords_fctn',
                  'govt_government', 'govt_chancellor', 'govt_minister',
                  'agenda_processed', 'agenda_clean', 'matches_meta', 'matches_govt', 'matches_fctn']).\
    to_csv(save_path_name + filename + "numeric.csv")
