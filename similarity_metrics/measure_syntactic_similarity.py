#!/usr/bin/python
# -*- coding: utf-8 -*-

'''NLTK 3.0 offers map_tag, which maps the Penn Treebank Tag Set to the Universal Tagset, a course tag set with the following 12 tags:

VERB - verbs (all tenses and modes)
NOUN - nouns (common and proper)
PRON - pronouns
ADJ - adjectives
ADV - adverbs
ADP - adpositions (prepositions and postpositions)
CONJ - conjunctions
DET - determiners
NUM - cardinal numbers
PRT - particles or other function words
X - other: foreign words, typos, abbreviations
. - punctuation

We'll map Stanford's tag set to this tag set then compare the similarity between subregions of French and English sentences.'''

from __future__ import division
from nltk.tag.stanford import POSTagger
from nltk.tokenize import word_tokenize
from collections import Counter
from nltk.tag import map_tag
import os, math, codecs, winsound

#########################
# Create Tagset Mapping #
#########################

def create_french_to_universal_dict():
	'''this function creates the dict we'll call below when we map french pos tags to the universal tag set'''
	french_to_universal = {}
	french_to_universal[u"ADJ"]    = u"ADJ"
	french_to_universal[u"ADJWH"]  = u"ADJ"
	french_to_universal[u"ADV"]    = u"ADV"
	french_to_universal[u"ADVWH"]  = u"ADV"
	french_to_universal[u"CC"]     = u"CONJ"    
	french_to_universal[u"CLO"]    = u"PRON"
	french_to_universal[u"CLR"]    = u"PRON"
	french_to_universal[u"CLS"]    = u"PRON"
	french_to_universal[u"CS"]     = u"CONJ"
	french_to_universal[u"DET"]    = u"DET"
	french_to_universal[u"DETWH"]  = u"DET"
	french_to_universal[u"ET"]     = u"X"
	french_to_universal[u"NC"]     = u"NOUN"
	french_to_universal[u"NPP"]    = u"NOUN"
	french_to_universal[u"P"]      = u"ADP"
	french_to_universal[u"PUNC"]   = u"."
	french_to_universal[u"PRO"]    = u"PRON"
	french_to_universal[u"PROREL"] = u"PRON"
	french_to_universal[u"PROWH"]  = u"PRON"
	french_to_universal[u"V"]      = u"VERB"
	french_to_universal[u"VIMP"]   = u"VERB"
	french_to_universal[u"VINF"]   = u"VERB"
	french_to_universal[u"VPP"]    = u"VERB"
	french_to_universal[u"VPR"]    = u"VERB"
	french_to_universal[u"VS"]     = u"VERB"
	#nb, I is not part of the universal tagset--interjections get mapped to X
	french_to_universal[u"I"]      = u"X"
	#strange: N was not in the list of tags that I saw, but it must be in the list and likely maps to NOUN
	french_to_universal[u"N"]      = u"NOUN"
	#likewise, C is also missing; assume it maps to CONJ
	french_to_universal[u"C"]      = u"CONJ"
	return french_to_universal

french_to_universal_dict = create_french_to_universal_dict()

def map_french_tag_to_universal(list_of_french_tag_tuples):
	'''Read in a list of tuples (word, pos) and return the same list with pos mapped to universal tagset.
	Note: We skip the CL tag because this designates clause, which is a class that is not present in the Universal Tagset '''
	return [ (tup[0], french_to_universal_dict[ tup[1] ]) for tup in list_of_french_tag_tuples if tup[1] != u"CL" ]

###############################
# Define Similarity Functions #
###############################

def counter_cosine_similarity(c1, c2):
	'''Read in two counters and return their cosine similarity'''
	terms = set(c1).union(c2)
	dotprod = sum(c1.get(k, 0) * c2.get(k, 0) for k in terms)
	magA = math.sqrt(sum(c1.get(k, 0)**2 for k in terms))
	magB = math.sqrt(sum(c2.get(k, 0)**2 for k in terms))
	return dotprod / (magA * magB)

def longest_common_subsequence_length(a, b):
	'''Read in two lists and return the length of their longest common subsequence'''
	table = [[0] * (len(b) + 1) for _ in xrange(len(a) + 1)]
	for i, ca in enumerate(a, 1):
		for j, cb in enumerate(b, 1):
		    table[i][j] = (
			table[i - 1][j - 1] + 1 if ca == cb else
			max(table[i][j - 1], table[i - 1][j]))
	return table[-1][-1]        
	    
