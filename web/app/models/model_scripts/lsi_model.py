# IMPORTS

from gensim.similarities import Similarity


# FUNCTIONS

## CREATE NEW LSI MODEL

def getModel(corpus, index, dictionary):
    model = Similarity(index, corpus, num_features=5000000, num_best=30)
    model.close_shard()
    return model

## ADDING NEW DOCS AND UPDATE MODEL

def updateModel(model, value, dictionary):
    if type([]) != type(value):
        value = [value]
    dictionary.add_documents(value, prune_at=None)
    new_corpus = [dictionary.doc2bow(doc) for doc in value]
    model.add_documents(new_corpus)
    model.close_shard()
    return model, dictionary
