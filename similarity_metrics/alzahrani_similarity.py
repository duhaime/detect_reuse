from __future__ import division
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.util import ngrams
import codecs, sys, itertools, regex

###################
# Build Functions #
###################

def generate_stopwords():
	'''generate stopword list compiled by Ted Underwood'''
	with codecs.open("../text_cleaning_resources/underwood_stopwords.txt","r","utf-8") as stopwords_in:
		stopwords = set(stopwords_in.read().split())
		return stopwords

def remove_stopwords(s):
	'''read in a string and return the split string without stopwords'''
	return [x for x in s.lower().split() if x not in stopwords and len(x) > 1]
    
def remove_punctuation(s):
	'''read in a string and return that strip without any punctuation except the hyphen and en-dash'''
	return regex.sub(ur"[^\P{P}-']+", " ", s)
	
def lemmatize_word(w):
	return lemmatizer.lemmatize(w)	
	
def preprocess_string(s):
	'''read in a string, return the string without stop words punctuation in lowercase form'''
	return [ lemmatize_word(w) for w in remove_stopwords(remove_punctuation(s).lower()) ]
	
def generate_synonym_dict(synonym_matrix):
	'''read in a tab-separated file wherein the first column of each row contains a word and all subsequent columns contain its synonyms'''
	with codecs.open(synonym_matrix,"r","utf-8") as synonyms_in:
		synonym_dict     = {}
		synonyms_in = synonyms_in.read().split("\n")
		for row_count, row in enumerate(synonyms_in):
			try:
				split_row = row.split("\t")
				synonym_dict[split_row[0]] = split_row[1:]
			except:
				print "There was trouble reading row", row_count, "of your synonym matrix. That row was skipped."
	return synonym_dict
	
def find_synonyms(word):
	'''read in a word and return its list of synonyms'''
	try:
		return synonym_dict[word]
	except:
		return [word]

def is_iterable(object):
	'''read in an object and return True if that object is iterable, otherwise return False'''
	try:
		iter(object)
		return True
	except:
		return False
		
def create_windows(iterable, size):
	'''read in an interable and integer and return consecutive slices of that iterable of length `size`'''
	shiftedStarts = [itertools.islice(iterable, s, None) for s in xrange(size)]
	return itertools.izip(*shiftedStarts)
	
def alzahrani_similarity(a, b, preprocess=1, length_normalize=1):
	'''read in two strings and return their alzahrani similarity'''
	similarity    =  0
	if preprocess == 1:
		a = preprocess_string(a)
		b = preprocess_string(b)
	
	for aw in a:
		if aw in b:
			similarity += 1
		else:
			for bw in b:	
				if aw in find_synonyms( bw ):
					similarity += .5
					break		
					
	if length_normalize == 1:
		try:
			return similarity / max(len(a), len(b))
		except ZeroDivisionError:
			return similarity
	else:
		return similarity	
		
def alzahrani_window_similarity(a_string, b_string, window_length, preprocess=1, window_length_normalize=1):
	'''read in two strings a,b and integer window_length and return the maximum alwhazari similarity across subwindows of the specified length'''
	a_windows      = list( ngrams( preprocess_string(a_string), window_length ) )
	b_windows      = list( ngrams( preprocess_string(b_string), window_length ) )
	max_similarity = 0
	
	for a_window in a_windows:
		for b_window in b_windows:						
			sim = alzahrani_similarity( list(a_window), list(b_window), preprocess=0, length_normalize=window_length_normalize )
			if sim > max_similarity:
				max_similarity = sim
				
	return max_similarity
	
def run_calculations(text_to_analyze):
	'''Main function called below: reads in texts and runs similarity calculations'''
	with codecs.open("similarity_scores.txt","w","utf-8") as out:
		with codecs.open(text_to_analyze, "r", "utf-8") as infile:
			infile_rows = infile.read().split("\n")[:-1]
			for row_number, row in enumerate(infile_rows):
				
				'''To obtain only the aggregate similarity score, one can run just the following line:
				print row_number, alzahrani_similarity(split_row[1], split_row[2])'''
				
				''' The following block allows one to measure the degree of separation as the subwindow size increases:'''
				
				print "Processing row", row_number
				
				try:
					split_row = row.split("\t")
					
					if row_number <= 24:
						groundtruth = 1
					else:
						groundtruth = 0
					
					shorter_row_text_length = min(  len(preprocess_string(split_row[1])), len(preprocess_string(split_row[2])) )
					
					for i in xrange( shorter_row_text_length - 1 ):
						desired_window_length = 1+i
					
						out.write( unicode(row_number) + "\t" + 
						unicode(groundtruth) + "\t" + 
						unicode(desired_window_length) + "\t" +
						unicode(alzahrani_similarity(split_row[1], split_row[2])) + "\t" +
						unicode(alzahrani_window_similarity(split_row[1], split_row[2], desired_window_length)) + "\n")
				
				except Exception as exc:
					print "There was an error reading row", row_number, "from the text_to_analyze. That row was skipped. Exception:", exc
					
##################
# Define Globals #
##################

if len(sys.argv) != 3:
	print "\nThis script requires as input two infiles. The first is a tab-separated file in which the first cell of each row contains a word and all subsequent cells contain synonyms for that word. This file = {synonym_dictionary} below. The second required file is a tab-separated matrix in which each row contains two sentences to be compared during the analysis. This file = {text_to_analyze} below.\n\nTo run the script, please use:  python alwhazari_similarity.py {synonym_dictionary} {text_to_analyze}"
	sys.exit()

lemmatizer       = WordNetLemmatizer()
stopwords        = generate_stopwords()	
synonym_dict     = generate_synonym_dict( sys.argv[1] )
text_to_analyze  = sys.argv[2]

run_calculations(text_to_analyze)