def longest_contiguous_subsequence_length(a, b):
	'''Read in two lists and return the length of their longest contiguous subsequence'''
	table = [[0] * (len(b) + 1) for _ in xrange(len(a) + 1)]
	l = 0
	for i, ca in enumerate(a, 1):
		for j, cb in enumerate(b, 1):
		    if ca == cb:
			table[i][j] = table[i - 1][j - 1] + 1
			if table[i][j] > l:
			    l = table[i][j]
	return l
	    
def find_relative_frequencies(pos_counter):
	'''Iterate over the POS tags and find the relative frequency of each for the current string'''
	rel_freqs = []
	for pos_class in ["ADV", "NOUN", "ADP", "PRON", "DET", "ADJ", ".", "PRT", "CONJ", "NUM", "VERB"]:
		rel_freqs.append( ( pos_class, pos_counter[pos_class] / sum(pos_counter.values()) )  )
	return rel_freqs
		
def calculate_syntactic_similarity(french_pos_tuples, english_pos_tuples):
	'''Read in two lists of (word, pos) tuples and returns their cosine similarity, logest_common_subsequence, and longest_common_contiguous_sequence''' 
	french_pos_list           = [tup[1] for tup in french_pos_tuples]
	english_pos_list          = [tup[1] for tup in english_pos_tuples]	
	french_pos_counter        = Counter(french_pos_list)
	english_pos_counter       = Counter(english_pos_list)
	
	english_rel_freqs         = find_relative_frequencies(english_pos_counter)
	french_rel_freqs          = find_relative_frequencies(french_pos_counter)
	
	cosine_similarity         = counter_cosine_similarity(french_pos_counter, english_pos_counter)
	lc_subsequence            = longest_common_subsequence_length(french_pos_counter, english_pos_counter) #/ len(french_pos_list) 
	lc_contiguous_subsequence = longest_contiguous_subsequence_length(french_pos_counter, english_pos_counter) #/ len(french_pos_list)   
	return cosine_similarity, lc_subsequence, lc_contiguous_subsequence, english_rel_freqs, french_rel_freqs

########################### 
# Set Stanford Parameters #
###########################

# Set java_home path from within script. Run os.getenv("JAVA_HOME") to test java_home
os.environ["JAVA_HOME"] = "C:\\Java\\jdk1.8.0_45\\bin"

# Specify paths 
path_to_english_model = "C:\\stanford\\stanford-postagger-full-2015-04-20\\models\\english-bidirectional-distsim.tagger"
path_to_french_model = "C:\\stanford\\stanford-postagger-full-2015-04-20\\models\\french.tagger"
path_to_jar = "C:\\stanford\\stanford-postagger-full-2015-04-20\\stanford-postagger.jar"

# Define English and French taggers
english_tagger = POSTagger(path_to_english_model, path_to_jar, encoding="utf-8")
french_tagger = POSTagger(path_to_french_model, path_to_jar, encoding="utf-8")

###############
# Parse texts #
###############

with codecs.open("pos_relative_frequencies.txt","w","utf-8") as rel_freqs_out:
	with codecs.open("syntactic_similarities.txt","w","utf-8") as out:
		with codecs.open("goldsmith_training_subset.csv","r","utf-8") as goldy:
			goldy = goldy.read().split("\n")
			for count, row in enumerate(goldy[:-1]):
				split_row = row.split("\t")
				french = split_row[0][1:-1]
				english = split_row[1][1:-1]

				# Each tuple in list_of_english_pos_tuples = (word, pos). Those tuples are contained in a list, which are contained in a one member list
				list_of_english_pos_tuples = english_tagger.tag(word_tokenize(english))[0]
				list_of_french_pos_tuples = french_tagger.tag(word_tokenize(french))[0]
						
				# Simplify each tagset
				simplified_pos_tags_english = [(word, map_tag('en-ptb', 'universal', tag)) for word, tag in list_of_english_pos_tuples]
				simplified_pos_tags_french = map_french_tag_to_universal( list_of_french_pos_tuples )
					
				out_values = calculate_syntactic_similarity(simplified_pos_tags_french, simplified_pos_tags_english)
				
				out.write(unicode(count) + "\t" + "\t".join(str(x) for x in out_values[0:3] ) + "\n" )
				
				for t in out_values[3]:
					rel_freqs_out.write("english\t" + unicode(count) + "\t" + "\t".join(unicode(x) for x in t) + "\n")
					
				for t in out_values[4]:
					rel_freqs_out.write("french\t" + unicode(count) + "\t" + "\t".join(unicode(x) for x in t) + "\n")