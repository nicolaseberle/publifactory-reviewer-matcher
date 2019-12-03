import pickle
import logging
import pandas as pd
import os

from models.model_scripts.testing_rm import getRev_v3
from models.model_scripts.requestsES import get_abstracts, get_abstracts_field, get_abstracts_field_big, get_citations_auth, get_citations_id, get_abstract_id
from models.model_scripts.preprocess import getCorpus, getCorpus2, preprocess
from models.model_scripts.lsi_model import getModel, updateModelLSI


def getReviewers(es, abstract, authors, dictionary):

    list_id = pickle.load(open("app/models/saves/list_id.p", "rb"))
    model = pickle.load(open("app/models/saves/lsi_model.p", "rb"))

    result = getRev_v3(es, abstract, authors, dictionary, list_id, model)

    del model
    del list_id
    del dictionary
    
    return result


def getReviewersField(es, abstract, authors, dictionary, field, sub_cat):
    list_id = pickle.load(open("app/models/similarities/"+field+"/list_id.pkl", "rb"))
    model = pickle.load(open("app/models/similarities/"+field+"/lsi_model_"+field+".pkl", "rb"))

    result = getRev_v3(es, abstract, authors, dictionary, list_id, model, field, sub_cat)

    del model
    del list_id
    del dictionary

    return result


def updateModel(es, field):

    # REQUEST ES
    start = pickle.load(open("app/models/similarities/"+field+"/start.pkl", "rb"))
    
    df_temp = get_abstracts_field(es, start, 200000, field)
    
    # PREPROCESS

    corpus = []
    list_id = pickle.load(open("app/models/similarities/"+field+"/list_id.pkl", "rb"))
    temp = int(sorted(list_id.keys())[-1])+1
    
    for index, row in df_temp.iterrows():
        corpus.append(preprocess(row["_source"]["paperAbstract"]))
        list_id[temp + index] = row["_id"]

    pickle.dump(list_id, open("app/models/similarities/"+field+"/list_id.pkl", "wb"), protocol=pickle.HIGHEST_PROTOCOL)
    
    # UPDATE MODEL

    
    model = pickle.load(open("app/models/similarities/"+field+"/lsi_model_"+field+".pkl", "rb"))
    dictionary = pickle.load(open("app/models/similarities/"+field+"/dictionary.pkl", "rb"))
    
    model, dictionary = updateModelLSI(model, corpus, dictionary)
    
    pickle.dump(dictionary, open("app/models/similarities/"+field+"/dictionary.pkl", "wb"), protocol=pickle.HIGHEST_PROTOCOL)
    pickle.dump(model, open("app/models/similarities/"+field+"/lsi_model_"+field+".pkl", "wb"), protocol=pickle.HIGHEST_PROTOCOL)

    del start
    del list_id
    del model
    del dictionary


def updateModelbig(es, field):
    # REQUEST ES
    start = pickle.load(open("app/models/similarities/" + field + "/start.pkl", "rb"))

    df_temp = get_abstracts_field_big(es, start, 200000, field)

    # PREPROCESS

    corpus = []
    list_id = pickle.load(open("app/models/similarities/" + field + "/list_id.pkl", "rb"))
    temp = int(sorted(list_id.keys())[-1]) + 1

    for index, row in df_temp.iterrows():
        corpus.append(preprocess(row["_source"]["paperAbstract"]))
        list_id[temp + index] = row["_id"]

    pickle.dump(list_id, open("app/models/similarities/" + field + "/list_id.pkl", "wb"),
                protocol=pickle.HIGHEST_PROTOCOL)

    # UPDATE MODEL

    model = pickle.load(open("app/models/similarities/" + field + "/lsi_model_" + field + ".pkl", "rb"))
    dictionary = pickle.load(open("app/models/similarities/" + field + "/dictionary.pkl", "rb"))

    model, dictionary = updateModelLSI(model, corpus, dictionary)

    pickle.dump(dictionary, open("app/models/similarities/" + field + "/dictionary.pkl", "wb"),
                protocol=pickle.HIGHEST_PROTOCOL)
    pickle.dump(model, open("app/models/similarities/" + field + "/lsi_model_" + field + ".pkl", "wb"),
                protocol=pickle.HIGHEST_PROTOCOL)

    del start
    del list_id
    del model
    del dictionary

    
def buildModel(es, field):

    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

    # REQUEST ES
    df_temp = get_abstracts_field(es, 0, 200000, field)
    print("Requests ES Done")


    # PREPROCESS
    corpus, index, dictionary, list_id = getCorpus(df_temp, field)
    pickle.dump(index, open("app/models/similarities/"+field+"/index.pkl", "wb"), protocol=pickle.HIGHEST_PROTOCOL)
    pickle.dump(dictionary, open("app/models/similarities/"+field+"/dictionary.pkl", "wb"), protocol=pickle.HIGHEST_PROTOCOL)
    pickle.dump(list_id, open("app/models/similarities/"+field+"/list_id.pkl", "wb"), protocol=pickle.HIGHEST_PROTOCOL)

    print("Corpus Done")

    
    # LSI Model
    model = getModel(corpus, index)
    pickle.dump(model, open("app/models/similarities/"+field+"/lsi_model_"+field+".pkl", "wb"), protocol=pickle.HIGHEST_PROTOCOL)

    print("Model Done")

    del corpus
    del index
    del dictionary
    del list_id
    del model


def getReviewersCits(es, abstract, authors, sub_cat):

    result = []
    for auth in authors:
        data = get_citations_auth(es, auth)
        for art in data:
            for citation in art['_source']['outCitations']:
                if citation not in result:
                    result.append(citation)

    if len(result) < 1000 and len(result) != 0:
        for id in result:
            check = False
            if get_citations_id(es, id):
                temp = get_citations_id(es, id)[0]['_source']['outCitations']
                for res in temp[:50]:
                    if len(result) >= 1000:
                        check = True
                        break
                    else:
                        result.append(res)
            if check:
                break
    else:
        result = result[:1000]

    if result != []:

        # REQUEST ES
        df_temp = pd.DataFrame(columns=["_id", "_index", "_score", "_source", "_type"])
        for id in result:
            if get_abstract_id(es, id):
                df_temp = df_temp.append(get_abstract_id(es, id)[0], ignore_index=True)

        # PREPROCESS
        corpus, index, dictionary, list_id = getCorpus2(df_temp, result[0])

        print("Corpus Done")

        # LSI Model

        model = getModel(corpus, index)

        print("Model Done")

        result = getRev_v3(es, abstract, authors, dictionary, list_id, model, "Citations", sub_cat)

        os.remove("app/models/similarities/simi_temps/temp_" + result[0] + ".0")
        del corpus
        del index
        del dictionary
        del list_id
        del model

    return result