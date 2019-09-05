# IMPORTS

import pandas as pd
from elasticsearch import Elasticsearch


# CONSTS

ES_HOST = 'localhost'
ES_PORT = '9200'

es = Elasticsearch(hosts=[ES_HOST])

INDEX_NAME = 'articles_large'
DOC_TYPE = 'articles_large'

# Pour changer le nombre de requete max :
# curl -XPUT "http://localhost:9200/articles_large/_settings" -d '{ "index" : { "max_result_window" : 1000000 } }' -H "Content-Type: application/json"


# FUNCTIONS

## REQUESTS ES

def get_abstracts():
    res = es.search(index=INDEX_NAME, body={
        "query": {"match_all": {}},
        "size": 1000000,
        "_source": ["paperAbstract"]
    }, request_timeout=500)
    res = res['hits']['hits']

    df_temp = pd.DataFrame(res)
    return df_temp


## GET ABSTRACT WITH ID

def get_abstract(id):
    value = es.search(index=INDEX_NAME, body={
        "query": {"terms": {"_id": [id]}},
        "_source": ["paperAbstract", "authors", "title", "doi"]
    })
    value = value['hits']['hits']

    return value[0]["_source"]


## ADD NEW VALUE

def add_value_es(id, title, keywords, abstract):
    line = {
        "id": id,
        "title": title,
        "entities": keywords,
        "paperAbstract": abstract
    }
    es.index(index=INDEX_NAME, doc_type=DOC_TYPE, body=line, id=id)
