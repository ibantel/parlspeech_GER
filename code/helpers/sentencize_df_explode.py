"""
    This file: sentencize & explode data set
"""

import pandas as pd
import nltk
import timeit


def sentencize_df_explode(df: pd.DataFrame, textcol_in: str, sentencecol_out: str):
    """ explode data set by sentencizing one column (textcol_in)
        takes in data frame (df) where df['textcol_in'] contains text
        returns data frame with a new column (df['sentencecol_out']) where each sentence in df['textcol_in'] is a row
    """
    starttime = timeit.default_timer()

    sentences_series: pd.Series = pd.Series(data=df[textcol_in].apply(nltk.tokenize.sent_tokenize).apply(pd.Series).reset_index().melt(
        id_vars="index").dropna()[['index', 'value']].set_index('index')['value'], name=sentencecol_out)
    # create sentencized series

    df: pd.DataFrame = pd.merge(df, sentences_series, left_index=True, right_index=True)

    df.reset_index(inplace=True) # reset index to unique indices

    if "index" in df.columns: # delete old index column
        df.drop(columns="index", inplace=True)


    print(f"The operation took {timeit.default_timer() - starttime:.3f} seconds.")

    del sentences_series, starttime

    return df


