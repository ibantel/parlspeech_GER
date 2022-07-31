"""
    This file:
        - save large data frame in chunks as pickle files
        - load pickle files from folder and combine into data frame
"""

import datetime
import os
import pandas as pd
import pickle
import timeit

try:
    print(folder_base)
except NameError:
    folder_base: str = r"G:\My Drive\_ParlSpeech_sent_Markus_Ivo_GDrive\Data"
    print("folder_base assigned")

def chunked_save_as_pickles(df: pd.DataFrame, skip_n=-1, length_chunks: int=1000,
                            save_path: str= folder_base + r"\001-preprocessing-out\py-preprocessed",
                            filename_base: str="bt"):

    """ take in data frame that is divided into chunks of length length_chunks, which are saved as pickle files to
        the path YYYY_MM_DD_HH_MM_save_path_base as filename_base_i.pkl (i iterated over the number of chunks)
        skips the firs skip_n chunks
        returns None
    """

    # timing
    starttime = timeit.default_timer()

    # preparation folder operations
    save_path_full: str = save_path + "/" + datetime.datetime.now().strftime("%Y-%m-%d-%H%M") + "_" + filename_base  # create folder name
    save_path_full_abs: os.PathLike = os.path.abspath(save_path_full)


    if not os.path.isdir(save_path_full): # check if folder exists
        os.makedirs(save_path_full) # if not: create

    # preparation saving
    chunks: list = [df[i:i + length_chunks][:] for i in range(0, df.shape[0], length_chunks)] # create list of dfs

    # saving
    try:
        for i in range(len(chunks)): # save every chunk individually as pickle file (pkl)

            if skip_n != -1:  # if skip_n is manually set
                if i < skip_n: continue  # skip first skip_n chunks

            chunk: pd.DataFrame = chunks[i]

            file: str = save_path_full + "/" + filename_base.rstrip(".pkl") + "_" + str(i) + ".pkl"


            chunk.to_pickle(path=file)

    except FileNotFoundError:
        print("The path did not resolve. Please check.")

    print(f"The saving process took {timeit.default_timer() - starttime:.3f} seconds.")

    return None


def chunked_load_from_pickles(load_path_base: str= folder_base + r"\001-preprocessing-out\py-preprocessed",
                              load_path_ext: str=r"2021-11-15-1500_bt", limit: int=-1):
    """ loads the first [limit] pickle files contained in folder load_path (all files if limit < 0);
        combines them to one data frame, which is returned
        returns pd.DataFrame
    """

    load_path: str = load_path_base + "\\" + load_path_ext

    # timing
    starttime = timeit.default_timer()

    # preparation folder operations
    os.listdir(load_path)

    df: pd.DataFrame = pd.DataFrame() # instantiate empty dataframe

    if limit < 0:  # if limit is negative: load all files
        limit = len(os.listdir(load_path))
        print("Loading ALL files")
    else:
        print(f"Loading the first {limit} files.")


    for file in os.listdir(load_path)[:limit]:
        if file == 'desktop.ini':
            print(f"Skipping file {file}.")
            continue

        print(f"Loading file {file}.")
        with open(load_path + "/" + file, 'rb') as pickle_file:
            df_tmp = pickle.load(pickle_file)

        df = df.append(df_tmp)

    print(f"The loading process took {timeit.default_timer() - starttime:.3f} seconds.")

    return df

