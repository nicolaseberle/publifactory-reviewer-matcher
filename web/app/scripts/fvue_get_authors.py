# IMPORT

import pandas as pd
from elasticsearch import Elasticsearch
from bson.json_util import dumps

# REQUESTS ES


def get_authors_es(name, keywords, journals):
    es_host = 'elasticsearch'
    es = Elasticsearch(hosts=[es_host])
    index_name = 'authors_large'

    res = es.search(index=index_name, body={
        "explain": "true",
        "query": {
            "bool": {
                "should": [
                    {
                        "match": {
                            "name": name
                        }
                    },
                    {
                        "match": {
                            "entities": keywords
                        }
                    },
                    {
                        "match": {
                            "journals": journals
                        }
                    }
                ]
            }
        },
    "_source": ["name", "entities", "articles", "journals"]
    })
    res = res['hits']['hits']

    return res

