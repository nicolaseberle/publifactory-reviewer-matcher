import json
import requests
from elasticsearch import Elasticsearch

ES_HOST = 'localhost'
ES_PORT = '9200'

es = Elasticsearch(hosts = [ES_HOST])

INDEX_NAME = 'articles_large'
DOC_TYPE = 'articles_large'
PATH_NAME = '../BDD/Corpus/'
FILE_NAME = 's2-corpus-'

uri = 'http://localhost:9200/articles_large/'
headers = {'Content-Type' : 'application/json'}

k = 1
data_ = {}
data_['publications'] = []



for it in range(0, 46):
    if it>0:
        break
    if it < 10 :
        iterId = "0"+str(it)
    else :
        iterId = str(it)
    fd= open(PATH_NAME+FILE_NAME+iterId,"r")
    for line in fd:
        data_['publications'].append(line)
    
        #with open('data.txt', 'w') as outfile:  
        #    json.dump(data_, outfile)

        if len(line) ==  0 :
            print('attention, chaine vide')
            continue
        #query = json.dumps(data_)
        #print(query)
        resp = es.index(index = INDEX_NAME, doc_type = DOC_TYPE, body=line, id=iterId+"-"+str(k))
        # print(resp)
        #response = requests.post(uri, headers=headers, data = query )
        #print(response)
        k = k+1
        # if k>10:
          #  break

