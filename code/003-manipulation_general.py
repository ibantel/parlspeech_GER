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


# %% Code out

# analyse agenda points to different topics
