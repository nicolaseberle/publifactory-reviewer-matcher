# IMPORTS

import pandas as pd
# from elasticsearch import Elasticsearch
import pickle


# FUNCTIONS

## REQUESTS ES


def get_abstracts(es, from_value, size_value):
    res = es.search(index="articles_large", body={
        "query": {"match_all": {}},
        "from": from_value,
        "size": size_value,
        "_source": ["entities", "year", "inCitations", "authors", "doi"]
    }, request_timeout=1000)
    res = res['hits']['hits']

    start = from_value + size_value
    pickle.dump(start, open("saves_index/start.p", "wb"))
    
    df_temp = pd.DataFrame(res)
    return df_temp


def get_authors(es, keyword):
    res = es.search(index="authors_large", body={
        "query": {
            "nested": {
                 "path": "keywords",
                 "query": {
                    "bool": {
                       "must": [
                          {
                             "match": {
                                "keywords.key_name": str(keyword)
                             }
                          }
                       ]
                    }
                 }
            }
        },
        "sort": [
            {
                "keywords.key_score": {
                    "order": "desc",
                    "nested_path": "keywords",
                    "nested_filter": {
                        "term": {"keywords.key_name": str(keyword)}
                    }
                }
            },
            {
                "keywords.key_year": {
                    "order": "desc",
                    "nested_path": "keywords"
                }
            }
        ],
        "_source": [
            "name",
            "keywords"
        ]
    }, request_timeout=1000)
    res = res['hits']['hits']

    df_temp = pd.DataFrame(res)
    return df_temp
