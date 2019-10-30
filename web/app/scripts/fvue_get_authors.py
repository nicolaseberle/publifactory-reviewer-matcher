# IMPORT

from elasticsearch import Elasticsearch

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

def get_authors_es_v2(name, keywords, article, affil):
    es_host = 'elasticsearch'
    es = Elasticsearch(hosts=[es_host])
    index_name = 'orcid_large'

    res = es.search(index=index_name, body={
        "explain": "true",
        "query": {
            "bool": {
                "should": [
                    {
                        "match": {
                            "record:record.person:person.researcher-url:researcher-urls.researcher-url:researcher-url.common:source.common:source-name": str(name)
                        }
                    },
                    {
                        "match": {
                            "record:record.person:person.keyword:keywords.keyword:keyword.keyword:content": str(keywords)
                        }
                    },
                    {
                        "match": {
                            "record:record.activities:activities-summary.activities:works.activities:group.work:work-summary.work:title.common:title": str(article)
                        }
                    },
                    {
                        "match": {
                            "record:record.activities:activities-summary.activities:employments.employment:employment-summary.employment:organization.common:name": str(affil)
                        }
                    }
                ]
            }
        },
        "_source": ["record:record.person:person.researcher-url:researcher-urls.researcher-url:researcher-url", "record:record.person:person.person:name", "record:record.person:person.email:emails.email:email.email:email", "record:record.activities:activities-summary", "record:record.person:person.external-identifier:external-identifiers", "record:record.person:person.keyword:keywords"]
    })

    res = res["hits"]["hits"]

    return res


def get_authors_by_id(doi):
    es_host = 'elasticsearch'
    es = Elasticsearch(hosts=[es_host])
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
        "_source": ["record:record.person:person.researcher-url:researcher-urls.researcher-url:researcher-url.common:source.common:source-name", "record:record.person:person.researcher-url:researcher-urls.researcher-url:researcher-url.common:source.common:source-orcid.common:path", "record:record.person:person.keyword:keywords"]
    })

    res = res["hits"]["hits"]
    
    return res


def get_author_es(orcid):
    es_host = 'elasticsearch'
    es = Elasticsearch(hosts=[es_host])
    index_name = 'orcid_large'

    res = es.search(index=index_name, body={
        "query": {
            "bool": {
                "should": [
                    {
                        "match_phrase": {
                            "record:record.person:person.person:name.@path": str(orcid)
                        }
                    }
                ]
            }
        }
    })
    res = res["hits"]["hits"]

    return res


def get_mail_id(id):
    es_host = 'elasticsearch'
    es = Elasticsearch(hosts=[es_host])
    index_name = 'authors_large'

    res = es.search(index=index_name, body={
        "query": {
            "match": {
               "id": str(id)
            }
        },
        "_source": ["mail"]
    })
    res = res["hits"]["hits"]

    return res


def update_mail(id, mail):
    es_host = 'elasticsearch'
    es = Elasticsearch(hosts=[es_host])
    index_name = 'authors_large'

    es.update(index=index_name, id=id, body={"doc": {"mail": mail}})

    res = es.search(index=index_name, body={
        "query": {
            "match": {
                "id": str(id)
            }
        },
        "_source": ["mail"]
    })
    res = res["hits"]["hits"]

    return res










