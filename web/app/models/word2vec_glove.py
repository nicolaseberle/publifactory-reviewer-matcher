# IMPORTS

from gensim.models import KeyedVectors
from gensim.test.utils import datapath, get_tmpfile
from gensim.scripts.glove2word2vec import glove2word2vec

import pickle
import statistics
import operator
from wikipedia2vec import Wikipedia2Vec
import gensim
import numpy as np
import pandas as pd


# MAIN

with open("w2v/glove.840B.300d.txt", "r+", errors='ignore', encoding='utf8') as f:
    lines = f.readlines()
    f.seek(0)
    for line in lines:
        val = line.split()
        unique_types = set([type(i) for i in list(val[1:])])
        if len(unique_types) == 1:
            f.write(line)
    f.truncate()

glove_file = 'w2v/glove.840B.300d.txt'
tmp_file = "w2v/glove_word2vec.txt"
_ = glove2word2vec(glove_file, tmp_file)
model = KeyedVectors.load_word2vec_format(tmp_file)
pickle.dump(model, open("w2v/glove_test_2.pkl", "wb"), protocol=pickle.HIGHEST_PROTOCOL)
#model = pickle.load(open("w2v/glove_test_2.pkl", "rb"))

print("Model Load")

fields_list = [
    "Art",
    "Biology",
    "Business",
    "Computer",
    "Chemistry",
    "Economics",
    "Engineering",
    "Environmental",
    "Geography",
    "Geology",
    "History",
    "Materials",
    "Mathematics",
    "Medicine",
    "Philosophy",
    "Physics",
    "Political",
    "Psychology",
    "Sociology"
]

keywords_list = [
    "processing",
    "images",
    "algorithm",
    "learning",
    "network",
    "cryptographic"
]

'''
    "aging",
    "protein",
    "autophagy",
    "body",
    "disorder",
    "Intestinal",
    "Organism",
    "Regulation",
    "Physiology",
'''

temp = []

for x in range(0, len(keywords_list)):
    temp.append(model.wv.most_similar_to_given(keywords_list[x].lower(), [x.lower() for x in fields_list]))

print(temp)

# print(model.wv.most_similar_to_given('autophagy', [x.lower() for x in fields_list]))

# print(model.wv.n_similarity([x.lower() for x in keywords_list], [x.lower() for x in fields_list]))

# print(model.wv.closer_than('Scarlett Johansson', 'star'))