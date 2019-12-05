# IMPORTS

import gensim
import logging
from elasticsearch import Elasticsearch
from gensim.models import phrases, word2vec
import pandas as pd
from nltk.corpus import stopwords
from string import punctuation
from nltk import word_tokenize
import pickle

# CONST

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

ES_HOST = 'localhost'
ES_PORT = '9200'
INDEX_NAME = 'articles_large'
es = Elasticsearch(hosts=[ES_HOST])

# LOADING

res = es.search(index=INDEX_NAME, body={
    "query": {
        "bool": {
            "must": [
                {
                    "exists": {
                        "field": "fields"
                    }
                },
                {
                    "exists": {
                        "field": "sub_cat"
                    }
                },
                    {
                    "exists": {
                        "field": "entities"
                    }
                }
            ],
            "must_not": [
                {
                    "match": {
                        "fields": "-1"
                    }
                },
                {
                    "match": {
                        "sub_cat": "-1"
                    }
                }
            ]
        }
    },
    "size": 100000,
    "_source": ["sub_cat", "fields", "entities"]
}, request_timeout=100)
res = res['hits']['hits']

df_temp = pd.DataFrame(res)

df = pd.DataFrame(columns=['fields', 'sub_cat', 'keywords', 'text'])
df['fields'] = [x["fields"] for x in df_temp["_source"]]
df['sub_cat'] = [x["sub_cat"] for x in df_temp["_source"]]
df['keywords'] = [x["entities"] for x in df_temp["_source"]]

stop_words = set(stopwords.words('english'))

def preprocess_sentence(text):
    text = text.replace('/', ' / ')
    text = text.replace('.-', ' .- ')
    text = text.replace('.', ' . ')
    text = text.replace('\'', ' \' ')
    text = text.lower()

texts = []
for val in df_temp["_source"]:
    text = ""
    for keyword in val["entities"]:
        text += str(keyword) + " is in " + " ".join(val["fields"]) + " and " + " ".join(val["sub_cat"]) + ". "
    text = [token for token in word_tokenize(text) if token not in punctuation]
    texts.append(text)

df['text'] = texts

print(df)

# BIGRAMS

sentences = df.text.values
bigrams = phrases.Phrases(sentences)

# BUILD MODEL

model = word2vec.Word2Vec(bigrams[sentences], size=50, min_count=3, iter=20)

pickle.dump(model, open("w2v_bigram.pkl", 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
#model = pickle.load(open("w2v_bigram.pkl", "rb"))

vocab = list(model.wv.vocab)
print(len(vocab))