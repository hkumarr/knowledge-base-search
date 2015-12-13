from nltk.corpus import stopwords
from requests import get
from nltk import pos_tag, word_tokenize
#from stat_parser import Parser
from nltk.parse import pchart
from nltk.corpus import wordnet as wn
from pandas import DataFrame
import nltk
import pickle
import subprocess

import csv

#nltk.download()
import re
import AnswerSearch

#replace this variable with your current directory

currdir = '/home/harish/NLP_Aristo/aristo/'

#helper files
outputfile = open(currdir+'sorted_output.txt','w')
outputfile2 = open(currdir+'unique_relations.txt','w')
argfileout = open(currdir+'arg_rel_out.txt','w')
onlyrel = open(currdir+'only_rels','w')
stemrel = open(currdir+'stem_rels','w')
'''answerFile = open('answer_corpus.pkl','r')
answer_corpus = pickle.load(answerFile)'''

verb_tags = ['VB','VBG','VBD','VBP','VBN','VBP']

#Add the concepts for which you have question files to this list
concept_list = ['bacteria','blood','blood vessels','earthquakes','evolution','fossils','soil','photosynthesis','stars','volcanoes','solar system']

questions = []
triples = []
unique_rels =[]
unique_pairs = []
n_ary_rels = []
fact_rels = []
arg_rels =[]
unique_objs = []
ques_triple_map = {}

rels_on_concept = []
reltriple_on_concept = []


concept = ''

class KBData:
	
	triple = ''
	relation = ''
	score = 0
	stemmed = ''
	rel_triple = ''
	ques = ''
	arg1 = ''
	arg2 = ''
	pos_tag = []

#To filter the definitive statements
def filter_definitive_statements(rels_list):
	
	new_list = []
	define_word = 'defin'
	mean_word = 'mean'
	between_word = 'between'
	for i in range(len(rels_list)):
		print "hi"
		if (re.search(define_word,rels_list[i].ques_line) or re.search(mean_word,rels_list[i].ques_line) or re.search(between_word,rels_list[i].ques_line)):
			print "hee"
			print rels_list[i].ques_line
		else: new_list.append(rels_list[i])
	return new_list

#To compute pos tag of tokens in the statement
def postag_statements(rels_list):

	for i in range(len(rels_list)):	
		text = word_tokenize(rels_list[i].ques_line)
		rels_list[i].pos_tag = nltk.pos_tag(text)
		print rels_list[i].pos_tag

#To filter statements with verb ended pos tags
def filter_verbend_postag(rels_list):
	
	new_list = []
	for i in range(len(rels_list)):
		index = len(rels_list[i].pos_tag)
		end_tag = rels_list[i].pos_tag[index-2]
		if(end_tag[1] in verb_tags):
			print rels_list[i].ques_line
		else:
			new_list.append(rels_list[i])
	return new_list



prep_words = ['of','in','for']
wh_phrases = ['what','What','which','Which','who','Who']
when_phrases = ['when','When']

	
#To check if the relation is directly on the concept
def add_to_rels_on_concept(x):
	
	ret = False
	arg_with_val = ''
	
	
	if(x.arg1 == '?' or x.arg2 == '?'):
		print x.arg1,x.arg2
		if(x.arg1 == '?'):

			arg_with_val = x.arg2
		else:
			arg_with_val = x.arg1
		#remove stop words
		stop = stopwords.words('english')
		arg_list = arg_with_val.split()
		mynewtext =[w for w in arg_list if w not in stop]
		
		if(len(mynewtext)==1):
			print "The words in argval:",mynewtext
			mynewtext[0] = mynewtext[0].replace(')','')
			print "mynewtext----concept",mynewtext[0].lower(),concept
			if(re.search(mynewtext[0].lower(),concept) != None):
				rels_on_concept.append(x)
				reltriple_on_concept.append(x.rel_triple)
				print "The relation on concept--",x.rel_triple
				ret = True
	return ret
	
#check if the concept is present in the triple
def check_blank(triplet =[]):
	index = 0
	for i in range(len(triplet)):
		if(re.search(r'BLANK_',triplet[i]) ):
			index = i+1
	return index


##************* MAIN STARTS HERE*****************##

