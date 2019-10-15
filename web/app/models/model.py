def getReviewers(es, abstract, authors, list_id, dictionary, model):

    #import pickle
    #import pickletools
    from models.model_scripts.testing_rm import getRev_v3

    #list_id = pickle.load(open("app/models/saves/list_id.p", "rb"))
    #dictionary = pickle.load(open("app/models/saves/dictionary.p", "rb"))
    #model = pickle.load(open("app/models/saves/lsi_model.p", "rb"))

    result = getRev_v3(es, abstract, authors, dictionary, list_id, model)

    del model
    del list_id
    del dictionary
    
    return result


def getReviewers_test(es, abstract):

    import pickle
    from models.model_scripts.testing_rm import getRev_test

    list_id = pickle.load(open("app/models/saves/list_id.p", "rb"))
    dictionary = pickle.load(open("app/models/saves/dictionary.p", "rb"))
    model = pickle.load(open("app/models/saves/lsi_model.p", "rb"))
    
    result = getRev_test(es, abstract, dictionary, list_id, model)

    del model
    del dictionary
    del list_id
    
    return result


def updateModel(es):

    # REQUEST ES
    import pickle
    from models.model_scripts.requestsES import get_abstracts
    start = pickle.load(open("app/models/saves_v2/start.p", "rb"))
    
    df_temp = get_abstracts(es, start, 200000)
    
    # PREPROCESS
    from models.model_scripts.preprocess import preprocess
    corpus = []
    list_id = pickle.load(open("app/models/saves_v2/list_id.p", "rb"))
    temp = int(sorted(list_id.keys())[-1])+1
    
    for index, row in df_temp.iterrows():
        corpus.append(preprocess(row["_source"]["paperAbstract"]))
        list_id[temp + index] = row["_id"]

    pickle.dump(list_id, open("app/models/saves_v2/list_id.p", "wb"), protocol=pickle.HIGHEST_PROTOCOL)
    
    # UPDATE MODEL
    from models.model_scripts.lsi_model import updateModel
    
    model = pickle.load(open("app/models/saves_v2/lsi_model.p", "rb"))
    dictionary = pickle.load(open("app/models/saves_v2/dictionary.p", "rb"))
    
    model, dictionary = updateModel(model, corpus, dictionary)
    
    pickle.dump(dictionary, open("app/models/saves_v2/dictionary.p", "wb"), protocol=pickle.HIGHEST_PROTOCOL)
    pickle.dump(model, open("app/models/saves_v2/lsi_model.p", "wb"), protocol=pickle.HIGHEST_PROTOCOL)

    del start
    del list_id
    del model
    del dictionary
    
    
def buildModel(es):

    # IMPORT

    import pickle
    import logging
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

    from models.model_scripts.requestsES import get_abstracts
    from models.model_scripts.requestsES import get_abstract
    from models.model_scripts.requestsES import add_value_es
    from models.model_scripts.preprocess import getCorpus
    from models.model_scripts.preprocess import preprocess
    from models.model_scripts.lsi_model import getModel
    from models.model_scripts.lsi_model import updateModel


    # REQUEST ES
    df_temp = get_abstracts(es, 0, 200000)
    print("Requests ES Done")

   
    # PREPROCESS
    corpus, index, dictionary, list_id = getCorpus(df_temp)
    pickle.dump(index, open("app/models/saves_v2/index.p", "wb"), protocol=pickle.HIGHEST_PROTOCOL)
    pickle.dump(dictionary, open("app/models/saves_v2/dictionary.p", "wb"), protocol=pickle.HIGHEST_PROTOCOL)
    pickle.dump(list_id, open("app/models/saves_v2/list_id.p", "wb"), protocol=pickle.HIGHEST_PROTOCOL)

    index = pickle.load(open("app/models/saves_v2/index.p", "rb"))
    dictionary = pickle.load(open("app/models/saves_v2/dictionary.p", "rb"))
    list_id = pickle.load(open("app/models/saves_v2/list_id.p", "rb"))
    print("Corpus Done")

    
    # LSI Model
    model = getModel(corpus, index, dictionary)
    pickle.dump(model, open("app/models/saves_v2/lsi_model.p", "wb"), protocol=pickle.HIGHEST_PROTOCOL)

    model = pickle.load(open("app/models/saves_v2/lsi_model.p", "rb"))
    print("Model Done")

    del corpus
    del index
    del dictionary
    del list_id
    del model
