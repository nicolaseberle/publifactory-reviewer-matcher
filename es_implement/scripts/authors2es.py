# IMPORTS

from elasticsearch import Elasticsearch
from elasticsearch import helpers
import objectpath
import pandas as pd


# MAIN

def authors2es(es, es_host, index_name_art, index_name_aut, doc_type_aut):

    data = es.search(index=index_name_art, body={
        "size": 10,
        "query": {"match_all": {}},
        "_source": ["id", "title", "entities", "year", "authors"]
    })

    json_tree = objectpath.Tree(data['hits'])
    df = pd.DataFrame.from_records(tuple(json_tree.execute('$..hits')))
    final = pd.DataFrame(columns=["id", "name", "entities"])

    for source in df["_source"]:
        try:
            source['year']
        except KeyError:
            year = -1
        else:
            year = source['year']
        if source['entities'] == []:
            source['entities'] = ["-1"]
        entities = [(x, str(year), source['title']) for x in source['entities']]
        authors = source['authors']
        for author in list(authors):
            if dict(author)['ids'] == []:
                final_ids = -1
            else:
                final_ids = dict(author)['ids'][0]
            final_name = dict(author)['name']
            temp = False

            for index, row in final.iterrows():
                if final_name == row[1]:
                    row[2] += entities
                    temp = True

            if temp == False:
                final = final.append({'id': final_ids, 'name': final_name, 'entities': entities}, ignore_index=True)

    use_these_keys = ['id', 'name', 'entities']

    def filterKeys(document):
        return {key: document[key] for key in use_these_keys }

    es_client = Elasticsearch(hosts=[es_host], http_compress=True)

    def doc_generator(df):
        df_iter = df.iterrows()
        for index, document in df_iter:
            yield {
                    "_index": index_name_aut,
                    "_type": doc_type_aut,
                    "_id" : f"{document['id']}",
                    "_source": filterKeys(document),
                }
    helpers.bulk(es_client, doc_generator(final))
