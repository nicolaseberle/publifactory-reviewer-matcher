# IMPORT

# import pandas as pd
from elasticsearch import Elasticsearch

# REQUESTS ES


def get_articles_es(value):
    es_host = 'localhost'
    es = Elasticsearch(hosts=[es_host])
    index_name = 'articles_large'

    res = es.search(index=index_name, body={
        "query": {"match": {"title": str(value)}},
        "size": 10,
        "_source": ["title", "paperAbstract", "authors.name", "year"]
    })
    res = res['hits']['hits']

    return res
