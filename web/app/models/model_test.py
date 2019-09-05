# IMPORT

import pickle
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


# REQUEST ES

#from model_scripts_test.requestsES import df_temp
#pickle.dump(df_temp, open("../saves_v2/dfES.p", "wb"))

df_temp = pickle.load(open("../saves_v2/dfES.p", "rb" ))
print("Requests ES Done")


# CREATE DOCUMENTS

#from model_scripts_test.getDocuments import getDocuments
#documents = getDocuments(df_temp)
#pickle.dump(documents, open("../saves_v2/documents.p", "wb"))

documents = pickle.load(open("../saves_v2/documents.p", "rb"))
print("Generate Documents Done")


# MODEL

#from model_scripts_test.getModel import getModel
#model = getModel(documents)
#pickle.dump(model, open("../saves_v2/model_v1.p", "wb"))

model = pickle.load(open("../saves_v2/model_v1.p", "rb"))
print("Model Done")


# UPDATE MODEL (RECURSIVE WAY)

# from model_scripts_test.updateModel import updateModel
# model = updateModel(model, new_docs)


# TESTING

#print(model_scripts_test.wv.similarity('milk', 'dairy'))
#print(model_scripts_test.wv.most_similar(positive='potatoes', topn=10))
