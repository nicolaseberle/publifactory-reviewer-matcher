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


# REQUESTS ES

res = es.search(index=INDEX_NAME, body={
    "query": {"match_all": {}},
    "size": 100000,
    "_source": ["paperAbstract"]
})
res = res['hits']['hits']

df_temp = pd.DataFrame(res)
