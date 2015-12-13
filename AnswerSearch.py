from nltk.corpus import stopwords
from requests import get
from nltk import pos_tag, word_tokenize
from stat_parser import Parser
from nltk.parse import pchart
from nltk.corpus import wordnet as wn
from pandas import DataFrame
import nltk
import pickle
import urllib
import subprocess
from bs4 import BeautifulSoup
import time
import re

import argparse
import sys

from googleapiclient.errors import HttpError
from nltk.corpus import stopwords

import utils

import csv
from google_search import Google

'''APIKEY and CSE_ID for calling the google search API'''

API_KEY = "AIzaSyCpmoz0FWlCV4H_XBdhqsGySdBescL6zAI"
CSE_ID = "013670238773978263527:ns3upjp6hhk"


concept = ' '
relation = ' '
stemmed = ' '


class Answer:
	triple = ''
	link = ''
	sent = []

'''Gets the relation as input and removes stop words'''

def stemRelation(phrase):

	global stemmed
	stop = stopwords.words('english')
	currstr = ''
	phrase = phrase.split()
	mynewtext =[w for w in phrase if w not in stop]
	if(len(mynewtext)>0):
			
		for i in range(len(mynewtext)):
			currstr = currstr+' '+mynewtext[i]
	else:
		currstr = phrase

	stemmed = currstr

''' Calls the google search API with given query and keywords.Returns all and 
	filtered sentences'''

def search(google, query, keywords):
    print "\nSearching \"%s\"" % (query)    
    all_sentences = []
    for start in xrange(1, 3):
     #   print (start / 10) + 1,
        try:
            result = google.search(query, start=start)
            
            sentences = utils.get_sentences(result)
            
            all_sentences.extend(sentences)

        except HttpError as e:
            print "\nERROR: {}\n".format(e)
            break
            # sys.exit()
    print "\nFiltering sentences using", keywords
    #filtered_sentences = utils.filter_sentences(list(set(all_sentences)),
    #                                            keywords)
    filtered_sentences = []

    return all_sentences, filtered_sentences



def searchAnswer(searchQuery):

    search_results = open('search_results.txt','w')
    stop_words = set(stopwords.words('english'))
    google = Google(API_KEY, CSE_ID)
    query = searchQuery
    #keywords = filter(lambda x: x not in stop_words, map(lambda x: x.strip(), filter(bool, query.split("*"))))
    keywords = filter(lambda x: x , map(lambda x: x.strip(), filter(bool, query.split(" "))))
    print keywords 
    all_sentences, filtered_sentences = search(google, query, keywords)

    print "\nRAW SENTENCES:"
    for x in all_sentences:
        print "- ", x.sent
        print x.link
        search_results.write(x.link)
        search_results.write("\n")
     
        for sent in x.sent:
        	sents = nltk.sent_tokenize(sent)
        	for y in sents:
        		#if(re.search(query,y)):
        			search_results.write(y)
        			search_results.write("\n")
    #exit()
    poss_ans,other_ans = extractTriples(all_sentences,searchQuery)
        #text = extractTextFromLink(x.link,x.sent)
        #for sent in sents:
        	#search_results.write(sent)
        	#search_results.write("\n")
   
    new_poss_ans = []

    for x in poss_ans:
    	cur_trip = ''
    	for t in x.triple:
    		cur_trip = cur_trip + t
    	if(len(new_poss_ans)==0): new_poss_ans.append(x)
    	else:
    		found = False
    		for y in new_poss_ans:
    			cur_add_trip = ''
    			for ti in y.triple:
    				cur_add_trip = cur_add_trip + ti
    			if(cur_trip == cur_add_trip): 
    				found = True
    				break
    		if(found == False): new_poss_ans.append(x)





    print "\nFILTERED SENTENCES:"
    #for x in filtered_sentences:
     #   print "- ", x
        
    print "\n"
    print "Found", len(filtered_sentences), "sentences"
    return new_poss_ans,other_ans



''' Called from pipeline when a relation is extracted.Query is constructed 
	and Google search API is called'''
def constructQuery(rel,con):

	global concept,relation
	concept = con
	s = rel.split('(')
	relat = s[0]
	arglist = s[1].split(',')
	arg1 = arglist[0]
    #arg2 = arglist[1].strip(')')
	r = arglist[1].split(')')
	arg2 = r[0]
	print relat,arg1,arg2

	relation = relat
	stemRelation(relation)
	if(arg1=='?'):
		query = relat + arg2
	else:
		query = arg1 + relat

	return searchAnswer(query)



''' This API gets the search results along with the links as input.It gives
	the search_result.txt '''

def extractTriples(documents,query):

	#Convert the statements into relation triples using OpenIE
	p = subprocess.Popen(['java', '-Xmx4g', '-XX:+UseConcMarkSweepGC', '-jar', '/home/harish/Downloads/openie-4.1.jar', '/home/harish/NLP_Aristo/aristo/search_results.txt', 'search_triples.txt'])
	out, err = p.communicate()
	search_triples = open('search_triples.txt','r')
	possible_answers = []
	other_answers = []

	'''process the search_triples.txt file and populate a data structure
	   with the triples'''

	curr_sent = ' '
	curr_link = ' '
	for line in search_triples:
		if(re.search(';',line)):
			line = line.split(" ")
			triplet = []
			if(line[0] != "\n"):
				#print line[0]
				conf_score = line[0]
				curr= ""
				for i in range(len(line)-1):
					curr = curr+line[i+1]+" "
				ptr = curr.strip('(')
				ptr = ptr.strip('\n')
				triplet = ptr.split(';')
				#print triplet

			concept_ind = isConceptInArg(triplet)
			
			relation_ind = isRelationInArg(triplet)
			ans = Answer()
			ans.triple = triplet
			ans.link = curr_link
			ans.sent = curr_sent

			if (concept_ind != -1) and (relation_ind != -1):
				print "possible_answer",triplet,curr_link,curr_sent
				possible_answers.append(ans)
			else:
				other_answers.append(ans)
				

		else:
			if(re.search('http',line)):
				curr_link = line
			else: 
				curr_sent = line


	return possible_answers,other_answers

''' Given a triple set,concept_index and relation_index
    if there is an argument other than those indices which denotes the possible answer'''

def getPossibleAnswer(triple,concept_index,relation_index):

	answer = ''
	for i in range(len(triple)):
		if((i != concept_index)  and (i != relation_index)):
			answer = answer + triple[i]
	return answer

'''Given a triple set,identify if the concept is in an argument.If so return
	that index else return -1'''
def isConceptInArg(triple):

	ret_val = -1
	for i in range(len(triple)):
		if(re.search(concept,triple[i])):
			ret_val = i
	return ret_val

''' Given the triple set,identify if the stemmed relation is part 
	of an argument.If so,return that index else return -1
'''
def isRelationInArg(triple):

	ret_val = -1
	for i in range(len(triple)):
		if(re.search(stemmed,triple[i])):
			ret_val = i
	return ret_val


#searchAnswer("kills bacteria")
#extractTriples('hello','hi')
