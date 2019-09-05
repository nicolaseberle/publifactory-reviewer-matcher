# IMPORTS

from gensim.similarities import Similarity


# FUNCTIONS

## CREATE NEW LSI MODEL

def getModel(corpus, index, dictionary):
    model = Similarity(index, corpus, num_features=len(dictionary), num_best=5)
    return model


## ADDING NEW DOCS AND UPDATE MODEL

def updateModel(model, value, dictionary):
    value = [value]
    dictionary.add_documents(value)
    new_corpus = [dictionary.doc2bow(doc) for doc in value]
    model.add_documents(new_corpus)
    return model, dictionary
