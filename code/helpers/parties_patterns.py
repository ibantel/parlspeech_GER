"""
    This script: patterns for matches of party files for lookup
"""



# %% Load packages
import pandas as pd

# %% load data (MP names)

folder_MdBs: str = r"C:\Users\bantel\Dropbox\YY_Filesharing\ParlSpeech_sent_Markus_Ivo\Data\Bundestag\002a-party-dictionaries"

mdbs_df: pd.DataFrame = pd.read_csv(folder_MdBs + r"\bundestag_members_2009_2021.csv")

try:
    assert "Greens" in mdbs_df['party'].unique()
except AssertionError:
    print("The dataset most likely contains NAs for Green MPs. Check csv file and implementation in R (scraping).")

list_afd_mps: list = mdbs_df.loc[mdbs_df['party'] == "AfD", "name"].to_list()
list_fdp_mps: list = mdbs_df.loc[mdbs_df['party'] == "FDP", "name"].to_list()
list_b90_mps: list = mdbs_df.loc[mdbs_df['party'] == "Greens", "name"].to_list()
list_lnk_mps: list = mdbs_df.loc[mdbs_df['party'] == "Left", "name"].to_list()
list_spd_mps: list = mdbs_df.loc[mdbs_df['party'] == "SPD", "name"].to_list()
list_cxu_mps: list = mdbs_df.loc[mdbs_df['party'] == "Union", "name"].to_list()  # contains CDU and CSU

del mdbs_df, folder_MdBs

# %% generate patterns for MP names

def spacy_pattern_from_list(list_in):
    """
        Takes in a list of multi-word strings, returns a pattern to be passed to spacy matcher.
        The resulting pattern will match that exact string
        E.g.:
            list_in = ["Barack Hussein Obama", "George Walker Bush", "George Bush"]
                ==> [[{'LOWER': 'barack'}, {'LOWER': 'hussein'}, {'LOWER': 'obama'}],
                     [{'LOWER': 'george'}, {'LOWER': 'walker'}, {'LOWER': 'bush'}],
                     [{'LOWER': 'george'}, {'LOWER': 'bush'}]]

    :param list_in: list
    :return: list (conforming to spacy matcher pattern architecture)
    """

    list_out: list = []  # list to hold patterns

    for name in list_in:  # gives entire name (2-x tokens)
        pattern_name = []
        for word in name.split():  # gives individual tokens of name
            pattern_name.append({"LOWER": word.lower()})

        list_out.append(pattern_name)

    return list_out

# generate MP patterns
afd_mp_patterns: list = spacy_pattern_from_list(list_afd_mps)
fdp_mp_patterns: list = spacy_pattern_from_list(list_fdp_mps)
b90_mp_patterns: list = spacy_pattern_from_list(list_b90_mps)
lnk_mp_patterns: list = spacy_pattern_from_list(list_lnk_mps)
spd_mp_patterns: list = spacy_pattern_from_list(list_spd_mps)
cxu_mp_patterns: list = spacy_pattern_from_list(list_cxu_mps)

del list_afd_mps, list_fdp_mps, list_b90_mps, list_lnk_mps, list_spd_mps, list_cxu_mps

if False:  # for manual testing
    nlp = spacy.load("de_core_news_lg")
    matcher_pty = spacy.matcher.Matcher(nlp.vocab)  # instantiate Matcher
    matcher_pty.add("linke_mps", list_lnk_mp_patterns)  # testing new pattern
    matcher_pty.add("cdu", [[{"LOWER": "cdu"}]])  # testing known pattern
    doc = nlp("Jan van Aken hasst die CDU, weil sie zweifelhaftes Verständnis von Gerechtigkeit hat. Agnes Dietmar Alpers stimmt zu, aber Dietmar P. Bartsch widerspricht.")
    matches = matcher_pty(doc)
    for match_id, start, end in matches:
        string_id = nlp.vocab.strings[match_id]  # Get string representation
        span = doc[start:end]  # The matched span
        print(match_id, string_id, start, end, span.text)

    del matcher_pty, doc, matches, match_id, start, end, string_id, span


# %% generate patterns for party names

print("")
# patterns for words associated with each party

