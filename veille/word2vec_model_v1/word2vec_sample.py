# IMPORT

import re  # For preprocessing
import pandas as pd  # For data handling
from time import time  # To time our operations
from collections import defaultdict  # For word frequency
import spacy  # For preprocessing
import logging

# MAIN

df = pd.read_csv('datas/sample_clear.csv', index_col=0)

# BIGRAMS
# Détection des expressions communes dans une liste de phrases

from gensim.models.phrases import Phrases, Phraser

sent = [row.split() for row in df['clean']]
# Récupère une liste de mots

phrases = Phrases(sent, min_count=1, progress_per=1)
# Phrases take a list of list of words as input

bigram = Phraser(phrases)
# Phraser réduit la consommation de mémoire de Phrases

sentences = bigram[sent]
# Transforme le corpus avec la detection des expressions communes

#print('sent: ', sent)
#print('phrases: ', phrases)
#print('bigram: ', bigram)
#print('sentences: ', sentences)

#exit(0)
# MOST FREQUENT WORDS

word_freq = defaultdict(int)
for sent in sentences:
    for i in sent:
        word_freq[i] += 1

#print(sorted(word_freq, key=word_freq.get, reverse=True)[:10])

# TRAINING THE MODEL

import multiprocessing
from gensim.models import Word2Vec

## Word2Vec

cores = multiprocessing.cpu_count()
#print(cores)

w2v_model = Word2Vec(min_count=1,
                     window=2,
                     size=300,
                     sample=6e-5,
                     alpha=0.03,
                     min_alpha=0.0007,
                     negative=20,
                     workers=cores-4)
# Paramètrage du modèle (voir doc)

t = time()

w2v_model.build_vocab(sentences, progress_per=100)
# Build du modèle

print('Time to build vocab: {} mins'.format(round((time() - t) / 60, 2)))

## TRAINING

t = time()

w2v_model.train(sentences, total_examples=w2v_model.corpus_count, epochs=10, report_delay=1)
# Training du modèle, voir la doc pour les paramètres

print('Time to train model : {} mins'.format(round((time() - t) / 60, 2)))

w2v_model.init_sims(replace=True)

# TESTING

print(w2v_model.wv.most_similar(positive=["tumor"]))



