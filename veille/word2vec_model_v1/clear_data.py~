# IMPORTS

import re
import pandas as pd
from time import time
from collections import defaultdict
import spacy
# Ne pas oublier d'installer le package 'en' : $ python3 -m spacy download en
import logging
logging.basicConfig(format="%(levelname)s - %(asctime)s: %(message)s", datefmt= '%H:%M:%S', level=logging.INFO)

# CLEANING / PREPROCCESING

df = pd.read_csv('data/simpsons_dataset.csv')
df = df.dropna().reset_index(drop=True)

nlp = spacy.load('en', disable=['ner', 'parser'])
# On desactive le 'Name Entity Recognition' pour gagner en vitesse

def cleaning(doc):
    txt = [token.lemma_ for token in doc if not token.is_stop]
    if len(txt) > 2:
        return ' '.join(txt)
# On choisi de mettre de côté les phrases de 1 ou 2 mots car le benefice apporté au train est trop faible

# Suppression des caratères non-alpha
brief_cleaning = (re.sub("[^A-Za-z']+", ' ', str(row)).lower() for row in df['spoken_words'])

# Augmenter la vitesse du clean
t = time()
txt = [cleaning(doc) for doc in nlp.pipe(brief_cleaning, batch_size=5000, n_threads=-1)]

df_clean = pd.DataFrame({'clean': txt})
df_clean = df_clean.dropna().drop_duplicates()
#print(df_clean.shape)

df_clean.to_csv('data/simpsons_clear.csv', sep=',', encoding='utf-8')