afd_words_patterns: list = [# afd (as proper noun)
                            [{'LOWER': {'IN': ['afd', 'afd.']}, 'POS': 'PROPN'}],
                            # afd-fraktion (literal matching)
                            [{'LOWER': 'afd'}, {'LOWER': '-', 'OP': '?'}, {'LOWER': {'IN': ['fraktion', 'fraktion.', 'bundestagsfraktion', 'bundestagsfraktion.']}}],
                            [{'LOWER': 'afd-fraktion'}],
                            # alternative für deutschland (literal matching)
                            [{'LOWER': 'alternative'}, {'LOWER': 'für'}, {'LOWER': 'deutschland'}],
                            # other afd words
                            [{'TEXT': {'REGEX': '^-?(AfD|Afd|afd|AFD)-?$'}}]  # followed or preceded by anything (and 0-1 dashes)
    ]

fdp_words_patterns: list = [# fdp (as proper noun)
                            [{'LOWER': {'IN': ['fdp', 'fdp.']}, 'POS': 'PROPN'}],
                            # fdp-fraktion (literal matching)
                            [{'LOWER': 'fdp'}, {'LOWER': '-', 'OP': '?'}, {'LOWER': {'IN': ['fraktion', 'fraktion.', 'bundestagsfraktion', 'bundestagsfraktion.']}}],
                            [{'LOWER': 'fdp-fraktion'}],
                            # freie demokratische partei (deutschland(s)) (literal matching)
                            [{'LOWER': 'freie'}, {'LOWER': 'demokratische'}, {'LOWER': 'partei'}, {'LOWER': {'IN': ['deutschland', 'deutschlands']}}],
                            # liberal*, Liberaldemokrat*, liberaldemokratisch*
                            [{'LEMMA':
                                  {'IN': ['liberal', 'Liberaler',  'Liberaldemokrat', 'Liberaldemokratin',
                                          'Liberaldemokraten', 'Liberaldemokratinnen',
                                          'liberaldemokratisch', 'liberaldemokratische', 'liberaldemokratischer',
                                          'liberaldemokratisches', 'liberaldemokratischen', 'liberaldemokratischem',
                                          ]}}],
                            # other fdp words
                            [{'TEXT': {'REGEX': '^-?(FDP|Fdp|fdp)-?$'}}],  # followed or preceded by anything (and 0-1 dashes)
                            [{'TEXT': {'REGEX': '^-?((G|g)el(b|be|ben|bes|ber))-?$'}}]  # followed or preceded by anything (and 0-1 dashes)
    ]

b90_words_patterns: list = [# bündnis 90 / die grünen (literal matching; variants)
                            [{'LOWER': 'bündnis'}, {'LOWER': '90'}, {'IS_PUNCT': True, 'OP': "?"}, {'LOWER': 'die'}, {'LEMMA': {'IN': ['Grüner', 'Grüne']}}],
                            # grünen-fraktion (literal matching)
                            [{'LOWER': {'IN': ['grüne', 'grünen']}}, {'LOWER': '-', 'OP': '?'}, {'LOWER': {'IN': ['fraktion', 'fraktion.', 'bundestagsfraktion', 'bundestagsfraktion.']}}],
                            [{'LOWER': {'IN': ['grüne-fraktion', 'grünen-fraktion']}}],
                            # bündnisgrüne (literal matching)
                            [{'LOWER': {'IN': ['bündnisgrün', 'bündnisgrüne', 'bündnisgrüner', 'bündnisgrünes', 'bündnisgrünen', 'bündnisgrünem']}}],
                            # grün* (Partei
                            [{'LEMMA': 'grün'}, {'LEMMA': 'Partei', 'OP': '?'}],
                            # other green words
                            [{'TEXT': {'REGEX': '^(G|g)rü(n|ne|ner|nes|nem|nen)-?$'}}, {'LEMMA': {'NOT_IN': ['Licht', 'Lichter', 'Start', 'Bohne', 'Bohnen', 'Curry']}}],  # grün followed by anything (and 0-1 dashes)
                            [{'TEXT': {'REGEX': '^-?(G|g)rü(n|ne|ner|nes|nem|nen)$'}}]  # grün preceded by anything (and 0-1 dashes); matches grün-rot, rot-grün
    ]

lnk_words_patterns: list = [[{'LOWER': {'IN': ['pds', 'linkspartei']}}], # PDS / linkspartei (literal matching; variants)
                            [{'POS': 'DET'}, {'LEMMA': {'IN': ['Linke', 'Linkspartei']}}],  # der / die Linke(n)/-spartei
                            [{'LOWER': 'linksfraktion'}],
                            [{'LEMMA': {'IN': ['linke', 'linken']}}, {'LOWER': 'bundestagsfraktion'}],
                            [{'ORTH': 'Linke'}],  # exact matching
                            # other left words
                            [{'TEXT': {'REGEX': '^-?(L|l)inks-?$'}}]  # followed or preceded by anything (and 0-1 dashes)
                            ]

