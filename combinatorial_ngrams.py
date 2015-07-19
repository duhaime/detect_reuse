from __future__ import division
from nltk.stem.wordnet import WordNetLemmatizer
from collections import deque, defaultdict, Counter
from itertools import islice, combinations
from nltk.util import ngrams
from regex import sub
from nltk import data
from os import path, remove
import sys, codecs, operator

'''Read in two files specified at the command line and calculate the number of shared words within subregions of those texts'''

###########################
# String Cleaning Methods #
###########################

def read_file(file_path):
	'''Read in a file object and return an opened representation of that file'''
	with codecs.open(file_path,'r','utf-8') as f:
		file_contents = " ".join( f.read().split() )
	f.close()
	return file_contents

def create_ortho_dict():
	'''Create mapping from spelling variant to controlled representation (orthographically-normalized representation) of word'''
	ortho_dict = {}
	with codecs.open("text_cleaning_resources/orthographic_variants.txt","r","utf-8") as ortho:
		ortho = ortho.read().replace("\r","").lower().split("\n")[:-1]
		for row in ortho:
			sr = row.split("\t")
			ortho_dict[ sr[0] ] = sr[1]
	return ortho_dict
	
def standardize_spelling(w):
	'''Read in a word and return an orthograpically normalized representation of the word'''
	try:
		return ortho_dict[w]
	except:
		return w

def create_stopwords():
	'''Generate stopword list compiled by Ted Underwood'''
	with codecs.open("text_cleaning_resources/underwood_stopwords.txt","r","utf-8") as stopwords_in:		
		stopwords = set(stopwords_in.read().split())
		return stopwords
		
def remove_stopwords(l):
	'''Read in a list of words and return that list sans stopwords'''
	return [w for w in l if w not in stopwords and len(w) > 1]
	
def remove_punctuation(s):
	'''Read in a string and return that strip without any punctuation except the hyphen and en-dash'''
	return sub(ur"[^\P{P}']+", " ", s)

def remove_digits(s):
	'''Read in a string and return that string without any numerical digits'''
	return filter(lambda c: not c.isdigit(), s)
		
def lemmatize_word(w):
	'''Read in a single word and return it in its lemmatized state'''
	return lemmatizer.lemmatize(w)

def sentence_split(s):
	'''Read in a string and return an iterable, each member of which is a sentence in that file'''
	return tokenizer.tokenize(s)	

def remove_common_words(l):
	'''Read in a list of words and return a list of sufficiently uncommon words in the list'''
	return [w for w in l if retrieve_frequency(w) < .9]
	
#########################
# Combinatorial Methods #
#########################	
		
def sliding_window(iterable, size=10, step=5, fillvalue=None):
	'''Read in an iterable and return a generator with windows of size `size`, using the specified step and fill values'''
	if size < 0 or step < 1:
		raise ValueError
	it = iter(iterable)
	q = deque(islice(it, size), maxlen=size)
	if not q:
		return  # empty iterable or size == 0
	q.extend(fillvalue for _ in range(size - len(q)))  # pad to size
	while True:
		yield iter(q)  # iter() to avoid accidental outside modifications
		q.append(next(it))
		q.extend(next(it, fillvalue) for _ in range(step - 1))

def word_combinations( word_list, size_val=int(sys.argv[3]), step_val=int(sys.argv[4]), combination_length_val=int(sys.argv[5]) ):
	'''Read in a list of words and return combinations of those words matching the user-supplied arguments:
	sys.argv[3] is the window size, 
	sys.argv[4] is the step interval, 
	sys.argv[5] is the length of each tuple to be compared'''
	ngram_list = []
	
	for w in sliding_window( word_list, size=size_val, step=step_val):
		for c in combinations(w, combination_length_val):
			if None not in c:
				# Sort the tuples into alphabetic order (for dimension reduction)
				ngram_list.append( tuple( sorted(c) ) )

	return set(ngram_list)

def clean_words(s):
	'''Read in a string and return a clean array of words in that string'''
	l = remove_digits( remove_punctuation( s.lower()) ).split()
	l = (standardize_spelling(w) for w in l)
	l = remove_stopwords(l)		
	l = (lemmatize_word(w) for w in l)
	l = remove_common_words(l)
	return l	
	
def find_shared_words(s):
	'''Read in a string and return words found in only one file'''
	return [word_to_int[w] for w in s if w in shared_words]
	
