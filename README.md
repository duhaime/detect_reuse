# crosslingual_text_reuse

This repo contains simple Python utilities for identifying crosslingual textual reuse. To prepare texts for analysis, the `translate_texts/translate_text.py` script uses goslate (`pip install goslate`) to translate all texts into a common language. That script can be called like this:

`python translate_text.py encyclopedie_volume05.txt "en" "utf-8"`

Where the arguments in order are: the text to be translated, the language into which the text should be translated, and the encoding of the input. 

Running the sample command above transforms Volume V of the French Encyclopédie into English:

```L'Encyclopédie vient de faire une excellente acquisition en la personne de M. Bourgelat , Ecuyer du Roi, chef de son Académie à Lyon, &amp; Correspondant de l'Académie
royale des Sciences de Paris. Il veut bien nous donner, à commencer à la lettre E , tous
les articles qui concernent le Manége , la Maréchallerie , &amp; les Arts relatifs. Ce Volume
en renferme déjà un nombre considérable. Les connoissances profondes de M. Bourgelat,
dans la matiere dont il s'agit, nous répondent du soin avec lequel ces articles ont été
faits; ils sont marqués d'un ( e ).```

Becomes:

```The Encyclopedia has made a great acquisition in the person of Mr. Bourgelat, Esquire of the King, the captain of his Academy in Lyons, & amp; Correspondent of the Royal Academy of Sciences in Paris. He wants to give us, starting with the letter E, all items that affect the Manege, the Maréchallerie, & amp; the relative Arts. This issue already contains a considerable number. The deep acquaintances of Mr. Bourgelat in the matter in question, we meet the care with which these items were made; they are marked with (e).```

Once all texts are represented in a common language, the next step is to simply unzip the normalized word frequency file in this repo:

`gunzip text_cleaning_resources/normalized_stats_one_million.txt.gz`

One can search for textual reuse between two files by running:

`python combinatorial_ngrams.py {text_one} {text_two} {window size} {step size} {ngram size}`

Where:

`{window size}` indicates the size of the sliding window to be created
`{step size}` indicates the number of words to advance the sliding window when it moves, and 
`{ngram size}` indicates the number of words to include in each ngram.

The output will contain data in the following format:

`path_to_text_one {tab} path_to_text_two {tab} number_of_shared_ngrams {tab} sentence_from_text_one {tab} sentence_from_text_two {newline}`

Sorting by the third column can give a rough estimate of textual similarity between the passages, with more similar passages having higher values here. 

As an example, running:

`python combinatorial_ngrams_departure.py sample/encyclopedie_volume05_translated.txt sample/goldsmith_animated_nature_full_unsplit.txt 8 4 4` 

completes in under a minute, and the first line of output looks like this:

```sample/encyclopedie_volume05_translated.txt	sample/goldsmith_animated_nature_full_unsplit.txt	19	The borders are poorly guarded & amp; poorly fortified; the troops of the Empire are few & amp; poorly paid; there is no public money, because nobody wants to contribute.	The frontiers are all ill guarded and ill fortified; the troops of the empire are but few in number, and ill paid; nor are there any public funds to supply these defects, as none are willing to contribute to them.```

I included source code for additional string similarity metrics in the `similarity_metrics` directory, but will leave those undocumented.
