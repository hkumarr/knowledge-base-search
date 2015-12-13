
from urllib2 import *
from collections import OrderedDict

''' API to search the solr with the given concept input.It returns the 
    list of triple and the popularity of this triple
'''
def searchSolr(concept):
	url = 'http://localhost:8983/solr/gettingstarted/select?q='+concept+'&wt=python&rows=500'
	connection = urlopen(url)
	response = eval(connection.read())
	retval = {}
	buckets = []
	for document in response['response']['docs']:
  		#print "  statement=", document['statement'][0] ,document['bucket'][0]
  		if document['bucket'][0] not in retval.keys():
  			retval[document['bucket'][0]] = []
  		
  		retval[document['bucket'][0]].append(document)

  	
  	desc = OrderedDict(sorted(retval.items(), key=lambda kv: len(kv[1]), reverse = True))
  	OrderedResult = []
  	for bucket in desc.keys():
  	    #print desc[bucket]
  	    bucket_length = len(desc[bucket])
  	    instance = desc[bucket][0]
  	    #print instance['triple'],bucket_length
  	    OrderedResult.append((instance['triple'][0],bucket_length))
  	return OrderedResult

#searchSolr('bacteria')