#Get the concept as input and returns a list of relations and corressponding questions#
def conceptSearch(concept_ip):
	global rels_on_concept
	global concept
	concept = raw_input('Enter the concept: ')
	#concept = concept_ip
	print concept
	print concept_list
	if concept in concept_list:
		concept_txt = currdir+"concepts/"+concept+"_ques.txt"
	else:
		print "Questions for this concept are not available..!!"
		exit()

	concept_file = open(concept_txt,'r')
	concept_ques = open(currdir+'concept_ques.txt','w')

	for line in concept_file:
		ques = line.split('::')
		words = ques[1].split(' ')
		if(words[0] in wh_phrases):
			concept_ques.write(ques[1])

	#Convert the questions into statements
	p = subprocess.Popen(['/home/harish/Downloads/sbt/bin/./sbt',"controller/run-main org.allenai.ari.controller.questionparser.QuestionPassage -i /home/harish/NLP_Aristo/aristo/concept_ques.txt"])
	print "HI"
	out, err = p.communicate()

	#Extract the statements alone
	concept_ques = open(currdir+'blank_statements.txt','r')
	outputFile = open(currdir+'output.txt','w')
	i=0
	lines = concept_ques.readlines()
	for line in lines:
		print line
		if(re.search(r'---',str(line))):
			i =0 
 			i =i +1
        	else:
			if(i == 2):
				outputFile.write(line)
				line =  line.split(' ')
				curr = ""
				for i in range(len(line)-1):
					curr = curr+" "+line[i+1]
				print curr
			else:
				i = i+1

	#Convert the statements into relation triples
	p = subprocess.Popen(['java', '-Xmx4g', '-XX:+UseConcMarkSweepGC', '-jar', '/home/harish/Downloads/openie-4.1.jar', '/home/harish/NLP_Aristo/aristo/output.txt', 'rel_triples.txt'])
	out, err = p.communicate()

	ques_file = open(currdir+'output.txt','r')
	inputfile = open(currdir+'rel_triples.txt','r')
	rels_on_concept_file = open(currdir+'rels_on_concept.txt','w')

	for line in ques_file:
		questions.append(line)

	ques_line = ''
	for line in inputfile:
		if(len(line) == 0):
			continue
		elif (line in questions):
			ques_line = line
			continue
		else: 
			line = line.split(" ")
			if(line[0] != "\n"):
				#print line[0]
				curr= ""
				for i in range(len(line)-1):
					curr = curr+line[i+1]+" "
				ptr = curr.strip('(')
				ptr = ptr.strip('\n')
				triple = ptr.split(';')
				try:
					if(triple[1]):
					#print line[0],triple[1]	
						triples.append((float(line[0]),triple,ques_line))
						ques_triple_map[triple[1]] = ques_line
				except:
					ee=0
			

	final_sorted = list(sorted(triples, key=lambda x: x[0],reverse = True))   
       
	for i in range(len(final_sorted)):
		print final_sorted[i][0]," ",final_sorted[i][1]
		outputfile.write(str(final_sorted[i][0])+"\t")
		x = final_sorted[i][1]
		outputfile.write("relation:"+x[1]+"\t\t\t"+"triple:")
		if(x[1] not in unique_rels):
			onlyrel.write(x[1]+"\n")
			unique_rels.append(x[1])
			outputfile2.write(str(final_sorted[i][0])+"\t\t"+x[1]+"\n")
		#create new KBData
			kb = KBData()
			kb.score = final_sorted[i][0]
			kb.ques_line = final_sorted[i][2]
			kb.relation = x[1]
		
			mytriple = ''
			for m in range(len(x)):
				mytriple = mytriple+x[m]+"---"
				outputfile2.write(x[m]+"---")
			kb.triple = mytriple+"\n"
		
			outputfile2.write("\n")
			if(len(x) > 3):
				#more than a triple
				n_ary_rels.append(x)
				kb.rel_triple = str(x[1])
			
			else:
				index = check_blank(x)
				if(index):
					index = index -1
					if(index == 0):
						arg1 = '?'
						arg2 = x[2]
						rel = x[1]
						arg_rels.append(str(x[1]+'('+arg1+','+arg2))
						kb.rel_triple = str(x[1]+'('+arg1+','+arg2)
						kb.arg1 = arg1#append the args in a triple to the object
						kb.arg2 = arg2
					else:
						arg2 = '?'
						arg1 = x[0]
						rel = x[1]

						arg_rels.append(str(x[1]+'('+arg1+','+arg2+')'))
						kb.rel_triple = str(x[1]+'('+arg1+','+arg2+')')	
						kb.arg1 = arg1#append the args in a triple to the object
						kb.arg2 = arg2
					
				else:
					fact_rels.append(str(x[1]+'('+x[0]+','+x[2]))
					kb.rel_triple = str(x[1]+'('+x[0]+','+x[2])
					kb.arg1 = x[0]#append the args in a triple to the object
					kb.arg2 = x[2]

			unique_objs.append(kb)	

		for m in range(len(x)):
			outputfile.write(x[m]+"-----")
		outputfile.write("\n")
	
	print "n-ary rels...."
	print n_ary_rels
	print "fact rels...."
	print fact_rels
	print "arg_rels...."
	print arg_rels
	print len(arg_rels)

	for x in arg_rels:
		argfileout.write(x)
		argfileout.write('\n')
	for x in fact_rels:
		argfileout.write(x)
		argfileout.write('\n')


	#remove stop words
	stop = stopwords.words('english')
	for x in range(len(unique_objs)):
		phrase = unique_objs[x].relation
		phrase = phrase.split()
		mynewtext =[w for w in phrase if w not in stop]
		if(len(mynewtext)>0):
			currstr = ''
			for i in range(len(mynewtext)):
				currstr = currstr+' '+mynewtext[i]
			unique_objs[x].stemmed = currstr
		else:
			unique_objs[x].stemmed = unique_objs[x].relation


	for x in range(len(unique_objs)):
		print unique_objs[x].relation,'\t\t',unique_objs[x].stemmed,'\t',unique_objs[x].arg1,'\t',unique_objs[x].arg2
		stemrel.write(unique_objs[x].stemmed+'\n')

	for x in range(len(unique_objs)):
		if(add_to_rels_on_concept(unique_objs[x])):
				print "added to rels"
				rels_on_concept_file.write(unique_objs[x].rel_triple+"\t"+unique_objs[x].ques_line+"\n")
				rels_on_concept_file.write("-----------------------\n")
	
	rels_on_concept = filter_definitive_statements(rels_on_concept)

	postag_statements(rels_on_concept)

	new_rels_on_concept = filter_verbend_postag(rels_on_concept)
	print len(rels_on_concept)
	print len(new_rels_on_concept)
	'''filter_relative_clauses(new_rels_on_concept)
	postag_statements(unique_objs)
	extract_events_noun_verb(unique_objs)'''
	#parse_answer()

	con_out_file = open(currdir+'concept_output.txt','w');
	filt_out_file =  open(currdir+'filtered_concept_output.txt','w');

	buckets = []

	for x in rels_on_concept:
		bucket_found = 0
		if len(buckets) != 0:
			for bucket in buckets:
				for rel in bucket:
					if re.search(rel.stemmed,x.stemmed) or re.search(x.stemmed,rel.stemmed):
						bucket.append(x)
						bucket_found = 1
						break
				if bucket_found == 1: break
			if bucket_found == 0:
				new_bucket = []
				new_bucket.append(x)
				buckets.append(new_bucket)
		else:
			new_bucket = []
			new_bucket.append(x)
			buckets.append(new_bucket)

	l1 = []
	l2 = []

	for bucket in buckets:
		#if len(bucket) > 1: 
			for rel in bucket:
				l1.append(rel.rel_triple)
				con_out_file.write(rel.rel_triple)
			#con_out_file.write("\n")
				l2.append(rel.ques_line)
				con_out_file.write(rel.ques_line)
			#con_out_file.write("\n")
				con_out_file.write("\n")
			con_out_file.write("----------------------\n")
			l1.append("-------")
			l2.append("-------")

	df = DataFrame({'Relation Triple': l1, 'Question': l2})

	df.to_excel(currdir+'concept_output.xlsx', sheet_name='sheet1', index=False)

	buckets = []

	for x in new_rels_on_concept:
		bucket_found = 0
		if len(buckets) != 0:
			for bucket in buckets:
				for rel in bucket:
					if re.search(rel.stemmed,x.stemmed) or re.search(x.stemmed,rel.stemmed):
						bucket.append(x)
						bucket_found = 1
						break
				if bucket_found == 1: break
			if bucket_found == 0:
				new_bucket = []
				new_bucket.append(x)
				buckets.append(new_bucket)
		else:
			new_bucket = []
			new_bucket.append(x)
			buckets.append(new_bucket)

	l1 = []
	l2 = []

	csvfile = open(currdir+'filtered_concept_output.csv','w')
	fieldnames = ['statement','triple','bucket']
	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
	writer.writeheader()
	buc_count = 1

	for bucket in buckets:
		#if len(bucket) > 1: 
			for rel in bucket:
				ind_set = {}
				l1.append(rel.rel_triple)
				filt_out_file.write(rel.rel_triple)
				#filt_out_file.write("\n")
				l2.append(rel.ques_line)
				filt_out_file.write(rel.ques_line)
				#AnswerSearch.constructQuery(rel)
				#filt_out_file.write("\n")
				filt_out_file.write("\n")
				ind_set['statement'] = rel.ques_line
				ind_set['triple'] = rel.rel_triple
				ind_set['bucket'] = buc_count
				writer.writerow(ind_set)
			filt_out_file.write("----------------------\n")
			l1.append("-------")
			l2.append("-------")
			buc_count = buc_count + 1

	df = DataFrame({'Relation Triple': l1, 'Question': l2})

	df.to_excel(currdir+'filtered_concept_output.xlsx', sheet_name='sheet1', index=False)

	pr = subprocess.Popen(['/home/harish/solr-5.3.1/bin/post', '-c', 'gettingstarted', '/home/harish/NLP_Aristo/aristo/filtered_concept_output.csv'])
	print "HI"
	out, err = pr.communicate()
	return l1,l2

conceptSearch("search")