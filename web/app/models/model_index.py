# IMPORTS

from elasticsearch import Elasticsearch
from elasticsearch import helpers
import pickle
from joblib import Parallel, delayed
from index_scripts.requestsES import get_abstracts

ES_HOST = 'localhost'
ES_PORT = '9200'

es = Elasticsearch(hosts=[ES_HOST])

# FUNCTIONS

def authors2es(source):
    print(type(source))
    authors = source["authors"]
    if "year" in source:
        year = str(source['year'])
    else:
        year = -1
    citations = len(source["inCitations"])
    keywords = source["entities"]
    if source["fields"]:
        if source["fields"] != [-1]:
            fields = source["fields"]
        else:
            fields = []
    else:
        fields = []
    if source["sub_cat"]:
        if source["sub_cat"] != [-1]:
            sub_cat = source["sub_cat"]
        else:
            sub_cat = []
    else:
        sub_cat = []
    i = 0
    final_conflit = []
    for auth in list(authors):
        if dict(auth)['ids']:
            final_auth = {
                "auth_id": str(dict(auth)['ids'][0]),
                "auth_name": str(dict(auth)['name']),
                "auth_year": int(year),
                "auth_iter": 1
            }
            final_conflit.append(final_auth)
    for author in list(authors):
        if i == 0:
            status = "Author"
        else:
            status = "Co-author"
        final_keys = []
        for keyword in list(keywords):
            final_key = {
                "key_name": str(keyword),
                "key_year": int(year),
                "key_role": status,
                "key_score": 1
            }
            final_keys.append(final_key)
        final_fields = []
        for field in list(fields):
            final_field = {
                "field_name": str(field),
                "field_score": 1
            }
            final_fields.append(final_field)
        final_sub_cat = []
        for cat in list(sub_cat):
            final_cat = {
                "sub_cat_name": str(cat),
                "sub_cat_score": 1
            }
            final_sub_cat.append(final_cat)
        if dict(author)['ids']:
            final_ids = int(dict(author)['ids'][0])
            #print("id ::", final_ids)
            final_name = dict(author)['name']
            action = {
                "_op_type": "update",
                "_index": "authors_total",
                "_id": final_ids,
                "_source": {
                    "script": {
                        "inline": "if (ctx._source.citations != null)"
                                  "{ctx._source.citations += params.cits}"
                                  "else {ctx._source.citations = params.cits}"
                                  ""
                                  "for (key in params.keys){"
                                    "def temp = 0;"
                                    "for (key2 in ctx._source.keywords){"
                                        "if (key.key_name == key2.key_name){"
                                            "key2.key_score += 1; temp = 1;"
                                            "if (key.key_year > key2.key_year)"
                                                "{key2.key_year = key.key_year}"
                                            "if (key.key_role == 'Author' && key2.key_role == 'Co-author')"
                                                "{key2.key_role = key.key_role}"
                                        "}"
                                    "}"
                                    "if (temp == 0){ctx._source.keywords.add(key)}"
                                  "}"
                                  ""
                                  "for (fie in params.fie){"
                                    "def temp2 = 0;"
                                    "for (fie2 in ctx._source.fields){"
                                        "if (fie.field_name == fie2.field_name){"
                                            "fie2.field_score += 1; temp2 = 1;"
                                        "}"
                                    "}"
                                    "if (temp2 == 0){ctx._source.fields.add(fie)}"
                                  "}"
                                  ""
                                  "for (cat in params.cats){"
                                    "def temp3 = 0;"
                                    "for (cat2 in ctx._source.sub_cat){"
                                        "if (cat.sub_cat_name == cat2.sub_cat_name){"
                                            "cat2.sub_cat_score += 1; temp3 = 1;"
                                        "}"
                                    "}"
                                    "if (temp3 == 0){ctx._source.sub_cat.add(cat)}"
                                  "}"
                                  ""
                                  "for (auth in params.conf){"
                                    "def test = 0;"
                                    "for (auth2 in ctx._source.auth_conflit){"
                                        "if (auth.auth_id == auth2.auth_id){"
                                            "auth2.auth_iter += 1; test = 1;"
                                            "if (auth.auth_year > auth2.auth_year)"
                                                "{auth2.auth_year = auth.auth_year}"
                                        "}"
                                    "}"
                                  "}",
                        "params": {
                            "cits": citations,
                            "keys": final_keys,
                            "fie": final_fields,
                            "cats": final_sub_cat,
                            "conf": final_conflit
                        }
                    },
                    "upsert": {
                        "id": str(final_ids),
                        "name": str(final_name),
                        "mail": '',
                        "citations": citations,
                        "keywords": final_keys,
                        "fields": final_fields,
                        "sub_cat": final_sub_cat,
                        "auth_conflit": final_conflit
                    }
                }
            }
            #try:
            helpers.bulk(es, [action])
            #except:
            #    continue
        i += 1


# GET ABSTRACTS

for i in range(0, 100):
    print("iter ::", i)

    start = pickle.load(open("saves_index/start2.pkl", "rb"))

    df = get_abstracts(es, start, 100000)

    Parallel(n_jobs=62, prefer="threads")(delayed(authors2es)(source) for source in df["_source"])