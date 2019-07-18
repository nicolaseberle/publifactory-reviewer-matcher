# IMPORT

import pandas as pd
from elasticsearch import Elasticsearch
from bson.json_util import dumps

# REQUESTS ES


def get_articles_es(title, abstract, authors, keywords, journal, year1, year2):
    es_host = 'elasticsearch'
    es = Elasticsearch(hosts=[es_host])
    index_name = 'articles_large'

    res = es.search(index=index_name, body={
            "explain": "true",
            "query": {
                "bool": {
                    "should": [
                        {
                            "match": {
                                "title": str(title)
                            }
                        },
                        {
                            "match": {
                                "paperAbstract": str(abstract)
                            }
                        },
                        {
                            "match": {
                                "authors.name": str(authors)
                            }
                        },
                        {
                            "match": {
                                "entities": str(keywords)
                            }
                        },
                        {
                            "match": {
                                "journalName": str(journal)
                            }
                        }
                    ],
                    "must": {
                        "range": {
                            "year": {
                                "gte": str(year1),
                                "lte": str(year2)
                            }
                        }
                    }
                }
            },
            "size": 10,
            "_source": ["title", "paperAbstract", "authors.name", "entities", "journalName", "year"]
        })
    res = res['hits']['hits']

    return res


def get_article_es(id_art):
    es_host = 'elasticsearch'
    es = Elasticsearch(hosts=[es_host])
    index_name = 'articles_large'

    res = es.search(index=index_name, body={
        "query": { "match": {"id": str(id_art)} },
        "_source": ["title", "paperAbstract", "authors.name", "entities", "journalName", "year"]
    })
    res = res["hits"]["hits"]
    
    return res
