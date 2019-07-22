# IMPORTS

from elasticsearch import Elasticsearch
import xmltodict
import json
import os

# CONSTS

# ES index name for articles
INDEX_NAME_ORC = 'orcid_large'
# ES index type for article
DOC_TYPE_ORC = 'orcid_large'

es = Elasticsearch(hosts=["localhost"])

# MAIN

k = 0

for filename in os.listdir("../corpus/000"):
    print(filename)
    with open("../corpus/000/"+filename, "r") as fd:
        doc = json.dumps(xmltodict.parse(fd.read()))
    es.index(index=INDEX_NAME_ORC, doc_type=DOC_TYPE_ORC, body=doc, id=k)
    k += 1
