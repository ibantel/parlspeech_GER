"""
    This script: load ed8 dictionary and provide positive and negative patterns for lookup
"""

# %% Loading Packages
import ast
import bios
from collections import Counter
import functools
import numpy as np
import operator

if __name__ != "__main__":
    import pandas as pd
    # print("pandas imported as pd")

try:
    print(folder_base)
except NameError:
    folder_base: str = r"C:\Users\Bantel\Documents\GitHub-repos\parlspeech_GER"
    print("folder_base assigned")


# %% Load Data
ed8_dict = bios.read(folder_base + r'\data\0-ed8_emotion_dictionary_Widman\ed8.yml')['ed8']  # load dictionary

# %% helper function
def reduce_to_set(nested_list_in: list):
    """
    takes in irregular nested list; returns list of unique values in this list

    :param nested_list_in: nested list
    :return: list
    """

    list_all: list = functools.reduce(operator.iconcat, [ls for ls in nested_list_in], [])  # flatten list
    list_unique: list = list(set(list_all))

    return sorted(list_unique)

# %% Prepare Matcher patterns
negations = ["nicht", "nichts", "kein", "keine", "keinen", "keinem", "keiner", "keines", "ohne"] # negation words

# unique XXX words
#[w for w in ed8_dict['SADNESS'] if (not w in ed8_dict['ANGER']) and
#                                 (not w in ed8_dict['FEAR']) and
#                                 (not w in ed8_dict['DISGUST'])]
#
#[w for w in ed8_dict['HOPE'] if (not w in ed8_dict['JOY']) and
#                                 (not w in ed8_dict['ENTHUSIASM']) and
#                                 (not w in ed8_dict['PRIDE'])]
#

print("")

# . ## discrete emotions
print("")

# patterns for negated words associated with each emotion
neg_anger       = [[{"LOWER": {"IN": negations}}, {"LOWER": {"IN": ed8_dict['ANGER']}}]]
neg_fear        = [[{"LOWER": {"IN": negations}}, {"LOWER": {"IN": ed8_dict['FEAR']}}]]
neg_disgust     = [[{"LOWER": {"IN": negations}}, {"LOWER": {"IN": ed8_dict['DISGUST']}}]]
neg_sadness     = [[{"LOWER": {"IN": negations}}, {"LOWER": {"IN": ed8_dict['SADNESS']}}]]
neg_joy         = [[{"LOWER": {"IN": negations}}, {"LOWER": {"IN": ed8_dict['JOY']}}]]
neg_enthusiasm  = [[{"LOWER": {"IN": negations}}, {"LOWER": {"IN": ed8_dict['ENTHUSIASM']}}]]
neg_pride       = [[{"LOWER": {"IN": negations}}, {"LOWER": {"IN": ed8_dict['PRIDE']}}]]
neg_hope        = [[{"LOWER": {"IN": negations}}, {"LOWER": {"IN": ed8_dict['HOPE']}}]]

# patterns for non-negated words associated with each emotion
anger       = [[{"IS_SENT_START": True, "LOWER": {"IN": ed8_dict['ANGER']}}],      [{"LOWER": {"NOT_IN": negations}}, {"LOWER": {"IN": ed8_dict['ANGER']}}]]
fear        = [[{"IS_SENT_START": True, "LOWER": {"IN": ed8_dict['FEAR']}}],       [{"LOWER": {"NOT_IN": negations}}, {"LOWER": {"IN": ed8_dict['FEAR']}}]]
disgust     = [[{"IS_SENT_START": True, "LOWER": {"IN": ed8_dict['DISGUST']}}],    [{"LOWER": {"NOT_IN": negations}}, {"LOWER": {"IN": ed8_dict['DISGUST']}}]]
sadness     = [[{"IS_SENT_START": True, "LOWER": {"IN": ed8_dict['SADNESS']}}],    [{"LOWER": {"NOT_IN": negations}}, {"LOWER": {"IN": ed8_dict['SADNESS']}}]]
joy         = [[{"IS_SENT_START": True, "LOWER": {"IN": ed8_dict['JOY']}}],        [{"LOWER": {"NOT_IN": negations}}, {"LOWER": {"IN": ed8_dict['JOY']}}]]
enthusiasm  = [[{"IS_SENT_START": True, "LOWER": {"IN": ed8_dict['ENTHUSIASM']}}], [{"LOWER": {"NOT_IN": negations}}, {"LOWER": {"IN": ed8_dict['ENTHUSIASM']}}]]
pride       = [[{"IS_SENT_START": True, "LOWER": {"IN": ed8_dict['PRIDE']}}],      [{"LOWER": {"NOT_IN": negations}}, {"LOWER": {"IN": ed8_dict['PRIDE']}}]]
hope        = [[{"IS_SENT_START": True, "LOWER": {"IN": ed8_dict['HOPE']}}],       [{"LOWER": {"NOT_IN": negations}}, {"LOWER": {"IN": ed8_dict['HOPE']}}]]


# . ## collapsed into positive and negative emotions
print("")

# patterns for emotions and negated emotions, collapsed into positive and negative emotions
neg_words = reduce_to_set([ed8_dict['ANGER'], ed8_dict['FEAR'], ed8_dict['DISGUST'], ed8_dict['SADNESS']])
pos_words = reduce_to_set([ed8_dict['JOY'], ed8_dict['ENTHUSIASM'], ed8_dict['PRIDE'], ed8_dict['HOPE']])

only_neg_words = [tok for tok in neg_words if tok not in pos_words]  # drop words associated with both pos & neg emotion
only_pos_words = [tok for tok in pos_words if tok not in neg_words]  # drop words associated with both pos & neg emotion