spd_words_patterns: list = [# spd (as proper noun)
                            [{'LOWER': {'IN': ['spd', 'spd.']}, 'POS': 'PROPN'}],
                            # spd-fraktion (literal matching)
                            [{'LOWER': 'spd'}, {'LOWER': '-', 'OP': '?'}, {'LOWER': {'IN': ['fraktion', 'fraktion.', 'bundestagsfraktion', 'bundestagsfraktion.']}}],
                            [{'LOWER': {'IN': ['spd-fraktion', 'spd-fraktion.', 'spdfraktion']}}],
                            # sozialdemokratische partei (deutschland(s)) (literal matching)
                            [{'LOWER': 'sozialdemokratische'}, {'LOWER': 'partei'}, {'LOWER': {'IN': ['deutschland', 'deutschlands']}, 'OP': '?'}],
                            # Sozialdemokrat*, sozialdemokratisch*
                            [{'LEMMA':
                                  {'IN': ['Sozialdemokrat',       'Sozialdemokratin', # includes Plural
                                          'sozialdemokratisch',   'sozialdemokratische'  # incl -es, -er, -en, -em
                                          ]}}],
                            # other spd words
                            [{'TEXT': {'REGEX': '^-?(SPD|spd|Spd)-?$'}}],  # SPD followed by anything (and 0-1 dashes)
                            [{'TEXT': {'REGEX': '^-?(R|r)o(t|te|ten|tes|ter|tem)-?$'}}, {'LEMMA': {'NOT_IN': ['Faden', 'Fäden']}}]  # rot in all its forms, not followed by Faden; matches schwarz-rot
                            ]

cxu_words_patterns: list = [# cdu (as proper noun)
                            [{'LOWER': {'IN': ['cdu', 'cdu.', 'csu', 'csu.', 'cdu-', 'cdu/csu']}, 'POS': 'PROPN'}],
                            # cxu-fraktion (literal matching)
                            [{'LOWER': {'IN': ['cdu', 'csu', 'cdu/csu']}}, {'LOWER': '-', 'OP': '?'}, {'LOWER': {'IN': ['fraktion', 'fraktion.', 'bundestagsfraktion']}, 'OP': '?'}],
                            [{'LOWER': {'IN': ['cdu-fraktion', 'csu-fraktion', 'cdu-fraktion.', 'csu-fraktion.', 'unions-fraktion', 'cdu/csu-bundestagsfraktion', 'cdu/csu-bundestagsfraktion.', 'cdu/csufraktion']}}],
                            [{'LOWER': 'cdu'}, {'IS_PUNCT': True}, {'LOWER': 'csu'}, {'LOWER': '-', 'OP': '?'}, {'LOWER': {'IN': ['fraktion', 'fraktion.']}}],
                            [{'LOWER': {'IN': ['cdu/csu-fraktion',  'cdu/ csu-fraktion',  'cdu / csu-fraktion',
                                               'cdu/csu-fraktion.', 'cdu/ csu-fraktion.', 'cdu / csu-fraktion.']}}],
                            # christdemokratische partei (deutschland(s)) (literal matching)
                            [{'LOWER': {'IN': ['christdemokratische', 'christdemokratischer', 'christdemokratischen']}}, {'LOWER': 'partei'}, {'LOWER': {'IN': ['deutschland', 'deutschlands']}, 'OP': '?'}],
                            # Christ(demokrat*|sozial*), christdemokratisch*
                            [{'LEMMA':
                                  {'IN': ['christdemokratisch',  'christdemokratische',  'christdemokratischer',
                                          'christdemokratisches', 'christdemokratischen', 'christdemokratischem',
                                          'christsozial', 'christsoziale', 'christsozialer',
                                          'christsoziales', 'christsozialen', 'christsozialem',
                                          'Christdemokrat', 'Christdemokratin',  # does not include Plural
                                          'Christdemokraten', 'Christdemokratinnen',
                                          'Christsozialer', 'Christsoziale',  # incl Plural because of forms, not lemma
                                          ]}}],
                            [{'LEMMA': {'IN': ['christlich', 'christliche']}}, {'LEMMA': {'IN': ['demokratisch', 'demokratische', 'sozial', 'soziale']}}, {'LOWER': 'union'}],
                            [{'LEMMA': {'NOT_IN': ['europäisch', 'Europäische', 'Europäischer']}}, {'LOWER': 'union'}],
                            # other cxu words
                            [{'TEXT': {'REGEX': '^-?((S|s)chwar(z|ze|zen|zes|zer))-?$'}},
                             {'LEMMA': {'NOT_IN': ['Schaf', 'Schafe', 'Loch', 'Löcher', 'Humor', 'Meer']}}],  # followed or preceded by anything (and 0-1 dashes)
                            [{'TEXT': {'REGEX': '^-?(CDU|Cdu|cdu|CSU|Csu|csu)-?$'}}]  # followed or preceded by anything (and 0-1 dashes)
                             ]


