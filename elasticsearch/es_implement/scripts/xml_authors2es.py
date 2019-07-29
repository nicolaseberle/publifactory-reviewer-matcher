# IMPORTS

from elasticsearch import Elasticsearch
import xmltodict
import json
import os
import io
from time import sleep
import csv
import shutil

# CONSTS

# ES index name for articles
INDEX_NAME_ORC = 'orcid_large'
# ES index type for article
DOC_TYPE_ORC = 'orcid_large'

es = Elasticsearch(hosts=["localhost"])

FILE_PATH = "../orcid/"

# MAIN

files_done = open("temp.csv","a+")
with open('temp.csv', 'r') as fp:
    temp = fp.read()

   
for folder in os.listdir(FILE_PATH):
    k = 0
    if folder not in temp:
        for filename in os.listdir(FILE_PATH + folder):
            print(folder, filename)
            with io.open(FILE_PATH+folder+"/"+filename, "r", encoding="utf-8") as fd:
                doc = json.dumps(xmltodict.parse(fd.read()))
                es.index(index=INDEX_NAME_ORC, doc_type=DOC_TYPE_ORC, body=doc, id=str(folder)+"-"+str(k))
                sleep(0.005)
            k += 1
        files_done.write(folder+",")
        shutil.rmtree(FILE_PATH + folder)
        
