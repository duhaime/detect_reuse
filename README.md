# Detecting (crosslingual) text reuse

This repo contains simple Python utilities for identifying crosslingual textual reuse. Quickstart:

<pre><code>git clone https://github.com/duhaime/detect_reuse 
cd detect_reuse 
cd text_cleaning_resources
gunzip normalized_stats_one_million.txt
cd ../
python combinatorial_ngrams.py sample/encyclopedie_volume05_translated.txt sample/goldsmith_animated_nature_full_unsplit.txt 8 4 4</code></pre>

This snippet looks for textual reuse between `sample/encyclopedie_volume05_translated.txt` and `sample/goldsmith_animated_nature_full_unsplit.txt`

### Translation Utility

`translate_texts/translate_text.py` uses goslate (`pip install goslate`) to translate all texts into a common language. Usage:

`python translate_text.py encyclopedie_volume05.txt "en" "utf-8"`

Where the arguments in order are: the text to be translated, the language into which the text should be translated, and the encoding of the input. 

Running the command above transforms Volume V of the French Encyclopédie into English:

```L'Encyclopédie vient de faire une excellente acquisition en la personne de M. Bourgelat , Ecuyer du Roi, chef de son Académie à Lyon ...``` becomes ```The Encyclopedia has made a great acquisition in the person of Mr. Bourgelat, Esquire of the King, the captain of his Academy in Lyons ...```

### Detecting Textual Reuse

One can search for textual reuse between two files by running:

`python combinatorial_ngrams.py {text_one} {text_two} {window size} {step size} {ngram size}`

Where:

`{window size}` indicates the size of the sliding window to be created
`{step size}` indicates the number of words to advance the sliding window when it moves, and 
`{ngram size}` indicates the number of words to include in each ngram.

The output will contain data in the following format:

`path_to_text_one {tab} path_to_text_two {tab} number_of_shared_ngrams {tab} sentence_from_text_one {tab} sentence_from_text_two {newline}`

Sorting by the third column can give an estimate of textual similarity between the passages, with more similar passages having higher values here. 
