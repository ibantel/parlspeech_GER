"""
    This script: get some sentences for inspection of face validity

    Later ToDos are marked with "###!!!"
"""

# %% Load packages
import pandas as pd


# %% Define inspection function
def inspect_face_validity(df: pd.DataFrame, party_emo_party: dict,
                          sentences_per_keyvalue: int = 10,
                          date_col: str = "date", origin_pty_col: str = "origin_pty",
                          emotion_col: str = "emotion", emotion_match_col: str = "emotion_match",
                          target_pty_col: str = "target_pty", target_pty_match_col: str = "target_pty_match",
                          sentenct_col: str="sentence"):
    """
        takes in pd.DataFrame
         searches for each entry of an origin party, emotion, and target party in party_emo_party,
         returns (max.) senteces_per_keyvalue numbers of sentences from textcolumn
        returns data frame containing the col_val entries and the text

        :param df: pd.DataFrame
        :param party_emo_party: dict containing needed keys: orig_pty, emo, targ_pty and the search terms as values
        :param xxx_col: str: name of column of interest in df
        :param sentences_per_keyvalue: int
        :return: pd.DataFrame
    """

    try:
        assert ('orig_pty' in party_emo_party.keys()) and \
               ('emo' in party_emo_party.keys()) and \
               ('targ_pty' in party_emo_party.keys())
    except AssertionError:
        print("party_emo_party must contain the keys 'orig_pty', 'emo', and 'targ_pty';",
              "at least three column names are needed.")

        return -1

    _: pd.DataFrame = df.loc[((df[origin_pty_col] == party_emo_party['orig_pty']) &
                              (df[emotion_col] == party_emo_party['emo']) &
                              (df[target_pty_col] == party_emo_party['targ_pty'])), :]


    if _.shape[0] < sentences_per_keyvalue:
        print(f"Less sentences found for {party_emo_party['orig_pty']}'s {party_emo_party['emo']} towards {party_emo_party['targ_pty']} than requested. Returning all detected sentences.")

    else:
        _ = _.sample(n=sentences_per_keyvalue, random_state=3141)

    return _[[origin_pty_col, emotion_col, target_pty_col,
              date_col, sentenct_col, emotion_match_col, target_pty_match_col]]
