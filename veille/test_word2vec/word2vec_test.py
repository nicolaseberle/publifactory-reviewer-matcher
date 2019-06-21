# IMPORT

import re  # For preprocessing
import pandas as pd  # For data handling
from time import time  # To time our operations
from collections import defaultdict  # For word frequency
import spacy  # For preprocessing
import logging

# MAIN

df = pd.read_csv('data/simpsons_clear.csv')

# BIGRAMS
# Détection des expressions communes dans une liste de phrases

from gensim.models.phrases import Phrases, Phraser

sent = [row.split() for row in df['clean']]
# Récupère une liste de mots

phrases = Phrases(sent, min_count=30, progress_per=10000)
# Phrases take a list of list of words as input

bigram = Phraser(phrases)
# Phraser réduit la consommation de mémoire de Phrases

sentences = bigram[sent]
# Transforme le corpus avec la detection des expressions communes

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

w2v_model = Word2Vec(min_count=20,
                     window=2,
                     size=300,
                     sample=6e-5,
                     alpha=0.03,
                     min_alpha=0.0007,
                     negative=20,
                     workers=cores-4)
# Paramètrage du modèle (voir doc)

t = time()

w2v_model.build_vocab(sentences, progress_per=10000)
# Build du modèle

#print('Time to build vocab : {} mins'.format(round((time() - t) / 60, 2)))

## TRAINING
print(sent)

t = time()

w2v_model.train(sentences, total_examples=w2v_model.corpus_count, epochs=30, report_delay=1)
# Training du modèle, voir la doc pour les paramètres

#print('Time to train model : {} mins'.format(round((time() - t) / 60, 2)))

w2v_model.init_sims(replace=True)
# Si l'on ne compte pas modifier le modèle, sert à optimiser la mémoire

# EXPLORE THE MODEL

## MOST SIMILAR TO

#print(w2v_model.wv.most_similar(positive=["homer"]))
#print(w2v_model.wv.most_similar(positive=["homer_simpson"]))
#print(w2v_model.wv.most_similar(positive=["marge"]))
#print(w2v_model.wv.most_similar(positive=["bart"]))
#print(w2v_model.wv.most_similar(positive=["tavern"]))

## SIMILARITIES

#print(w2v_model.wv.similarity("maggie", 'baby'))
#print(w2v_model.wv.similarity('bart', 'milhouse'))
#print(w2v_model.wv.similarity('krusty', 'clown'))

## ODD-ONE-OUT

#print(w2v_model.wv.doesnt_match(['jimbo', 'milhouse', 'kearney']))
#print(w2v_model.wv.doesnt_match(["nelson", "bart", "milhouse"]))
# Better with tuples, not lists

## ANALOGY DIFFERENCE
# Quel mot est équivalent string1 comme string2 est pour string3 ?

#print(w2v_model.wv.most_similar(positive=["woman", "homer"], negative=["marge"], topn=3))
#print(w2v_model.wv.most_similar(positive=["woman", "bart"], negative=["man"], topn=3))

## t-SNE VISUALIZATION
# non-linear dimensionality reduction algorithm that attempts to represent high-dimensional data

import numpy as np
import matplotlib.pyplot as plt
from IPython import get_ipython
get_ipython().run_line_magic('matplotlib', 'inline')
 
import seaborn as sns
sns.set_style("darkgrid")

from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

def tsnescatterplot(model, word, list_names):
    arrays = np.empty((0, 300), dtype='f')
    word_labels = [word]
    color_list  = ['red']
    arrays = np.append(arrays, model.wv.__getitem__([word]), axis=0)
    close_words = model.wv.most_similar([word])
    for wrd_score in close_words:
        wrd_vector = model.wv.__getitem__([wrd_score[0]])
        word_labels.append(wrd_score[0])
        color_list.append('blue')
        arrays = np.append(arrays, wrd_vector, axis=0)
    for wrd in list_names:
        wrd_vector = model.wv.__getitem__([wrd])
        word_labels.append(wrd)
        color_list.append('green')
        arrays = np.append(arrays, wrd_vector, axis=0)
    reduc = PCA(n_components=50).fit_transform(arrays)
    np.set_printoptions(suppress=True)
    Y = TSNE(n_components=2, random_state=0, perplexity=15).fit_transform(reduc)
    df = pd.DataFrame({'x': [x for x in Y[:, 0]],
                       'y': [y for y in Y[:, 1]],
                       'words': word_labels,
                       'color': color_list})
    fig, _ = plt.subplots()
    fig.set_size_inches(9, 9)
    p1 = sns.regplot(data=df,
                     x="x",
                     y="y",
                     fit_reg=False,
                     marker="o",
                     scatter_kws={'s': 40,
                                  'facecolors': df['color']
                                 }
                    )
    for line in range(0, df.shape[0]):
         p1.text(df["x"][line],
                 df['y'][line],
                 '  ' + df["words"][line].title(),
                 horizontalalignment='left',
                 verticalalignment='bottom', size='medium',
                 color=df['color'][line],
                 weight='normal'
                ).set_size(15)
    plt.xlim(Y[:, 0].min()-50, Y[:, 0].max()+50)
    plt.ylim(Y[:, 1].min()-50, Y[:, 1].max()+50)
            
    plt.title('t-SNE visualization for {}'.format(word.title()))

tsnescatterplot(w2v_model, 'homer', ['dog', 'bird', 'ah', 'maude', 'bob', 'mel', 'apu', 'duff'])







