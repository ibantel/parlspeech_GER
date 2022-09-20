# Repository `parlspeech_GER`

The project contains an analysis of parliamentary speeches in Germany, from 2009 (17th German parliament) to 2021 (19th German parliament). 
Data is obtained from *[ParlSpeech](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/L4OAKN)* (Rauh & Schwalbach 2020), and analysis is performed in `python`'s `spaCy` package.


The data is 
- prepared for analysis (`000-[...].R`),
- split into sentences which are transformed into `spaCy` objects 
(`001-[...].py`) and
- on which a lookup of negative emotive language is applied (`002-[...]).py`; based on Valentim & Widmann 2021)
- the results are presented in a shiny app (https://ivo-bantel.shinyapps.io/parlspeech_GER)
<!-- 
`next steps`
- afterwards, the data is clustered into the ministry ressorts (policy areas) and negative language differentiated by policy area and origin party
- next, also look at open discourse data to do analyses based on speaker characteristics
-->
<br><br><br><br>


## References
Rauh, Christian & Schwalbach, Jan (2020): The ParlSpeech V2 data set: Full-text corpora of 6.3 million parliamentary speeches in the key legislative chambers of nine representative democracies, _Dataverse_. https://doi.org/10.7910/DVN/L4OAKN.

Valentim, Vicente & Widmann, Tobias (2021): Does Radical-Right Success Make the Political Debate More Negative? Evidence from Emotional Rhetoric in German State Parliaments. _Political Behavior_. https://doi.org/10.1007/s11109-021-09697-8.
