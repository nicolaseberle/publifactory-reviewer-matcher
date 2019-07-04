# IMPORT

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# MAIN


def updateModel(model, doc):

    model.build_vocab(doc, update=True)
    model.train(sentences=doc, total_examples=model.corpus_count, epochs=model.iter)
    return model
