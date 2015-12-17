# knowledge-base-search

The knowledge-base-search mainly has two parts.One component is to process the questions on a concept and generate the relation triples that involve the concept directly.It also indexes the extracted triples into solr.

The question file on a concept should be placed in the /concepts folder.

Run $python pipeline.py 

You will be prompted to enter the concept for which you need to process.Once entered,the questions are processed and the relation triples are indexed into solr.(Pre-requisite is that solr has to be installed and initiated so that the solr server could index the requests from our pipeline)
