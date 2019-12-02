from sklearn import metrics
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
import pandas as pd
import re
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

import spacy
from spacy.matcher import PhraseMatcher
from fuzzywuzzy import fuzz

sns.set()

#Extraction automatique de Keywords d'un abstract


##load inputs
#input_df = pd.read_json('~/workspace/public_ml_models/multi_label_classification_understanding/data/abtractKeywords.json')
input_df = pd.read_csv('../w2v/abstract_fields_cat_key_500K.csv')
input_df = input_df[:1000]

print(input_df.columns)

df_x = input_df['abstract']
s_x = pd.Series(df_x, name="abstract")
df_x = s_x.to_frame()
print(df_x.head(10))


df_t = input_df['sub_cat']
s_t = pd.Series(df_t, name="sub_cat")

df_t = s_t.to_frame()
print(df_t.head(30))


df_y = input_df['keywords']
s_y = pd.Series(df_y, name="keywords")
df_y = s_y.to_frame()
print(s_y.isnull().sum())
print(df_y.head(10))

yt = []
ytt = []
for index, row in df_t.iterrows():
    r = [re.sub(' +', ' ',words).lstrip().replace(" ","_").replace(")","").replace("(","").lower() for words in row['sub_cat'].split(',')]
    ytt.append(len(r))
    for r_ in r:
        yt.append(r_)

df_tt = pd.Series(yt,name="sub_cat").to_frame()
df_ttt = pd.Series(ytt,name="nbSubCat").to_frame()
print(df_tt["sub_cat"].reset_index().groupby(["sub_cat"]).count().sort_values(by='index', ascending=False)[:10])
print(df_ttt.sort_values(by='nbSubCat', ascending=False)[:10])


#x = [[1,2,3],[3,3,2],[8,8,7],[3,7,1],[4,5,6]]
#y = [['bar','foo'],['bar'],['foo'],['foo','jump'],['bar','fox','jump']]

#mlb = MultiLabelBinarizer()
#y_enc = mlb.fit_transform(y)

#train_x, test_x, train_y, test_y = train_test_split(x, y_enc, test_size=0.25)

#clf = OneVsRestClassifier(SVC(probability=True))
#clf.fit(train_x, train_y)

#predictions = clf.predict(test_x)
#print(test_y)
#print(predictions)
#my_metrics = metrics.classification_report( test_y, predictions)
