def getReviewers(es, abstract):

    import pickle
    from models.model_scripts.testing_rm import getRev_v3

    list_id = pickle.load(open("app/models/saves/list_id.p", "rb"))
    dictionary = pickle.load(open("app/models/saves/dictionary.p", "rb"))
    model = pickle.load(open("app/models/saves/lsi_model.p", "rb"))

    result = getRev_v3(es, abstract, dictionary, list_id, model)

    return result


def getReviewers_test(es, abstract):

    import pickle
    from models.model_scripts.testing_rm import getRev_test

    list_id = pickle.load(open("app/models/saves/list_id.p", "rb"))
    dictionary = pickle.load(open("app/models/saves/dictionary.p", "rb"))
    model = pickle.load(open("app/models/saves/lsi_model.p", "rb"))
    
    result = getRev_test(es, abstract, dictionary, list_id, model)
    
    return result


def updateModel(es):

    # REQUEST ES
    import pickle
    from models.model_scripts.requestsES import get_abstracts
    start = pickle.load(open("app/models/saves/start.p", "rb"))
    
    df_temp = get_abstracts(es, start, 200000)
    
    # PREPROCESS
    from models.model_scripts.preprocess import preprocess
    corpus = []
    list_id = pickle.load(open("app/models/saves/list_id.p", "rb"))
    temp = int(sorted(list_id.keys())[-1])+1
    
    for index, row in df_temp.iterrows():
        corpus.append(preprocess(row["_source"]["paperAbstract"]))
        list_id[temp + index] = row["_id"]

    pickle.dump(list_id, open("app/models/saves/list_id.p", "wb"))
    
    # UPDATE MODEL
    from models.model_scripts.lsi_model import updateModel
    
    model = pickle.load(open("app/models/saves/lsi_model.p", "rb"))
    dictionary = pickle.load(open("app/models/saves/dictionary.p", "rb"))
    
    model, dictionary = updateModel(model, corpus, dictionary)
    
    pickle.dump(dictionary, open("app/models/saves/dictionary.p", "wb"))
    pickle.dump(model, open("app/models/saves/lsi_model.p", "wb"))
    
    
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
    #pickle.dump(df_temp, open("app/models/saves/dfES.p", "wb"))

    #df_temp = pickle.load(open("app/models/saves/dfES.p", "rb"))
    print("Requests ES Done")


    # PREPROCESS

    corpus, index, dictionary, list_id = getCorpus(df_temp)
    #pickle.dump(corpus, open("app/models/saves/corpus.p", "wb"))
    pickle.dump(index, open("app/models/saves/index.p", "wb"))
    pickle.dump(dictionary, open("app/models/saves/dictionary.p", "wb"))
    pickle.dump(list_id, open("app/models/saves/list_id.p", "wb"))

    #corpus = pickle.load(open("app/models/saves/corpus.p", "rb"))
    index = pickle.load(open("app/models/saves/index.p", "rb"))
    dictionary = pickle.load(open("app/models/saves/dictionary.p", "rb"))
    list_id = pickle.load(open("app/models/saves/list_id.p", "rb"))
    print("Corpus Done")


    # LSI Model

    model = getModel(corpus, index, dictionary)
    pickle.dump(model, open("app/models/saves/lsi_model.p", "wb"))

    model = pickle.load(open("app/models/saves/lsi_model.p", "rb"))
    print("Model Done")


    # UPDATE LSI MODEL

    new_value = {
        "id": "XX-1",
        "title": "The article describes the control of the 2-axis electrohydraulic manipulator by the human-hand motion. To recognition of skeleton points the Kinect sensor was used. In this application the information about coordinates of shoulder, elbow and hand was used to compute of inverse kinematic in manipulator. In investigation the accuracy of control by human's hand motion was tested. The aim of study was to find a new of control method without commonly used joysticks to create human-machine interface.",
        "abstract": "Considering the geographical asymmetric distribution of viral hepatitis A, B and E, having a much higher prevalence in the less developed world, travellers from developed countries are exposed to a considerable and often underestimated risk of hepatitis infection. In fact a significant percentage of viral hepatitis occurring in developed countries is travel related. This results from globalization and increased mobility from tourism, international work, humanitarian and religious missions or other travel related activities. Several studies published in Europe and North America shown that more than 50% of reported cases of hepatitis A are travel related. On the other hand frequent outbreaks of hepatitis A and E in specific geographic areas raise the risk of infection in these restricted zones and that should be clearly identified. Selected aspects related with the distribution of hepatitis A, B and E are reviewed, particularly the situation in Portugal according to the published studies, as well as relevant clinical manifestations and differential diagnosis of viral hepatitis. Basic prevention rules considering enteric transmitted hepatitis (hepatitis A and hepatitis E) and parenteral transmitted (hepatitis B) are reviewed as well as hepatitis A and B immunoprophylaxis. Common clinical situations and daily practice pre travel advice issues are discussed according to WHO/CDC recommendations and the Portuguese National Vaccination Program. Implications from near future availability of a hepatitis E vaccine, a currently in phase 2 trial, are highlighted. Potential indications for travellers to endemic countries like India, Nepal and some regions of China, where up to 30% of sporadic cases of acute viral hepatitis are caused by hepatitis E virus, are considered. Continued epidemiological surveillance for viral hepatitis is essential to recognize and control possible outbreaks, but also to identify new viral hepatitis agents that may emerge as important global health issues.",
        "keywords": ["Antihypertensive Agents"]
    }

    '''
    
    temp = sorted(list_id.keys())[-1]+1
    list_id[int(temp)] = new_value["id"]
    
    value = [preprocess(new_value["abstract"])]
    model, dictionary = updateModel(model, value, dictionary)
    
    add_value_es(new_value["id"], new_value["title"], new_value["keywords"], new_value["abstract"])
    
    '''

# TESTING

    '''
    test = [preprocess(new_value['abstract'])]
    test2 = [dictionary.doc2bow(doc) for doc in test]
    result = model.__getitem__(test2)
    

    print(result)
    list_authors = []

    for i in result[0]:
        print(get_abstract(list_id[i[0]])["paperAbstract"])

        res = get_abstract(list_id[i[0]])["authors"]
        for auth in res:
            list_authors.append({"name": auth["name"], "score": i[1]})

    print(list_authors)
    '''
