# IMPORTS

import re
import pandas as pd
from time import time
from collections import defaultdict
import spacy
# Ne pas oublier d'installer le package 'en' : $ python3 -m spacy download en
import logging
logging.basicConfig(format="%(levelname)s - %(asctime)s: %(message)s", datefmt= '%H:%M:%S', level=logging.INFO)

# REQUESTS ES

import json
import requests
from elasticsearch import Elasticsearch

ES_HOST = 'localhost'
ES_PORT = '9200'

es = Elasticsearch(hosts = [ES_HOST])

INDEX_NAME = 'articles_sample'
DOC_TYPE = 'articles_sample'

uri = 'http://'+ES_HOST+':'+ES_PORT+'/'+INDEX_NAME+'/'
headers = {'Content-Type' : 'application/json'}

res = es.search(index=INDEX_NAME, body={"query": {"match_all": {}}, "_source": ["paperAbstract"]})
res = res['hits']['hits']

df = pd.DataFrame(res)

# CLEANING / PREPROCCESING

temp = []

for line in df['_source']:
    temp.append(line['paperAbstract'])

df = pd.DataFrame(temp, columns=["abstract"]) 
df = df[df.abstract != ""]

nlp = spacy.load('en', disable=['parser'])
# On desactive le 'Name Entity Recognition' pour gagner en vitesse

def cleaning(doc):
    txt = [token.lemma_ for token in doc if not token.is_stop]
    if len(txt) > 2:
        return ' '.join(txt)
# On choisi de mettre de côté les phrases de 1 ou 2 mots car le benefice apporté au train est trop faible

# Suppression des caratères non-alpha
brief_cleaning = (re.sub("[^A-Za-z0-9_]+", ' ', str(row)).lower() for row in df['abstract'])

# Augmenter la vitesse du clean
t = time()
txt = [cleaning(doc) for doc in nlp.pipe(brief_cleaning, batch_size=5000, n_threads=-1)]

df_clean = pd.DataFrame({'clean': txt})
df_clean = df_clean.dropna().drop_duplicates()
print(df_clean)

df_clean.to_csv('datas/sample_clear.csv', sep=',', encoding='utf-8')



