#!/usr/bin/env python
# coding: utf-8

import time
#basic imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import nltk

#word modeling
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.preprocessing import MultiLabelBinarizer

from sklearn.metrics import hamming_loss

from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.manifold import TSNE
from sklearn.linear_model import LogisticRegression
import gensim.parsing.preprocessing as gsp
from ast import literal_eval
from sklearn.neural_network import MLPClassifier
from sklearn.multiclass import OneVsRestClassifier
import warnings
import re

warnings.filterwarnings("ignore",category=DeprecationWarning)
warnings.filterwarnings('ignore',message="Precision")


#load data
filters = [
           gsp.strip_tags,
           gsp.strip_punctuation,
           gsp.strip_multiple_whitespaces,
           gsp.strip_numeric,
           gsp.remove_stopwords,
           #gsp.strip_short,
           #gsp.stem_text
          ]

def clean_text(text):
    text = text.lower()
    text = re.sub(r"what's", "what is ", text)
    text = re.sub(r"\'s", " ", text)
    text = re.sub(r"\'ve", " have ", text)
    text = re.sub(r"can't", "can not ", text)
    text = re.sub(r"n't", " not ", text)
    text = re.sub(r"i'm", "i am ", text)
    text = re.sub(r"\'re", " are ", text)
    text = re.sub(r"\'d", " would ", text)
    text = re.sub(r"\'ll", " will ", text)
    text = re.sub(r"\'scuse", " excuse ", text)
    text = re.sub('\W', ' ', text)
    text = re.sub('\s+', ' ', text)
    text = text.strip(' ')
    return text

def strip_html_tags(body):
    body = str(body)
    for f in filters:
        body = f(body)
    #body = clean_text(body)
    return body


lectures = pd.read_csv('../w2v/abstract_fields_cat_key_500K.csv')
lectures = lectures[:50000]

lectures['abstract'] = lectures['abstract'].apply(strip_html_tags)
lectures['fields'] = [x.replace('_', '') for x in lectures['fields']]
lectures['fields'] = [literal_eval(x) for x in lectures['fields']]
lectures['keywords'] = [literal_eval(x) for x in lectures['keywords']]

print(lectures.head(10))


yt = []
ytt = []
df_t = lectures['fields']
for index, row in lectures['fields'].to_frame().iterrows():
    r = [re.sub(' +', ' ',words).lstrip().replace(" ","_").replace(")","").replace("(","").lower() for words in row['fields']]
    ytt.append(len(r))
    for r_ in r:
        yt.append(r_)
        
df_tt = pd.Series(yt,name="fields").to_frame()
categories = df_tt["fields"].reset_index().groupby(["fields"]).count().sort_values(by='index', ascending=False)


df_stats = pd.DataFrame(categories)
print(df_stats.index.unique())
df_stats.plot( kind='bar', legend=False, grid=True, figsize=(8, 5))
plt.title("Number of articles per category")
plt.ylabel('# of Occurrences', fontsize=12)
plt.xlabel('fields', fontsize=12)


#Split the df for training and testing
train, test = train_test_split(lectures.reset_index(drop=True), test_size=.10, random_state=43)
sample_test = lectures.iloc[lectures.index==971]
print(sample_test)
#The Doc2Vec model takes 'tagged_documents'
#tag the training data
tagged_tr = [TaggedDocument(words=nltk.word_tokenize(str(_d)),tags=[str(i)]) for i, _d in enumerate(train.abstract)]

#tag testing data
tagged_test = [TaggedDocument(words=nltk.word_tokenize(str(_d)),tags=[str(i)]) for i, _d in enumerate(test.abstract)]

#Instantiate the model

model = Doc2Vec(vector_size=500, # 100 should be fine based on the standards
                window=5, #change to 8
                alpha=.025, #initial learning rate
                min_alpha=0.00025, #learning rate drops linearly to this
                min_count=2, #ignores all words with total frequency lower than this.
                dm =1, #algorith 1=distributed memory
                workers=32)#cores to use

#build the vocab on the training data
model.build_vocab(tagged_tr)

#max training epochs
max_epochs = 100

#train n epochs and save the model
t1 = time.time()


for epoch in range(max_epochs):
    print('iteration {0}'.format(epoch+1))
    model.train(tagged_tr,
                total_examples=model.corpus_count,
                epochs=model.epochs)
    # decrease the learning rate
    model.alpha -= 0.0002
    # fix the learning rate, no decay
    model.min_alpha = model.alpha
    
   

print("done!")
t2 = time.time()    
model.save("5klects1.model")
print("Model Saved")
print("Time: {}".format(t2-t1))


#Now that we have the embedding trained, we can use the infer vector method to convert the test sentences into vectors
#that can be used to model 

# Extract vectors from doc2vec model
X_train = np.array([model.docvecs[str(i)] for i in range(len(tagged_tr))])
y_train = train.fields


# Extract test values
X_test = np.array([model.infer_vector(tagged_test[i][0]) for i in range(len(tagged_test))])
y_test = test.fields


multilabel_binarizer = MultiLabelBinarizer()
multilabel_binarizer.fit(lectures.fields)
y_train = multilabel_binarizer.transform(y_train)
y_test = multilabel_binarizer.transform(y_test)

print(y_train.shape)

def hamming_score(y_true, y_pred, normalize=True, sample_weight=None):
    acc_list = []
    for i in range(y_true.shape[0]):
        set_true = set(np.where(y_true[i])[0])
        set_pred = set(np.where(y_pred[i])[0])
        tmp_a = None
        if len(set_true) == 0 and len(set_pred) == 0:
            tmp_a = 1
        else:
            tmp_a = len(set_true.intersection(set_pred))/float(len(set_true.union(set_pred)) )
            acc_list.append(tmp_a)
    return np.mean(acc_list)

def print_score(y_pred, clf):
    print("Clf: ", clf.__class__.__name__)
    print("Hamming loss: {}".format(hamming_loss(y_pred, y_test)))
    print("Hamming score: {}".format(hamming_score(y_pred, y_test)))
    print("---")

tagged_test_ = [TaggedDocument(words=nltk.word_tokenize(str(_d)),tags=[str(i)]) for i, _d in enumerate(sample_test.abstract)]

# Extract test values
X_test_sample = np.array([model.infer_vector(tagged_test_[i][0]) for i in range(len(tagged_test_))])
y_test_ = sample_test.fields
#print(X_test_sample[0])


clf = MLPClassifier(solver='lbfgs', alpha=1e-5,hidden_layer_sizes=(500, 500), random_state=1)
lrc = LogisticRegression(C=5, multi_class='multinomial', solver='saga',max_iter=1000)
for classifier in [clf]:
    current_classifier = OneVsRestClassifier(classifier)
    y_pred = current_classifier.fit(X_train, y_train)
    y_pred = current_classifier.predict(X_test)
    print_score(y_pred, classifier)

def heatconmat(y_test,y_pred):
    sns.set_context('talk')
    plt.figure(figsize=(9,6))
    
    sns.heatmap(confusion_matrix(y_test.argmax(axis=1),y_pred.argmax(axis=1)),
                annot=True,
                fmt='d',
                cbar=False,
                cmap='gist_earth_r')
    plt.show()
    print(classification_report(y_test,y_pred))


heatconmat(y_test,y_pred)