if False:  # for manual testing
    nlp = spacy.load("de_core_news_lg")
    matcher_pty = spacy.matcher.Matcher(nlp.vocab)  # instantiate Matcher
    matcher_pty.add("xxx_pty", cxu_words_patterns)  # testing new pattern

    # patterns for testing
    doc = nlp("die alternative für deutschland ist klein. die afd-fraktion bestreitet das. die afd ist im bundestag") # Test AfD
    doc = nlp("Die FDP ist in der FDP-Fraktion. Viel liberales ist liberaldemokratischer, Liberale oder Liberaldemokraten.")  # Test FDP
    doc = nlp("Bündnis 90/ Die Grünen sind die Grünen-Fraktion, grüne Fraktion, die Bündnisgrünen und der grünen Partei.")  # Test Greens
    doc = nlp("Die Linken und die Linkspartei finden soziale Gerechtigkeit wichtig.")  # Test Left
    doc = nlp("Die SPD (SPD Fraktion) und die Sozialdemokratische Partei Deutschlands denken sozialdemokratisch, "
              "sozialdemokratische,  sozialdemokratischer, sozialdemokratisches, sozialdemokratischen, "
              "sozialdemokratischem sozialdemokratisches und bezeichnen sich als Sozialdemokraten SPD-grün oder grün-SPD.")  # Test SPD
    doc = nlp("Die CDU und die CSU (CDU-Fraktion bzw. CSU-Fraktion oder CDU / CSU-Fraktion oder CDU/CSU Fraktion) und die "
              "christlicher demokratischen union "
              "Europäischen Union "  # should not match
              #"Christlich Demokratische Union bzw. Christlich Soziale Union denken christdemokratisch, christlich "
              #"demokratisch, christdemokratische,  christdemokratischer, christdemokratisches, christdemokratischen, "
              #"christdemokratischem christdemokratisches und bezeichnen sich als Christdemokratinnen und "
              "Christdemokraten.")  # Test CDU
    doc = nlp("Das heißt, Sie korrigieren den Unsinn, den Ministerpräsidenten aus CDU- und FDP-geführten Ländern im Bundesrat durchgesetzt haben."
              "Die CDU/CSU-Bundestagsfraktion unterstützt nachdrücklich die Vision des amerikanischen Präsidenten Obama, Schritt für Schritt eine Welt frei von Atomwaffen zu schaffen."
              "Für die Russland-Politik der CDU/CSU-FDP-Koalition gilt, dass wir eine enge, aufgeschlossene und in Umgang und Ansprache ehrliche Partnerschaft wollen."
              "Die CDU/CSUFraktion wird sich Deutschlands Verantwortung für die Welt im Interesse unseres Landes engagiert stellen."
              "– Ich war in der Sommerpause beim Oberbürgermeister von Stralsund, einem CDUMann, gut mit Frau Merkel bekannt."
              "Bisher bin ich davon ausgegangen: Wir müssen Ihre Justizministerin vor den Kollegen der CDU/CSU schützen.")  # Test CDU 2

    for tok in doc: print(tok.text, tok.lemma_, tok.pos_)
    matches = matcher_pty(doc)
    for match_id, start, end in matches:
        string_id = nlp.vocab.strings[match_id]  # Get string representation
        span = doc[start:end]  # The matched span
        print(match_id, string_id, start, end, span.text)

    del tok, match_id, start, end, doc, matches, string_id, word, span


# %% Testing (if __name__ == "__main__()")
if __name__ == "__main__()":
    print("Testing matcher")

