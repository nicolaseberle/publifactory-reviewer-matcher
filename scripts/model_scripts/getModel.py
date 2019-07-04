# IMPORTS

import gensim
import multiprocessing
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


# CONSTS

cores = multiprocessing.cpu_count()

# MAIN


def getModel(doc):

    model = gensim.models.Word2Vec(size=300, window=10, min_count=2, sg=1, workers=cores-2)
    model.build_vocab(doc)

    model.train(sentences=doc, total_examples=len(doc), epochs=model.iter)
    return model
