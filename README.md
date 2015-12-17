# knowledge-base-search

The knowledge-base-search mainly has two parts.One component is to process the questions on a concept and generate the relation triples that involve the concept directly.It also indexes the extracted triples into solr.

The question file on a concept should be placed in the /concepts folder.Run the following command:

```sh

 $python pipeline.py 

```

You will be prompted to enter the concept for which you need to process.Once entered,the questions are processed and the relation triples are indexed into solr.(Pre-requisite is that solr has to be installed and initiated so that the solr server could index the requests from our pipeline)

The second component in our system is the web interface,where you can search the triples for a given concept.The web interface lists the triples in the order of popularity of how many people have asked that particular question.When a particular triple is selected,the query for that triple is provided as input to Google Search API.The results are processed using OpenIE and the possible answers are generated.The results are listed along with the links from where the possible answer is extracted.

The pre-requisites are that, django python web framework has to be installed in the system.It can be done by:


```sh

 $pip install dango

```

Other pre-requisites are OpenIE 4.0 to extract relation triples and NLP Aristo project to convert questions into statements with the possible answer replaced with BLANK.

Extract the contents of Aristo project in your project folder and replace the QuestionPassage.scala with the file in the project folder

```sh

/home/Username/NLP_Aristo/aristo/controller/src/main/scala/org/allenai/ari/controller/questionparser

```

Inorder for the web interface to run,invoke your solr server using following command in your solr folder:

```sh
$bin/solr start -e cloud -noprompt

```

Invoke the knowledge-base-search server using the following command:

```sh
 python manage.py runserver

```