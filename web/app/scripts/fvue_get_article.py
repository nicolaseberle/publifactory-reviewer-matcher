# IMPORT

import pandas as pd
from elasticsearch import Elasticsearch
from pymongo import MongoClient
from bson.json_util import dumps

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


def get_articles_mongo(value):
    db_client = MongoClient(host="localhost", port=27017)
    db = db_client.reviewer_matcher
    coll_art = db.articles
    cursor = coll_art.find(
        {"$text":
            {"$search": value}
         },
        {"_id": 0, "title": 1, "paperAbstract": 1, "authors": 1, "year": 1}
    ).limit(10)

    return cursor
