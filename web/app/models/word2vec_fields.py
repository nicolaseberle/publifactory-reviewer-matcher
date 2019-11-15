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

import re
from nltk import download
from nltk.corpus import stopwords

# MAIN

download('stopwords')
stop_words = stopwords.words('english')

#df = pd.read_csv('glove.840B.300d.txt', sep=" ", quoting=3, header=None, index_col=0)
#glove = {key: val.values for key, val in df.T.items()}

'''embeddings_dict = {}

with open("w2v/glove.840B.300d.txt", 'r', errors='ignore', encoding='utf8') as f:
    for index, line in enumerate(f):
        values = line.split()
        word = values[0]
        vector = np.genfromtxt(np.array(values[1:]))
        embeddings_dict[word] = vector

pickle.dump(embeddings_dict, open("w2v/glove_test.pkl", "wb"), protocol=pickle.HIGHEST_PROTOCOL)
embeddings_dict = pickle.load(open("w2v/glove_test.pkl", "rb"))

def find_closest_embeddings(embedding):
    return sorted(embeddings_dict.keys(), key=lambda word: spatial.distance.euclidean(embeddings_dict[word], embedding))


print(find_closest_embeddings(embeddings_dict["king"])[:5])
'''

glove_file = 'w2v/glove.42B.300d.txt'
tmp_file = "w2v/test_word2vec.txt"
# _ = glove2word2vec(glove_file, tmp_file)
# model = KeyedVectors.load_word2vec_format(tmp_file)
# pickle.dump(model, open("w2v/glove_test.pkl", "wb"), protocol=pickle.HIGHEST_PROTOCOL)
model = pickle.load(open("w2v/glove_test_2.pkl", "rb"))

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
"Exosomes",
"Integrins",
"liver metastases",
"Neoplasms",
"lung metastases",
"Proteomics",
"Bone Tissue",
"Structure of parenchyma of lung"
]

keywords_list_temp = []

for val in keywords_list:
    for word in val.split(","):
        keywords_list_temp.append(word)

keywords_list_temp = [re.sub(r'([^\s\w-]|_)+', '', x) for x in keywords_list_temp]
keywords_list = []

for val in keywords_list_temp:
    if val.split()[0].lower() not in stop_words:
        keywords_list.append(val.split()[0])
    else:
        it = 1
        for x in val.split()[1:]:
            if len(val.split()) > it and x.lower() not in stop_words:
                keywords_list.append(val.split()[it])
                break
            else:
                it += 1

'''for val in keywords_list_temp:
    for word in val.split():
        if word not in stop_words:
            keywords_list.append(word)'''

print(keywords_list)

temp = []

for x in range(0, len(keywords_list)):
    try:
        temp.append(model.wv.most_similar_to_given(keywords_list[x].lower(), [x.lower() for x in fields_list]))
    except KeyError:
        temp.append("N/A")

print(temp)

# print(model.wv.most_similar_to_given('Post-Dural', [x.lower() for x in fields_list]))

# print(model.wv.n_similarity([x.lower() for x in keywords_list], [x.lower() for x in fields_list]))

exit(0)









matrice = []

for key in keywords_list:
    line = []
    for field in fields_list:
        line.append(wv_wiki.similarity(key.lower(), field.lower()))
    matrice.append(line)

print("Matrice :: ", matrice)


matrice_temp = []

for field in fields_list:
    line = []
    for key in keywords_list:
        line.append(wv_wiki.similarity(key.lower(), field.lower()))
    matrice_temp.append(line)

moyenne_field = []

for i in range(0, len(fields_list)):
    moyenne_field.append({fields_list[i]: sum(matrice_temp[i]) / float(len(matrice_temp[i]))})

print("Moyenne :: ", moyenne_field)


matriceUp = []

for key in keywords_list:
    line = {}
    for field in fields_list:
        line[field] = wv_wiki.similarity(key.lower(), field.lower())
    matriceUp.append(line)

print("MatriceUp :: ", matriceUp)

maxField = []

for key in matriceUp:
    maxField.append(max(key.items(), key=operator.itemgetter(1))[0])

print("maxField :: ", maxField)

