# IMPORT

from elasticsearch import Elasticsearch, helpers

# REQUESTS ES


def get_articles_es(title, title_ord, abstract, abstract_ord, authors, keywords, keywords_ord, journal, year1, year2):
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
                            "match_phrase": {
                                "title": str(title_ord)
                            }
                        },
                        {
                            "match": {
                                "paperAbstract": str(abstract)
                            }
                        },
                        {
                            "match_phrase": {
                                "paperAbstract": str(abstract_ord)
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
                            "match_phrase": {
                                "entities": str(keywords_ord)
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
            "_source": ["title", "paperAbstract", "authors.name", "entities", "journalName", "year", "pmid", "doi"]
        })
    res = res['hits']['hits']

    return res


def get_article_es(id_art):
    es_host = 'elasticsearch'
    es = Elasticsearch(hosts=[es_host])
    index_name = 'articles_large'

    res = es.search(index=index_name, body={
        "query": {"match": {"id": str(id_art)}},
        "_source": ["title", "paperAbstract", "authors.name", "entities", "journalName", "year"]
    })
    res = res["hits"]["hits"]
    
    return res


def get_article_async(title, title_end):
    es_host = 'elasticsearch'
    es = Elasticsearch(hosts=[es_host])
    index_name = 'articles_large'
    '''
    res = es.search(index=index_name, body={
        "query":{
            "match_phrase": {
                "title" : {
                    "query" : title,
                    "analyzer" : "pattern"
                }
            }
        },
        "_source": ["title"]
    })
    '''

    res = es.search(index=index_name, body={
        "size": 5,
        "query": {
            "bool": {
                "should": [
                    {
                        "match":{
                            "title": title
                        }
                    }
                ],
                "must":[
                    {
                        "regexp": {
                            "title":{
                                "value": title_end+".*"
                            }
                        }
                    }
                ]
            }
        },
        "_source": ["journalVolume", "journalPages", "journalName", "authors.name", "title", "year"]
    })
    
    res = res["hits"]["hits"]

    return res


def add_list_perti(data, token):
    es_host = 'elasticsearch'
    es = Elasticsearch(hosts=[es_host])
    index_name = 'list_pertinence'

    action = {
        "_op_type": "update",
        "_index": index_name,
        "_id": token,
        "_source": {
            "script": {
                "inline": "if (!ctx._source.list_failed.contains(params.list)) "
                          "{ctx._source.list_failed = params.list}"
,
                "params": {
                    "list": data["list_failed"]
                }
            },
            "upsert": {
                "abstract": data["abstract"],
                "nb_suggestion": data["nb_suggestion"],
                "ratio": data["ratio"],
                "list_failed": data["list_failed"]
            }
        }
    }

    helpers.bulk(es, [action])

    #es.index(index=index_name, body=data)