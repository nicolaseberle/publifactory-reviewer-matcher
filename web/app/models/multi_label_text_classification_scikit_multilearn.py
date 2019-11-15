#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt 

from gensim import utils
import gensim.parsing.preprocessing as gsp

from sklearn.preprocessing import MultiLabelBinarizer
from gensim.models.doc2vec import TaggedDocument, Doc2Vec
from sklearn.base import BaseEstimator
from sklearn import utils as skl_utils
from tqdm import tqdm


from skmultilearn.problem_transform import ClassifierChain
from sklearn.model_selection import train_test_split
from sklearn.pipeline import FeatureUnion


from sklearn.pipeline import Pipeline
from skmultilearn.problem_transform import BinaryRelevance
from sklearn.ensemble import RandomForestClassifier

import sklearn.metrics as metrics
from sklearn.metrics import roc_curve, auc

import multiprocessing
import numpy as np
import re
import pickle
import ast
from sklearn.externals import joblib

from sklearn.linear_model import RidgeClassifier

print("open json")
input_df = pd.read_csv('w2v/abstract_fields.csv')
input_df = input_df

## Data Exploration and Visualization

# total_df = pd.merge(questions_df,tag_df, on='Id', how='inner')
#concat_tag_df = total_df.groupby(['Id'])['Tag'].apply(','.join).reset_index()
#input_df = pd.merge(questions_df, concat_tag_df, on='Id', how='inner')[['Title','Body','Tag']]
#input_df.head()

#tags_count_df = tag_df.groupby(['Tag']).count()
#tags_count_df_asc = tags_count_df.sort_values(by=['Id'])
#tags_count_df_asc.query('Id >= 3').tail()

#tags_count_df_desc = tags_count_df.sort_values(by=['Id'], ascending=False)
#tags_count_df_desc.head()

#get_ipython().run_line_magic('matplotlib', 'inline')


def plot_word_cloud(text):
    wordcloud_instance = WordCloud(width = 800, height = 800, 
                background_color ='black', 
                stopwords=None,
                min_font_size = 10).generate(text) 
             
    plt.figure(figsize = (8, 8), facecolor = None) 
    plt.imshow(wordcloud_instance) 
    plt.axis("off") 
    plt.tight_layout(pad = 0) 
    plt.show() 


filters = [
           gsp.strip_tags, 
           gsp.strip_punctuation,
           gsp.strip_multiple_whitespaces,
           gsp.strip_numeric,
           gsp.remove_stopwords, 
           gsp.strip_short, 
           gsp.stem_text
          ]

def clean_text(s):
    s = s.lower()
    s = utils.to_unicode(s)
    for f in filters:
        s = f(s)
    return s

#input_df.iloc[0,0]
#clean_text(input_df.iloc[0,0])
#input_df.iloc[0,1]
#clean_text(input_df.iloc[0,1])


df_x = input_df['abstract']
s_x = pd.Series(df_x, name="abstract")
df_x = s_x.to_frame()

input_df['fields'] = [ast.literal_eval(x) for x in input_df['fields']]

df_y = input_df['fields'].apply(','.join)
s_y = pd.Series(df_y, name="fields")
df_y = s_y.to_frame()

## STATISTIC ANALYSIS

yt = []
ytt = []
for index, row in df_y.iterrows():
    r = [words for words in row['fields'].split(',')]
    ytt.append(len(r))
    for r_ in r:
        yt.append(r_)

df_yt = pd.Series(yt,name="fields").to_frame()
df_ytt = pd.Series(ytt,name="nbFields").to_frame()
print(df_yt["fields"].reset_index().groupby(["fields"]).count().sort_values(by='index', ascending=False))
print(df_ytt.sort_values(by='nbFields', ascending=False))


## Building the ML model & Pipeline

y = []
for index, row in df_y.iterrows():
    r = [words for words in row['fields'].split(',')]
    y.append(set(r))

mlb = MultiLabelBinarizer(sparse_output=True)
print("nb of keywords to binarize",len(y))
encoded_y = mlb.fit_transform(y)

class Doc2VecTransformer(BaseEstimator):

    def __init__(self, vector_size=100, learning_rate=0.02, epochs=20, field=None):
        self.learning_rate = learning_rate
        self.epochs = epochs
        self._model = None
        self.vector_size = vector_size
        self.workers = multiprocessing.cpu_count() - 1
        self.field = field

    def fit(self, df_x, df_y=None):
        tagged_x = [TaggedDocument(clean_text(row[str(self.field)]).split(), [index]) for index, row in df_x.iterrows()]
        model = Doc2Vec(documents=tagged_x, vector_size=self.vector_size, workers=self.workers)

        for epoch in range(self.epochs):
            model.train(skl_utils.shuffle([x for x in tqdm(tagged_x)]), total_examples=len(tagged_x), epochs=1)
            model.alpha -= self.learning_rate
            model.min_alpha = model.alpha

        self._model = model
        return self

    def save(self):
        filename = 'w2v/finalized_random_forest_model.sav'
        pickle.dump(self._model, open(filename, 'wb'))
        
    def load(self):
        filename = 'w2v/finalized_random_forest_model.sav'
        self._model = pickle.load(open(filename, 'rb'))
        
    def transform(self, df_x):
        return np.asmatrix(np.array([self._model.infer_vector(clean_text(row[str(self.field)]).split())
                                     for index, row in df_x.iterrows()]))

print("train_test_split")
train_x, test_x, train_y, test_y = train_test_split(df_x, encoded_y)
print("nb train samples: ",len(train_x))
print("nb test samples: ",len(test_x))

fu = FeatureUnion(transformer_list=[('abstract_doc2vec',Doc2VecTransformer(field='abstract'))])

#binary_rel_model = BinaryRelevance(RandomForestClassifier(verbose=1,n_jobs=-1))
binary_rel_model = BinaryRelevance(RidgeClassifier(tol=1e-2, solver="sag"))
multi_label_rf_br_model = Pipeline(steps=[
                           ('feature_union', fu),
                           ('binary_relevance', binary_rel_model)
                        ])

def hamming_loss(multi_label_model_pipeline,train_x, train_y, test_x, test_y):
    predictions_test_y = multi_label_model_pipeline.predict(test_x)
    return metrics.hamming_loss(y_true=test_y, y_pred=predictions_test_y)

print("multi_label_rf_br_model")
multi_label_rf_br_model.fit(train_x, train_y)

#Save the model
joblib.dump(multi_label_rf_br_model, 'w2v/model_classif_abstract2fields.joblib')

print("test data")
print('Hamming loss for test data :', hamming_loss(multi_label_rf_br_model,train_x,train_y,test_x,test_y))
