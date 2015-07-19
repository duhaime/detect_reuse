#!/usr/bin/python
# -*- coding: utf-8 -*-
import goslate, codecs, sys

def translate_text(text_to_translate, target_language):
	'''Read in a text t and target language, and attempt to return t translated into the target language'''
	tries = 0
	max_tries = 20
	while tries < max_tries:
		try:
			translated = gs.translate(text_to_translate, target_language)
			tries = 20
			#time.sleep(1)
			return translated
			
		except Exception as exc:
			print "An exception occurred while translating your text:", exc
			tries += 1
			#time.sleep(tries*4)
			
def process_text(input_text, encoding, target_language):
	'''Read in an input text, encoding, and target_language, and try to write the translated text to disk'''
	with codecs.open(input_text[:-4] + "_translated.txt", "a", encoding) as out:
		with codecs.open(input_text, "r", encoding) as f:
			f = f.read().replace("\r","").split("\n\n")
			for row_num, row in enumerate(f[:-1]):
				print "Processing paragraph number", row_num
				
				try:
					clean_row             = " ".join(row.split())
					translation_response  = translate_text(clean_row, target_language)
					
					out.write( translation_response + "\n")
					
				except Exception as exce:
					print "An exception occurred while processing paragraph", row_num, exce
				
input           = sys.argv[1]
target_language = sys.argv[2]
target_encoding = sys.argv[3]
gs              = goslate.Goslate()
	
process_text( input, target_encoding, target_language )
