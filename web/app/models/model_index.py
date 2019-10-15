# IMPORTS

from elasticsearch import Elasticsearch

ES_HOST = 'localhost'
ES_PORT = '9200'

es = Elasticsearch(hosts=[ES_HOST])


# GET ABSTRACTS

from index_scripts.requestsES import get_abstracts

df = get_abstracts(es, 0, 10000)

from index_scripts.implementDB import authors2es

authors2es(es, df)

from index_scripts.requestsES import get_authors

#res = get_authors(es, "Database")

#print(res)