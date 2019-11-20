# IMPORTS

from elasticsearch import Elasticsearch
import pandas as pd
import ast


# CONSTS

es_host = 'localhost:9200'
es = Elasticsearch(hosts=[es_host])
index_name = 'articles_large'

journal_classif = pd.read_csv("../models/w2v/journal_classif.csv")

# MAIN


def add_cats(size):
    data = es.search(index=index_name, request_timeout=600, body={
        "size": size,
        "query": {
            "bool": {
                "must_not": {
                    "exists": {
                        "field": "fields"
                    }
                }
            }
        },
        "_source": ["id", "title", "journalName"],
    })

    data = data["hits"]["hits"]

    journal_classif['Title'] = [x.lower() for x in journal_classif['Title']]
    journal_classif['Categories'] = [x.lower() for x in journal_classif['Categories']]

    for val in data:
        sub_cat = []
        fields = []
        if val["_source"]["journalName"]:

            # Checking if the journal contain "&"
            if "&" in val["_source"]["journalName"]:
                val["_source"]["journalName"] = val["_source"]["journalName"].replace('&', 'and')

            # Checking if the journal have " :"
            if " :" in val["_source"]["journalName"]:
                val["_source"]["journalName"] = val["_source"]["journalName"].split(' :')[0]

            # Checking if the journal start with "j."
            test = val["_source"]["journalName"].split()
            if test[0].lower() == "j.":
                test[0] = "Journal of"
                val["_source"]["journalName"] = ' '.join(test)

            if val["_source"]["journalName"].lower() in journal_classif['Title'].tolist():
                sub_cat = journal_classif[journal_classif["Title"] == val["_source"]["journalName"].lower()]["Categories"].values[0]
                fields = journal_classif[journal_classif["Title"] == val["_source"]["journalName"].lower()]["Fields"].values[0]

            else:
                # Checking if the journal start with "the"
                test = val["_source"]["journalName"].split()
                if test[0].lower() == "the":
                    test.pop(0)
                    val["_source"]["journalName"] = ' '.join(test)
                    if val["_source"]["journalName"].lower() in journal_classif['Title'].tolist():
                        sub_cat = journal_classif[journal_classif["Title"] == val["_source"]["journalName"].lower()]["Categories"].values[0]
                        fields = journal_classif[journal_classif["Title"] == val["_source"]["journalName"].lower()]["Fields"].values[0]

        if type(sub_cat) == type('str'):
            sub_cat = ast.literal_eval(sub_cat)
        if type(fields) == type('str'):
            fields = ast.literal_eval(fields)

        if sub_cat == []:
            sub_cat = [-1]
        if fields == []:
            fields = [-1]

        #print(val["_id"], sub_cat)

        es.update(index=index_name, id=val["_id"], body={
            "script": {
                "source": "ctx._source.fields = params.fields; ctx._source.sub_cat = params.sub",
                "lang": "painless",
                "params": {
                    "fields": fields,
                    "sub": sub_cat
                }
            }
        })


size = 100000
for x in range(0, 1):
    add_cats(size)
