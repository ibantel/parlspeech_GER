# Repository `parlspeech_GER`

The project contains an analysis of parliamentary speeches in Germany, from 2009 (17th German parliament) to 2021 (19th German parliament). The data is obtained from *[ParlSpeech](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/L4OAKN)*, and analysis is performed in `python`'s `spaCy` package.


The data is 
- prepared for analysis (`000-[...].R`),
- split into sentences which are transformed into `spaCy` objects 
(`001-[...].py`) and
- on which a lookup of negative emotive language is applied (`002-[...]).py`; based on Valentim & Widmann 2021)

```next steps```
- afterwards, the data is clustered into the ministry ressorts (policy areas) and negative language differentiated by policy area and origin party
- next, also look at open discourse data to do analyses based on speaker characteristics





## References
Valentim, Vicente & Widmann, Tobias (2021): Does Radical-Right Success Make the Political Debate More Negative? Evidence from Emotional Rhetoric in German State Parliaments. _Political Behavior_. https://doi.org/10.1007/s11109-021-09697-8
