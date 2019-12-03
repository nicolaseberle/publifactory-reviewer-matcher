# IMPORTS

import pandas as pd
from elasticsearch import Elasticsearch
import pickle

# CONSTS

ES_HOST = 'localhost'
ES_PORT = '9200'

#es = Elasticsearch(hosts=[ES_HOST])

INDEX_NAME = 'articles_large'
DOC_TYPE = 'articles_large'

# Pour changer le nombre de requete max :
# curl -XPUT "http://localhost:9200/articles_large/_settings" -d '{ "index" : { "max_result_window" : 1000000 } }' -H "Content-Type: application/json"


# FUNCTIONS

## REQUESTS ES

def get_abstracts(es, from_value, size_value):
    res = es.search(index=INDEX_NAME, body={
        "query": {"match_all": {}},
        "from": from_value,
        "size": size_value,
        "_source": ["paperAbstract"]
    }, request_timeout=1000)
    res = res['hits']['hits']

    start = from_value + size_value
    pickle.dump(start, open("app/models/saves_v2/start.p", "wb"), protocol=pickle.HIGHEST_PROTOCOL)
    
    df_temp = pd.DataFrame(res)
    return df_temp

## REQUESTS FIELD

def get_abstracts_field(es, from_value, size_value, field):
    res = es.search(index=INDEX_NAME, body={
        "query": {
            "match": {
                "fields": field
            }
        },
        "from": from_value,
        "size": size_value,
        "_source": ["paperAbstract"]
    }, request_timeout=1000)
    res = res['hits']['hits']

    start = from_value + size_value
    pickle.dump(start, open("app/models/similarities/"+field+"/start.pkl", "wb"), protocol=pickle.HIGHEST_PROTOCOL)

    df_temp = pd.DataFrame(res)
    return df_temp


def get_abstracts_field_big(es, from_value, size_value, field):
    res = es.search(index=INDEX_NAME, body={
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "fields": field
                        }
                    }
                ],
                "filter": [
                   {
                       "range": {
                          "year": {
                             "from": 2005
                          }
                       }
                   }
                ]
            }
        },
        "from": from_value,
        "size": size_value,
        "_source": ["paperAbstract"]
    }, request_timeout=1000)
    res = res['hits']['hits']

    start = from_value + size_value
    pickle.dump(start, open("app/models/similarities/"+field+"/start.pkl", "wb"), protocol=pickle.HIGHEST_PROTOCOL)

    df_temp = pd.DataFrame(res)
    return df_temp


## GET OUT-CITATIONS

def get_citations_auth(es, auth):
    res = es.search(index=INDEX_NAME, body={
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "authors.name": auth
                        }
                    }
                ]
            }
        },
        "size": 10,
        "_source": ["outCitations"]
    }, request_timeout=200)
    res = res['hits']['hits']

    return res

def get_citations_id(es, id):
    res = es.search(index=INDEX_NAME, body={
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "id": id
                        }
                    }
                ]
            }
        },
        "_source": ["outCitations"]
    }, request_timeout=200)
    res = res['hits']['hits']

    return res


def get_abstract_id(es, id):
    res = es.search(index=INDEX_NAME, body={
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "id": id
                        }
                    }
                ]
            }
        },
        "_source": ["paperAbstract"]
    }, request_timeout=200)
    res = res['hits']['hits']

    return res


## GET ABSTRACT WITH ID

def get_abstract(es, id):
    #es = Elasticsearch(hosts=[ES_HOST])
    value = es.search(index=INDEX_NAME, body={
        "query": {"terms": {"_id": [id]}},
        "_source": ["paperAbstract", "authors", "title", "doi", "doiUrl", "year", "venue", "inCitations", "fields", "sub_cat"]
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

## GET AUTHOR IN ORCID

def get_authors_doi(es, doi):
    index_name = 'orcid_large'

    res = es.search(index=index_name, body={
        "query": {
            "bool": {
                "should": [
                    {
                        "match_phrase": {
                            "record:record.activities:activities-summary.activities:works.activities:group.common:external-ids.common:external-id.common:external-id-value": str(doi)
                        }
                    }
                ]
            }
        },
        "_source": ["record:record.person:person", "record:record.common:orcid-identifier", "record:record.activities:activities-summary"]
    })
    
    res = res["hits"]["hits"]
    
    return res
        

def get_authors_name(es, name):
    index_name = 'orcid_large'

    res = es.search(index=index_name, body={
        "query": {
            "bool": {
                "must": [
                    {
                        "bool": {
                            "should": [
                                {
                                    "match_phrase": {
                                        "record:record.person:person.researcher-url:researcher-urls.researcher-url:researcher-url.common:source.common:source-name": str(name)
                                    }
                                },
                                {
                                    "match_phrase": {
                                        "record:record.person:person.person:name.personal-details:credit-name": str(name)
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        },
        "_source": ["record:record.person:person", "record:record.common:orcid-identifier"]
    })
    
    res = res["hits"]["hits"]
    
    return res

def get_authors_orcid(es, orcid):
    index_name = 'orcid_large'
    
    res = es.search(index=index_name, body={
        "query": {
            "bool": {
                "should": [
                    {
                        "match_phrase": {
                           "record:record.common:orcid-identifier.common:path": str(orcid)
                        }
                    }
                ]
            }
        },
        "_source": ["record:record.person:person", "record:record.common:orcid-identifier"]
    })
    
    res = res["hits"]["hits"]

    return res

## GET AUTHORS IN AUTHORS

def get_authors_id(es, id):
    index_name = 'authors_large'
    res = es.search(index=index_name, body={
        "query": {
            "match": {
               "id": str(id)
            }
        }
    })

    res = res["hits"]["hits"]

    return res