from __future__ import division
from sklearn.metrics.pairwise import cosine_similarity
from gensim.models.word2vec import Word2Vec
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.util import ngrams
from logging import basicConfig, INFO
import codecs, os, regex

###########################
# String Cleaning Methods #
###########################

def load_stopwords():
	'''Return the NLTK's English stopwords list'''
	return set(stopwords.words('english'))

def remove_stopwords(s):
	'''Read in a string and return that word as a split list without stopwords'''
	return [w for w in s if w not in stops and len(w) > 2]
	
def lemmatize_word(w):
	'''Read in a single word and return it in its lemmatized state'''
	return lemmatizer.lemmatize(w)

def remove_punctuation(s):
	'''Read in a string and return that string without any puncutation'''
	return regex.sub(ur"\p{P}+","", s)	
	
def create_ortho_dict():
	'''Create mapping from spelling variant to controlled representation (orthographically-normalized representation) of word'''
	ortho_dict = {}
	with codecs.open("orthographic_variants.txt","r","utf-8") as ortho:
		ortho = ortho.read().replace("\r","").lower().split("\n")[:-1]
		for row in ortho:
			sr = row.split("\t")
			ortho_dict[ sr[0] ] = sr[1]
	return ortho_dict
	
def standardize_spelling(w):
	'''Perform the spelling normalization lookup'''
	try:
		return ortho_dict[w]
	except:
		return w	
	
def preprocess_text(s):
	'''Read in a string, lowercase, strip punctuation, remove duplicates, standardize spelling, then lemmatize each word, and return a tuple of words'''
	l = remove_punctuation(s.lower()).split()
	l = [standardize_spelling(w) for w in l]
	l = remove_stopwords(l)	
	l = [lemmatize_word(w) for w in l]
	l = list(set(l))
	return l

#################################
# Vector Loading and Processing #
#################################

def load_google_vectors():
	'''Return the Google pretrained binary vectors for Word2Vec'''
	return Word2Vec.load_word2vec_format('../google_pretrained_word_vectors/GoogleNews-vectors-negative300.bin.gz', binary=True)
	
def word2vec_word_comparison(w1, w2):
	'''Read in two words from the word2vec_similarity() function and return their word similarity'''
	if w1 == w2:
		return 1
	try:
		v1 = model[ w1 ]
		v2 = model[ w2 ]
		return float( cosine_similarity(v1,v2)[0][0])
		
	#exceptions will occur if w1 or w2 are not in the Google pretrained vector list. 
	except Exception as exc:
		return 0		

def word2vec_similarity(s1, s2, preprocess=1):
	'''Read in two strings and return their length-normalized Word2Vec similarity value'''
	string_similarity = []
	
	if preprocess == 1:
		s1 = preprocess_text(s1)
		s2 = preprocess_text(s2)
	
	for ws1 in s1:
		max_word_similarity = 0
		max_similar_word    = u""
		for ws2 in s2:
			similarity = word2vec_word_comparison(ws1, ws2)
			if similarity > max_word_similarity:
				max_word_similarity = similarity
				max_similar_word    = ws2
		
		#because it's unfair to penalize a string for containing words not in the Google vectors, skip words with max_word_similarity == 0
		if max_word_similarity > 0:
			string_similarity.append( max_word_similarity )
	try:
		return sum(string_similarity) / len(string_similarity)
	
	except Exception as exc:
		print exc
		for x in s1:
			print "".join(y for y in x if ord(y) < 128),
		for x in s2:
			print "".join(y for y in x if ord(y) < 128),
		print "\n"
		return 0

def word2vec_window_similarity(s1, s2, window_length):
	'''Read in two strings and a subwindow_length, and return the maximum similarity value for the subwindows of the specified length'''
	s1_windows      = list( ngrams( preprocess_text( s1 ), window_length ) )
	s2_windows      = list( ngrams( preprocess_text( s2 ), window_length ) )
	
	max_window_similarity = 0
	
	for s1_window in s1_windows:
		for s2_window in s2_windows:
			
			observed_similarity = word2vec_similarity( list(s1_window), list(s2_window), preprocess=0 )
			
			if observed_similarity > max_window_similarity:
				max_window_similarity = observed_similarity
				
	return max_window_similarity
	
###########
# Globals #
###########

basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=INFO)

stops       = load_stopwords()
lemmatizer  = WordNetLemmatizer()
ortho_dict  = create_ortho_dict()
model       = load_google_vectors()	
	
with codecs.open("word_to_vec_similarity_values.txt","w","utf-8") as out:
	with codecs.open("goldsmith_french_to_english.csv","r","utf-8") as goldy:
		goldy = goldy.read().split("\n")
		for count, row in enumerate(goldy[:-1]):
		
			#calculate aggregate similarity
			split_row                = row.split("\t")
			aggregate_similarity     = word2vec_similarity( split_row[1], split_row[2] )
			
			#calculate window similarity
			shorter_row_text_length  = min(  len(preprocess_text(split_row[1])), len(preprocess_text(split_row[2])) )
			window_similarity_tuples = []
			
			for i in xrange( shorter_row_text_length - 1 ):
				desired_window_length = 1+i
			
				max_window_similarity = word2vec_window_similarity(split_row[1], split_row[2], desired_window_length)
				window_similarity_tuples.append( (desired_window_length, max_window_similarity) )
			
			#each window similarity tuple countains a window length and the maximum similarity observed for that window length. Write these in "long format" for ggplot
			for window_similarity_tuple in window_similarity_tuples:
				out.write( unicode(count) + "\t" + unicode(aggregate_similarity) + "\t" + unicode(window_similarity_tuple[0]) + "\t" +unicode(window_similarity_tuple[1]) + "\n")