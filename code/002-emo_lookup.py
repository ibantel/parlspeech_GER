"""
    This script:
        looks up sentences that contain emotion words according to ed8 dictionary
        saves intermediary result containing all rows (also without matches)

    Later ToDos are marked with "###!!!"
"""

# %% Load packages

import numpy as np
import os
import spacy
from datetime import datetime as dt
nlp = spacy.load("de_core_news_lg")

# base folder
from helpers.folder_base import folder_base
folder_base: str = r"C:\Users\Bantel\Documents\GitHub-repos\parlspeech_GER"


# import costum helpers
from helpers.chunked_pickle_save_load import chunked_load_from_pickles
from helpers.ed8_patterns import *
from helpers.parties_patterns import *  # del afdnn, afdpn, b90nn, b90pn, cdunn, cdupn, csunn, csupn, fdpnn, fdppn, lnknn, lnkpn, spdnn, spdpn  # if needed b/c of old version
from helpers.face_validity_inspection import inspect_face_validity
from helpers.validation_helpers import token_from_spacy_match


# %% Load data

newest_subfolder: str = [f for f in os.listdir(folder_base + r'\data\2-preprocessing-out') if
                         f.endswith("bt_parlspeech")][-1]  # load data from newest _bt subfolder

bt_long = chunked_load_from_pickles(load_path_ext=newest_subfolder, limit=-1)  # load results from pickles in chunks; load all if limit < 0
# The full loading process took 2878.174 seconds (ca. 47 minutes).

del newest_subfolder
# bundestag_long_tmp.head(1000)

print(dt.now())

# %% Matcher emotions


matcher_emo = spacy.matcher.Matcher(nlp.vocab)  # instantiate Matcher

# add matcher patterns
matcher_emo.add(10, neg_emo)
matcher_emo.add(10, pos_emo_negated)

matcher_emo.add(20, pos_emo)
matcher_emo.add(20, neg_emo_negated)

emo_values: tuple = (10, 20)

column_mapper_emo: dict = {10: "neg_emo", 20: "pos_emo"}

# clean up
del negations
del ed8_dict
del anger, disgust, enthusiasm, fear, hope, joy, pride, sadness
del neg_anger, neg_disgust, neg_enthusiasm, neg_fear, neg_hope, neg_joy, neg_pride, neg_sadness
del neg_words, pos_words, neg_emo_negated, pos_emo_negated, pos_emo, neg_emo, only_neg_words, only_pos_words

# %% Apply matcher_emo

print(f"{dt.now()}: started matching emotion occurrences")
bt_long['matches_emo'] = bt_long['processed_sentence'].apply(matcher_emo)  # match patterns
# takes ca. 4min for non-discrete emotions
print(f"{dt.now()}: finished matching emotion occurrences")

# %% Manipulate emotion matches

bt_long = bt_long.join(bt_long['matches_emo'].apply(
    count_tup_first_values, args=(emo_values,)))  # aggregate emo matches: extract values & rejoin

# rename columns
bt_long = bt_long.rename(columns=column_mapper_emo)  # optional columns renaming

face_validation_emo: bool = False

if face_validation_emo:
    # save matched emo word
    bt_long['matchwords_emo'] =\
        bt_long.apply(lambda x: token_from_spacy_match(x['matches_emo'], x['processed_sentence']), axis=1)

del matcher_emo, column_mapper_emo, emo_values

# %% Save intermediary result

if face_validation_emo:
    filename: str = "bt_all_sents_with_matchwords_emo.csv"

    bt_long['matchwords_emo'] = \
        bt_long.apply(lambda x: token_from_spacy_match(x['matches_emo'], x['processed_sentence']), axis=1)

if not face_validation_emo:
    filename: str = "bt_all_sents_no_matchwords_emo.csv"


del bt_long['matches_emo'], bt_long['processed_sentence']

bt_long.to_csv(folder_base + "\data\\3-matching-out\\" + dt.now().strftime("%Y-%m-%d-%H%M") + "_" + filename)
