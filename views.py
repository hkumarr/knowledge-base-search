from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
from django.shortcuts import render


import importlib
import pickle
import sys
sys.path.append("/home/harish/NLP_Aristo/aristo/")

#import pipeline
import SearchSolr
import AnswerSearch

class Result:
    triple = ""
    count = 0

concept = ''

#pickle file to cahce the search results for concepts
objfile_read = open('myobj.pkl','r')
try:
    Cache = pickle.load(objfile_read)
except:
    Cache = {}

#view to render the home page for search
def search_form(request):
    global Cache
    objfile = open('myobj.pkl','w')
    pickle.dump(Cache,objfile)
    return render(request, 'search_home.html')

#view to render the results for a particular concept
def search(request):
    global Cache
    global concept
    if 'concept' in request.GET:
        print 'You searched for: %r' % request.GET['concept']
        concept = str(request.GET['concept'].decode("utf-8"))
        #l1,l2 = pipeline.conceptSearch(str(concept))
        documents = SearchSolr.searchSolr(str(concept))
        person = {'name': 'Sally', 'age': '43'}
        send_val = []
        for document in documents:
            #print document[0]
            r = Result()
            r.triple = document[0] 
            r.count = document[1]
            send_val.append(r)
        t = get_template('results.html')
        #AnswerSearch.constructQuery(send_val[0].triple,concept)
        html = t.render(Context({'doc':send_val, 'concept':concept}))
        
    else:
        html = 'You submitted an empty form.'
    return HttpResponse(html)

#view to render the matching google search results for a selected relation triple
def triple(request):
    global Cache
    poss_ans = []
    other_ans = []
    found = False
    triple = request.GET['id'].decode("utf-8")
    #concept = request.GET['con'].decode("utf-8")
    try:
        triple_searched = Cache[concept]
        try:
            ret_val = triple_searched[triple]
            poss_ans = ret_val[0]
            other_ans = ret_val[1]
            found = True
        except:
            found = False
    except:
        found = False

    if(found == False):

        poss_ans,other_ans = AnswerSearch.constructQuery(triple,concept)
        put_val = []
        put_val.append(poss_ans)
        put_val.append(other_ans)
        try:
            triple_searched = Cache[concept]
            triple_searched[triple] = put_val
        except:
            Cache[concept] = {}
            Cache[concept][triple] = put_val

        objfile = open('myobj.pkl','w')
        pickle.dump(Cache,objfile)

    t = get_template('triple.html')
    html = t.render(Context({'triple':triple,'poss_ans':poss_ans,'other_ans':other_ans}))
    return HttpResponse(html)

def hello(request):
    return HttpResponse("Hello world")