pos_emo         = [[{"IS_SENT_START": True, "LOWER": {"IN": only_pos_words}}], [{"LOWER": {"NOT_IN": negations}}, {"LOWER": {"IN": only_pos_words}}]]
neg_emo         = [[{"IS_SENT_START": True, "LOWER": {"IN": only_neg_words}}], [{"LOWER": {"NOT_IN": negations}}, {"LOWER": {"IN": only_neg_words}}]]
neg_emo_negated = [[{"LOWER": {"IN": negations}}, {"LOWER": {"IN": only_neg_words}}]]
pos_emo_negated = [[{"LOWER": {"IN": negations}}, {"LOWER": {"IN": only_pos_words}}]]

#%% Define function for aggregation of patterns


def count_tup_first_values(lst, values):
    """ Takes in list of tuples. Returns count of occurences of different values at position 0 of the tuples
        Example:
            lst: list = [(101, 0, 2), (102, 4, 6), (101, 8, 10)]
            values: [101, 102, 103]
            return: pd.Series(index=[0,1], data={0: 2, 1: 1})

    :param lst: list of tuples
    :param values: list of values to be aggregated
    :return: pd.Series

    """

    counts = Counter({n: 0 for n in values})  # initialize the counts to zero for every element of values

    if len(lst) == 0:
        return pd.Series(counts)  # if value is NaN: return zero counts

    # lst = ast.literal_eval(lst_str)  # convert string to list if input is

    counts.update(x for x, *_ in lst if x in values)  # update counts based on 1st element of each tuple

    return pd.Series(counts) # return series of counts


#%% Testing

if False:

# %% setup
    print("Testing matcher")
    import pandas as pd
    import spacy

    nlp = spacy.load("de_core_news_lg")

    matcher_emo = spacy.matcher.Matcher(nlp.vocab)  # instantiate Matcher

    # add matcher patterns
    matcher_emo.add(101, neg_anger)
    matcher_emo.add(102, neg_fear)
    matcher_emo.add(103, neg_disgust)
    matcher_emo.add(104, neg_sadness)
    matcher_emo.add(105, neg_joy)
    matcher_emo.add(106, neg_enthusiasm)
    matcher_emo.add(107, neg_pride)
    matcher_emo.add(108, neg_hope)
    matcher_emo.add(201, anger)
    matcher_emo.add(202, fear)
    matcher_emo.add(203, disgust)
    matcher_emo.add(204, sadness)
    matcher_emo.add(205, joy)
    matcher_emo.add(206, enthusiasm)
    matcher_emo.add(207, pride)
    matcher_emo.add(208, hope)

    # clean up
    del negations
    del ed8_dict
    del anger, disgust, enthusiasm, fear, hope, joy, pride, sadness
    del neg_anger, neg_disgust, neg_enthusiasm, neg_fear, neg_hope, neg_joy, neg_pride, neg_sadness

    df_tmp: pd.DataFrame = \
        pd.DataFrame(columns=['date', 'ground_emo', 'ground_emoword', 'ground_targ', 'sentence'],
                     data=[["2009-09-01", "anger", 'wutschäumend', "SPD", "Wutschäumend ist die SPD"],
                           ["2009-09-01", "fear", 'zweifelhaftes', "CDU",
                            "Die CDU hat ein zweifelhaftes Verständnig von Gerechtigkeit."],
                           ["2009-09-01", "disgust", 'unsittlicheres', "AfD", "Es gibt nichts unsittlicheres als die AfD."],
                           ["2009-09-01", "sadness", 'unsolidarisch', "FDP",
                            "Niemand ist so unsolidarisch wie die FDP."],
                           ["2009-09-01", "joy", 'zauberhafte', "LEFT", "Die zauberhafte Linkspartei."],
                           ["2009-09-01", "enthusiasm", 'vorbehaltslos', "GREENS",
                            "Ich unterstütze vorbehaltslos was die Grünen vorschlagen."],
                           ["2009-09-01", "pride", 'wertvoll', "SPD", "Das ist wertvoll was die SPD tut."],
                           ["2009-09-01", "hope", 'vorsorgt', "FDP",
                            "Das kann nur tun, wer so gut vorsorgt wie die FDP."]])



#%% Testing: matching

    df_tmp['processed_sentence'] = [doc for doc in
                                    nlp.pipe(df_tmp['sentence'].tolist())]  # faster than apply
    df_tmp['matches_emo'] = df_tmp['processed_sentence'].apply(matcher_emo)  # match patterns

    print("result of matching:")
    print(df_tmp)

    type(df_tmp.at[1, 'matches_emo'])


#%% Testing: aggregating
    print("aggregating")

    # df_tmp['matches_emo'] = df_tmp['matches_emo'].astype("string")  # convert to str ## NOT NEEDED ANYMORE

    # extract values & rejoin
    df_tmp = df_tmp.join(
        df_tmp['matches_emo'].apply(
            count_tup_first_values, args=((101, 102, 103, 104, 105, 106, 107, 108, 201, 202, 203, 204, 205, 206, 207, 208), )
    ))

    # rename columns
    df_tmp = df_tmp.rename(columns={101: "neg_anger", 102: "neg_fear", 103: "neg_disgust", 104: "neg_sadness",
                           105: "neg_joy", 106: "neg_enthusiasm", 107: "neg_pride", 108: "neg_hope",
                           201: "anger", 202: "fear", 203: "disgust", 204: "sadness",
                           205: "joy", 206: "enthusiasm", 207: "pride", 208: "hope"})  # optional columns renaming

    del df_tmp, matcher_emo

