# IMPORT

import gensim
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# MAIN

def read_questions(row, column_name):
    return gensim.utils.simple_preprocess(str(row[column_name]).encode('utf-8'))

def getDocuments(f):
    documents = []
    for index, row in f.iterrows():
        documents.append(read_questions(row, "_source"))
    return documents
