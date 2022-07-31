"""
    This script:
        (1) loads data frames of German parliamentary speeches from ParlSpeech into csv
                (prepared in 000-rds-[...].R)
                data: https://dataverse.harvard.edu/dataverse/opendiscourse
                description: https://open-discourse.github.io/open-discourse-documentation/1.1.0/index.html

        (2) combines data sets of speeches with data on party/ faction, speaker, and electoral terms

--------(3) pre-processes combined data (cleaning, recoding)

--------(4) splits speeches up into sentence-rows

--------(5) converts sentences to spacy object (applies language model)

--------(6) saves data in chunks of 100k rows as pickle objects

    Later ToDos are marked with "###!!!"


"""

# %% (0) load dependencies

import datetime as dt
import nltk
import numpy as np
import os
import pandas as pd
import pickle
import spacy
import timeit

# costum helpers
from helpers.party_dict import party_remapping as hlp_party_remapping
from helpers.sentencize_df_explode import sentencize_df_explode as hlp_sentencize_df_explode
from helpers.chunked_pickle_save_load import chunked_save_as_pickles as hlp_chunked_save_as_pickles

# spacy corpus
nlp = spacy.load("de_core_news_lg")  # to install: [s above]

# base folder
from helpers.folder_base import folder_base
folder_base: str = r"C:\Users\Bantel\Documents\GitHub-repos\parlspeech_GER"

# %% (1) Load data

file_bt: str = r"\data\1-R-preproc_Corp_Bundestag_V2-nochairinterv-2009ff.csv"

bt: pd.DataFrame = pd.read_csv(folder_base + file_bt) # .head(10)#performance

# %% (2) Clean & Filter Data

if 'party' in bt.columns:
    bt.rename(columns = {'party': 'origin_pty'}, inplace=True)
if 'terms' in bt.columns:
    bt = bt.rename(columns={'terms': 'speech_terms'})

bt['date'] = pd.to_datetime(bt['date'])

bt['origin_pty'] = bt['origin_pty'].replace(party_remapping) # clean origin party column

bt['state'] = 'DE' # include column for the state (for consistentcy with state parliament analysis)

bt = bt.loc[bt['date'] > '2009-09-22', :]  # first session: 2009-10-27

bt['origin_pty'].replace(party_remapping, inplace=True)  # clean pty abbr.s

bt = bt.loc[bt['origin_pty'].isin(['afd', 'cxu', 'lnk', 'fdp', 'b90', 'spd']), :]  # keep only speeches by MPs of major factions
del party_remapping

bt = bt.loc[bt['text'].notna(), :]  # drop speeches where text is NaN

# cell manipulation
bt['text'] = bt['text'].replace(r'\n', ' ', regex=True)  # remove new lines from speeches
bt['text'] = bt['text'].replace(r'\(\{\d+\}\)', '', regex=True)  # remove ({0}) etc. from speeches
# remove patterns of numbers followed by dot and month name or specific words found ## takes ca 5min
bt['text'] = bt['text'].replace(r'(?<=\d)\.\sJanuar', ' Januar', regex=True)
bt['text'] = bt['text'].replace(r'(?<=\d)\.\sFebruar', ' Februar', regex=True)
bt['text'] = bt['text'].replace(r'(?<=\d)\.\sMärz', ' März', regex=True)
bt['text'] = bt['text'].replace(r'(?<=\d)\.\sApril', ' April', regex=True)
bt['text'] = bt['text'].replace(r'(?<=\d)\.\sMai', ' Mai', regex=True)
bt['text'] = bt['text'].replace(r'(?<=\d)\.\sJuni', ' Juni', regex=True)
bt['text'] = bt['text'].replace(r'(?<=\d)\.\sJuli', ' Juli', regex=True)
bt['text'] = bt['text'].replace(r'(?<=\d)\.\sAugust', ' August', regex=True)
bt['text'] = bt['text'].replace(r'(?<=\d)\.\sSeptember', ' September', regex=True)
bt['text'] = bt['text'].replace(r'(?<=\d)\.\sOktober', ' Oktober', regex=True)
bt['text'] = bt['text'].replace(r'(?<=\d)\.\sNovember', ' November', regex=True)
bt['text'] = bt['text'].replace(r'(?<=\d)\.\sDezember', ' Dezember', regex=True)
bt['text'] = bt['text'].replace(r'(?<=\d)\.\sLesung', ' Lesung', regex=True)
bt['text'] = bt['text'].replace(r'(?<=\d)\.\sJahrestag', ' Jahrestag', regex=True)
bt['text'] = bt['text'].replace(r'(?<=\d)\.\sJahr', ' Jahr', regex=True)
bt['text'] = bt['text'].replace(r'(?<=\d)\.\sDeutschen\sBundestages', ' Deutschen Bundestages', regex=True)
bt['text'] = bt['text'].replace(r'(?<=\d)\.\sJubiläumsjahr', ' Jubiläumsjahr', regex=True)
bt['text'] = bt['text'].replace(r'(?<=\d)\.\sGeburtstag', ' Geburtstag', regex=True)
bt['text'] = bt['text'].replace(r'(?<=\d)\.\sMale', ' Male', regex=True)
bt['text'] = bt['text'].replace(r'(?<=\d)\.\sVertragsstaatenkonferenz', ' Vertragsstaatenkonferenz', regex=True)
bt['text'] = bt['text'].replace(r'(?<=\d)\.\sKonferenz', ' Konferenz', regex=True)


print(f"The data frame 'speeches' has {bt.shape[0]} rows and {bt.shape[1]} columns.")  # (66635, 7)

# %% (3) Split speeches into sentences

bt_long = sentencize_df_explode(df=bt, textcol_in='text', sentencecol_out='sentence')  # explode df
# The operation took 118.253 seconds.

print(f"The data frame 'speeches_long' has {bt_long.shape[0]} rows and {bt_long.shape[1]} columns.")  # (2391579, 8)

# %% (4) Convert sentences to spacy object (apply language model)

starttime = timeit.default_timer()
bt_long['processed_sentence'] = \
    [doc for doc in nlp.pipe(bt_long['sentence'].tolist())]  # faster than apply
# https://stackoverflow.com/questions/63057742/best-method-for-creating-python-spacy-nlp-objects-from-a-pandas-series

print(f"The operation took {timeit.default_timer() - starttime:.3f} seconds.")
# The operation took 5683.248 seconds [using nlp.pipe()]
del starttime

type(bt_long.at[1, 'processed_sentence'])  # check that cell contains a spaCy Doc object

# %% (5) Declutter result before saving

bt_long = bt_long.drop(columns=['text'])  # drop column with entire speech

# %% (6) Save data as pickle chunks (to preserve spacy objects)
chunked_save_as_pickles(df=bt_long, length_chunks=100000, filename_base="bt_parlspeech",
                        save_path=folder_base + r"\data\2-preprocessing-out")  # gives 21 chunks (from 2009 onwards)
# The saving process took 2969.308 seconds.

