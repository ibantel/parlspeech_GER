# %% Setup
import pandas as pd
import spacy
nlp = spacy.load("de_core_news_lg")



def token_from_spacy_match(match_tuples, spacy_sentence):
    """ Takes in a list of tuples, each with three elements: match_id ("what is matched?"), match_start, and match_end
        Also takes in a processed sentence (spaCy doc)
        Returns matched words (text representation)

        :match_tuples: list of tuples (each length 3)
        :spacy_sentence: spacy object
        :return: list of strings
    """

    return_object: list = []  # list to hold all words of matches

    for tup in match_tuples:  # iterate through tuples in match_tuples

        # ensure tuple has three elements
        try:
            assert len(tup) == 3
        except AssertionError:
            # print("Tuple input length unexpectedly does not equal 3.")
            continue

        # unpack tuple
        try:
            match_span = spacy_sentence[tup[1]:tup[2]]
            return_object.append(match_span.text)

        except AttributeError:
            print(f"spacy_sentence should be <class 'spacy.tokens.doc.Doc'>.\nIs {type(spacy_sentence)}")
            continue

        except TypeError:
            print(f"spacy_sentence should be <class 'spacy.tokens.doc.Doc'>.\nIs {type(spacy_sentence)}")
            continue

    return return_object


if False:

    # with single sentence
    sent = 'Dies ist ein generischer Satz mit einem bestimmten Wort und anderen Worten.'
    processed_sentence = nlp(sent)
    matcher = spacy.matcher.Matcher(nlp.vocab)
    pttrn: list = [[{'LOWER': "wort"}], [{'LOWER': "worten"}]]
    matcher.add(1021, pttrn) # add matcher pattern

    matches = matcher(processed_sentence)  # match patterns

    for match_id, start_match, end_match in matches:
        match_span = processed_sentence[start_match:end_match]
        print(match_span.text)

    # test function
    token_from_spacy_match(match_tuples=matches, spacy_sentence=processed_sentence)


    # reproduce analysis with dataframe
    df: pd.DataFrame = pd.DataFrame({'num': [1, 2],
                                     'sentence': ['Dies ist ein generischer Satz mit einem bestimmten Wort und anderen Worten.',
                                                  'Hier nur ein bestimmtes Wort.']})
    df['processed_sentence'] = [doc for doc in nlp.pipe(df['sentence'].tolist())]  # faster than apply
    df['matches'] = df['processed_sentence'].apply(matcher)  # match patterns
    df['matchwords'] = df.apply(lambda x: token_from_spacy_match(x['matches'], x['processed_sentence']), axis=1)

