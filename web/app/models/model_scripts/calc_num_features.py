# IMPORT

import pickle
import pandas as pd
from elasticsearch import Elasticsearch
from nltk import word_tokenize
from nltk import download
from nltk.corpus import stopwords
from gensim import corpora

# CONSTS

es_host = 'localhost:9200'
es = Elasticsearch(hosts=[es_host])
index_name = 'articles_large'

download('punkt')
download('stopwords')
stop_words = stopwords.words('english')

# FUNCTIONS


def get_abstracts(start, size):
    res = es.search(index=index_name, body={
        "query": {"match_all": {}},
        "from": start,
        "size": size,
        "_source": ["paperAbstract"]
    }, request_timeout=500)
    res = res['hits']['hits']

    df_temp = pd.DataFrame(res)
    return df_temp


def preprocess(text):

    text = text.lower()
    doc = word_tokenize(text)
    doc = [word for word in doc if word not in stop_words]
    doc = [word for word in doc if word.isalnum()]
    return doc


def get_dictionary(df):

    corpus = []
    for index, row in df.iterrows():
        corpus.append(preprocess(row["_source"]["paperAbstract"]))

    dictionary = corpora.Dictionary(corpus, prune_at=None)
    return dictionary


def update_dictionary(df, dictionary):
    corpus = []
    for index, row in df.iterrows():
        corpus.append(preprocess(row["_source"]["paperAbstract"]))
    dictionary.add_documents(corpus, prune_at=None)

    return dictionary


def main():

    dictionary = False
    size = 100000

    for i in range(0, 50):
        df = get_abstracts(i*size, size)

        if i == 0:
            dictionary = get_dictionary(df)
            print(i, len(dictionary), dictionary)

        else:
            dictionary = update_dictionary(df, dictionary)
            print(i, len(dictionary), dictionary)

    pickle.dump(dictionary, open("../saves_test/dictionary_num.p", "wb"))
    dictionary = pickle.load(open("../saves_test/dictionary.p", "rb"))

    print(dictionary)


if __name__ == '__main__':
    main()
