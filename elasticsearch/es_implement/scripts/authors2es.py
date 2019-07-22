# IMPORTS

from elasticsearch import helpers
import objectpath
import pandas as pd
import logging


# CONSTS

# LOG_FILENAME = 'l.log'
# logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG, filemode='w')
# logging.getLogger("requests").setLevel(logging.WARNING)

# MAIN


def authors2es(es, index_name_art, index_name_aut, doc_type_aut):

    data = es.search(index=index_name_art, body={
        "size": 1000,
        "query": {"match_all": {}},
        "_source": ["id", "title", "entities", "year", "authors", "journalName"]
    })

    json_tree = objectpath.Tree(data['hits'])
    df = pd.DataFrame.from_records(tuple(json_tree.execute('$..hits')))

    for source in df["_source"]:
        authors = source['authors']
        if "year" in source:
            year = str(source['year'])
        else:
            year = "-1"
        if source['journalName'] == "":
            journal = "-1"
        else:
            journal = source['journalName']
        for author in list(authors):
            if not dict(author)['ids']:
                final_ids = -1
            else:
                final_ids = int(dict(author)['ids'][0])
            if not source['entities']:
                source['entities'] = ["-1"]
            final_name = dict(author)['name']
            for line in source['entities']:
                entitie = [line, year, source['id']]
                action = {
                    "_op_type": "update",
                    "_index": index_name_aut,
                    "_type": doc_type_aut,
                    "_id": final_ids,
                    "_source": {
                        "script": {
                            "inline": "if (!ctx._source.entities.contains(params.ent)) "
                                      "{ctx._source.entities.add(params.ent)}"
                                        
                                      "if (!ctx._source.articles.contains(params.art)) "
                                      "{ctx._source.articles.add(params.art);"
                                      "if (params.jrnl != '-1')"
                                      "{ctx._source.journals.add(params.jrnl)}}",
                            "params": {
                                "ent": entitie,
                                "art": str(source['id']),
                                "jrnl": journal
                            }
                        },
                        "upsert": {
                            "auth_id": final_ids,
                            "name": final_name,
                            "entities": [entitie],
                            "articles": [str(source['id'])],
                            "journals": journal
                        }
                    }
                }

                helpers.bulk(es, [action])