def integerize_words(shared_words):
	'''Read in a set of words and return a hash table that maps each word to an integer'''
	word_to_integer = defaultdict()
	word_to_integer.default_factory = lambda: len(word_to_integer)
	for w in shared_words:
		word_to_integer[w]
	return word_to_integer
	
#######################
# Statistical Methods #
#######################	
	
def populate_stats():
	'''Read in a file containing the relative frequency of the 1M most common words in the English language and return in dictionary form'''
	stats_dict = {}
	with codecs.open("text_cleaning_resources/normalized_stats_one_million.txt",'r','utf-8') as f:
		f = f.read().split("\n")[:-1]
		for row in f:
			sr = row.split("\t")
			stats_dict[ sr[0] ] = float( sr[1] )
			
	return stats_dict
	
def retrieve_frequency(word):
	'''Read in a word and return its relative frequency value'''
	try:
		return stats_dict[ word ]
	except Exception as exc:
		return .000001
	
def product(iterable):
	'''Read in an iterable of numerical values and return the product of all those values'''
	return reduce(operator.mul, iterable, 1)			
		
################
# Main Methods #
################		

def generate_ngrams(text_file):
	'''Read in a string, lowercase, strip punctuation, remove duplicates, standardize spelling, then lemmatize each word, and return a tuple of words'''
	ngram_to_sentence_id = defaultdict(list)
	ngram_to_sentence_id["file_path"].append(text_file)
	
	file_contents = read_file(text_file)
	
	for sentence_id, sentence in enumerate( sentence_split(file_contents) ):
		word_list    = clean_words(sentence)
		shared_words = find_shared_words(word_list)
		ngram_iterable = word_combinations(shared_words)
		if ngram_iterable:
			for ngram in ngram_iterable:
				ngram_to_sentence_id[".".join(str(i) for i in ngram)].append(sentence_id)
	return ngram_to_sentence_id	

def count_sentence_matches(results_list):
	'''Read in a list of two autovivify objects and return a Counter object that indicates the number of ngrams shared by sentence pairs in the input documents'''
	matching_ngrams_counter = Counter()
	intersection = set(results_list[0].keys()) & set(results_list[1].keys())
		
	# Given a common ngram, find all sentences that ngram appears within, and increase the match count for that sentence combination'''
	for ngram in intersection:
		for sentence_id_one in results_list[0][ngram]:
			for sentence_id_two in results_list[1][ngram]:
				matching_ngrams_counter[ str(sentence_id_one) + "." + str(sentence_id_two) ] += 1 
							
	return matching_ngrams_counter
	
def write_significant_matches(matching_ngrams_counter):
	'''Read in a Counter object indicating the sentences from the two files that share ngrams, and write those paired sentences to disk'''
	file_one_path      = results[0]["file_path"][0]
	file_two_path      = results[1]["file_path"][0]
	file_one_sentences = sentence_split( read_file(file_one_path) )
	file_two_sentences = sentence_split( read_file(file_two_path) )
	
	with codecs.open("matches.txt",'w','utf-8') as out:
		for sentence_pair in matching_ngrams_counter:
			
			# Raising the integer value below increases precision; lowering it increases recall
			if matching_ngrams_counter[sentence_pair] > 5:
				sentence_one = file_one_sentences[ int(sentence_pair.split(".")[0]) ]
				sentence_two = file_two_sentences[ int(sentence_pair.split(".")[1]) ]
				
				out.write( 
					file_one_path + "\t" +
					file_two_path + "\t" +
					unicode(matching_ngrams_counter[sentence_pair]) + "\t" + 
					sentence_one + "\t" +
					sentence_two + "\n" 
					)
					
###########
# Globals #	
###########	

ortho_dict   = create_ortho_dict()	
stopwords    = create_stopwords()
lemmatizer   = WordNetLemmatizer()
stats_dict   = populate_stats()
tokenizer    = data.load('tokenizers/punkt/english.pickle')
shared_words = set(clean_words(read_file(sys.argv[1]))) & set(clean_words(read_file(sys.argv[2])))
word_to_int  = integerize_words(shared_words)
		
if __name__ == "__main__":
	
	results = []
	infiles = [ sys.argv[1], sys.argv[2] ]
	
	for i in infiles:
		results.append(generate_ngrams(i))
	
	write_significant_matches( count_sentence_matches( results ) )