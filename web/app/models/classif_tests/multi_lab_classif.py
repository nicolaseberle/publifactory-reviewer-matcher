# IMPORTS

import pandas as pd
import numpy as np
import re
import pickle


from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.preprocessing import MultiLabelBinarizer

from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.metrics import hamming_loss

from sklearn.model_selection import train_test_split

import gensim.parsing.preprocessing as gsp


from ast import literal_eval

# FUNCTIONS

filters = [
           gsp.strip_tags,
           gsp.strip_punctuation,
           gsp.strip_multiple_whitespaces,
           gsp.strip_numeric,
           gsp.remove_stopwords,
           #gsp.strip_short()
           #gsp.stem_text
          ]

def strip_html_tags(body):
    body = str(body)
    for f in filters:
        body = f(body)
    body = body.lower()
    return body


def hamming_score(y_true, y_pred, normalize=True, sample_weight=None):
    acc_list = []
    for i in range(y_true.shape[0]):
        set_true = set( np.where(y_true[i])[0] )
        set_pred = set( np.where(y_pred[i])[0] )
        tmp_a = None
        if len(set_true) == 0 and len(set_pred) == 0:
            tmp_a = 1
        else:
            tmp_a = len(set_true.intersection(set_pred))/float(len(set_true.union(set_pred)) )
        acc_list.append(tmp_a)
    return np.mean(acc_list)


def print_score(y_pred, clf):
    print("Clf: ", clf.__class__.__name__)
    print("Hamming loss: {}".format(hamming_loss(y_pred, y_test_tfidf)))
    print("Hamming score: {}".format(hamming_score(y_pred, y_test_tfidf)))
    print("---")

# LOADING & CLEANING

print("open json")
input_df = pd.read_csv('../w2v/abstract_fields_subcat_200K.csv')
#input_df = input_df[:20000]

input_df['abstract'] = input_df['abstract'].apply(strip_html_tags)
input_df['fields2'] = input_df['fields']
input_df['fields'] = [x.replace('_', '') for x in input_df['fields']]
input_df['fields'] = [literal_eval(x) for x in input_df['fields']]

print(input_df.head(10))

print("tf-idf")

multilabel_binarizer = MultiLabelBinarizer()
multilabel_binarizer.fit(input_df.fields)
Y = multilabel_binarizer.transform(input_df.fields)

count_vect = CountVectorizer()
count_vect.fit(input_df.abstract)
X_counts = count_vect.transform(input_df.abstract)

tfidf_transformer = TfidfTransformer()
X_tfidf = tfidf_transformer.fit_transform(X_counts)

x_train_tfidf, x_test_tfidf, y_train_tfidf, y_test_tfidf = train_test_split(X_tfidf, Y, test_size=0.1, random_state=0)

nb_clf = MultinomialNB()
sgd = SGDClassifier(loss='hinge', penalty='l2', alpha=1e-3, random_state=42, max_iter=6, tol=None)
lr = LogisticRegression()
mn = MultinomialNB()

i = 0
names = ["SGDClassifier", "LogisticRegression", "MultinomialNB"]

for classifier in [sgd, lr, mn]:
#for classifier in [lr]:
    clf = OneVsRestClassifier(classifier)
    clf.fit(x_train_tfidf, y_train_tfidf)
    y_pred = clf.predict(x_test_tfidf)
    print_score(y_pred, classifier)
    pickle.dump(clf, open("models_saves/"+names[i]+".pkl", 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
    i += 1


pickle.dump(count_vect, open("models_saves/count_vect.pkl", 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
pickle.dump(multilabel_binarizer, open("models_saves/multilabel_binarizer.pkl", 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
pickle.dump(tfidf_transformer, open("models_saves/tfidf_transformer.pkl", 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
