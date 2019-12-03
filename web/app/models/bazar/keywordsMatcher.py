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
input_df = pd.read_json('~/workspace/public_ml_models/multi_label_classification_understanding/data/abtractKeywords.json')
input_df = input_df[:100000]


df_x = input_df['abstract']
s_x = pd.Series(df_x, name="abstract")
df_x = s_x.to_frame()
print(df_x.head(10))



df_y = input_df['keywords'].apply(','.join)
s_y = pd.Series(df_y, name="keywords")
df_y = s_y.to_frame()
print(df_y.head(10))

yt = []
ytt = []
for index, row in df_y.iterrows():
    r = [re.sub(' +', ' ',words).lstrip().replace(" ","_").replace(")","").replace("(","").lower() for words in row['keywords'].split(',')]
    ytt.append(len(r))
    for r_ in r:
        yt.append(r_)

df_yt = pd.Series(yt,name="keywords").to_frame()
df_ytt = pd.Series(ytt,name="nbKeywords").to_frame()
print(df_yt["keywords"].reset_index().groupby(["keywords"]).count().sort_values(by='index', ascending=False)[:10])
print(df_ytt.sort_values(by='nbKeywords', ascending=False)[:10])



all_text = 'Packet-switching characteristics of an integrated 4 /spl times/ 4 InGaAsP-InP active vertical coupler optical cross-point switch matrix are optimized. Optical gain differences of less then 3 dB between the shortest and longest switching paths are achieved. Bit-error rate (BER) and power penalty measurements during packet routing have been carried out over the entire 4 /spl times/ 4 matrix. At 10-Gb/s packet data rate less than 1-dB power penalty is found across the switch matrix, and the possibility for error-free packet routing is demonstrated with no BER floor observed.'
#full_funds_list_flat = yt

keyword_list = yt

if any(word in all_text for word in keyword_list):
    print('found one of em',word)


#nlp = spacy.load('en_core_web_sm')
#keyword_patterns = [nlp(text) for text in full_funds_list_flat]
#matcher = PhraseMatcher(nlp.vocab)
#matcher.add('KEYWORD', None, *keyword_patterns)


#sns.scatterplot(linewidth=0,data=df_yt["keywords"].reset_index().groupby(["keywords"]).count().sort_values(by='index', #ascending=False).values)

#plt.show()


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