# %% Setup
    import spacy

    nlp = spacy.load("de_core_news_lg")

    matcher_pty = spacy.matcher.Matcher(nlp.vocab)  # instantiate Matcher

    # add matcher patterns
    matcher_pty.add(1010, list_afd_mp_patterns)
    matcher_pty.add(1011, afd_words_patterns)
    matcher_pty.add(1020, list_fdp_mp_patterns)
    matcher_pty.add(1021, fdp_words_patterns)
    matcher_pty.add(1030, list_b90_mp_patterns)
    matcher_pty.add(1031, b90_words_patterns)
    matcher_pty.add(1040, list_lnk_mp_patterns)
    matcher_pty.add(1041, lnk_words_patterns)
    matcher_pty.add(1050, list_spd_mp_patterns)
    matcher_pty.add(1051, spd_words_patterns)
    matcher_pty.add(1060, list_cxu_mp_patterns)
    matcher_pty.add(1061, cxu_words_patterns)

    # clean up
    del list_afd_mp_patterns, list_fdp_mp_patterns, list_b90_mp_patterns, list_lnk_mp_patterns, list_spd_mp_patterns, \
        list_cxu_mp_patterns
    del afd_words_patterns, fdp_words_patterns, b90_words_patterns, lnk_words_patterns, spd_words_patterns, \
        cxu_words_patterns, matcher_pty, nlp




# %% Testing patterns

    df_tmp: pd.DataFrame = \
        pd.DataFrame(columns=['date', 'ground_emo', 'ground_emoword', 'ground_targ', 'sentence'],
                     data=[["2009-09-01", "anger", 'wutschäumend', "SPD", "Wutschäumend ist die SPD"],
                           ["2009-09-01", "fear", 'zweifelhaftes', "CDU",
                            "Die CDU hat ein zweifelhaftes Verständnig von Gerechtigkeit."],
                           ["2009-09-01", "disgust", 'unsittlicheres', "AfD", "Es gibt nichts unsittlich als die AfD."],
                           ["2009-09-01", "sadness", 'unsolidarisch', "FDP",
                            "Niemand ist so unsolidarisch wie die FDP."],
                           ["2009-09-01", "joy", 'zauberhafte', "LEFT", "Die zauberhafte Linkspartei."],
                           ["2009-09-01", "enthusiasm", 'vorbehaltslos', "GREENS",
                            "Ich unterstütze vorbehaltslos was die Grünen vorschlagen."],
                           ["2009-09-01", "pride", 'wertvoll', "SPD", "Das ist wertvoll was die SPD tut."],
                           ["2009-09-01", "hope", 'vorsorgt', "FDP",
                            "Das kann nur tun, wer so gut vorsorgt wie die FDP."]])

    df_tmp['processed_sentence'] = [doc for doc in
                                    nlp.pipe(df_tmp['sentence'].tolist())]  # faster than apply
    df_tmp['matches_pty'] = df_tmp['processed_sentence'].apply(matcher_pty)  # match patterns

    print("result of matching:")
    print(df_tmp)

# %% Testing patterns (2)

    cdu = nlp("Die CDU hat ein zweifelhaftes Verständnig von Gerechtigkeit.")
    for tok in cdu: print(tok.text, tok.pos_) # PROPN

    spd = nlp("Wutschäumend ist die SPD")
    for tok in spd: print(tok.text, tok.pos_)  # PROPN

    afd = nlp("Es gibt nichts unsittlich als die AfD.")
    for tok in afd: print(tok.text, tok.pos_)  # PROPN

    fdp = nlp("Niemand ist so unsolidarisch wie die FDP.")
    for tok in fdp: print(tok.text, tok.pos_)  # PROPN

    lnk = nlp("Die zauberhafte Linkspartei.")
    b90 = nlp("Ich unterstütze vorbehaltslos was die Grünen vorschlagen.")
    for tok in b90: print(tok.text, tok.pos_)  # NOUN

    spd = nlp("Das ist wertvoll was die SPD tut.")
    for tok in spd: print(tok.text, tok.pos_)  # PROPN

    fdp = nlp("Das kann nur tun, wer so gut vorsorgt wie die FDP.")
    for tok in fdp: print(tok.text, tok.pos_)  # PROPN



# %% Cleaning up

    del afd, b90, cdu, fdp, lnk, spd, df_tmp, tok, nlp
