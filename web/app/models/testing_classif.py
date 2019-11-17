# IMPORT

from sklearn.externals import joblib
from sklearn.base import BaseEstimator
from sklearn.pipeline import FeatureUnion

from gensim.models.doc2vec import TaggedDocument, Doc2Vec

import pickle
import numpy as np
import multiprocessing
import pandas as pd

from gensim import utils
import gensim.parsing.preprocessing as gsp

from sklearn.preprocessing import MultiLabelBinarizer
from gensim.models.doc2vec import TaggedDocument, Doc2Vec
from sklearn.base import BaseEstimator
from sklearn import utils as skl_utils
from tqdm import tqdm


from skmultilearn.problem_transform import ClassifierChain
from sklearn.model_selection import train_test_split
from sklearn.pipeline import FeatureUnion


from sklearn.pipeline import Pipeline
from skmultilearn.problem_transform import BinaryRelevance
from sklearn.ensemble import RandomForestClassifier

# MAIN

def clean_text(s):
    s = s.lower()
    s = utils.to_unicode(s)
    for f in filters:
        s = f(s)
    return s

filters = [
           gsp.strip_tags,
           gsp.strip_punctuation,
           gsp.strip_multiple_whitespaces,
           gsp.strip_numeric,
           gsp.remove_stopwords,
           gsp.strip_short,
           gsp.stem_text
          ]

class Doc2VecTransformer(BaseEstimator):
    def __init__(self, vector_size=100, learning_rate=0.02, epochs=20, field=None):
        self.learning_rate = learning_rate
        self.epochs = epochs
        self._model = None
        self.vector_size = vector_size
        self.workers = multiprocessing.cpu_count() - 1
        self.field = field

    def fit(self, df_x, df_y=None):
        tagged_x = [TaggedDocument(clean_text(row[str(self.field)]).split(), [index]) for index, row in df_x.iterrows()]
        model = Doc2Vec(documents=tagged_x, vector_size=self.vector_size, workers=self.workers)

        for epoch in range(self.epochs):
            model.train(skl_utils.shuffle([x for x in tqdm(tagged_x)]), total_examples=len(tagged_x), epochs=1)
            model.alpha -= self.learning_rate
            model.min_alpha = model.alpha

        self._model = model
        return self

    def save(self):
        filename = 'w2v/finalized_random_forest_model.sav'
        pickle.dump(self._model, open(filename, 'wb'))

    def load(self):
        filename = 'w2v/finalized_random_forest_model.sav'
        self._model = pickle.load(open(filename, 'rb'))

    def transform(self, df_x):
        return np.asmatrix(np.array([self._model.infer_vector(clean_text(row[str(self.field)]).split())
                                     for index, row in df_x.iterrows()]))


multi_label_rf_br_model = joblib.load('w2v/model_classif_abstract2fields.joblib')

test_x = {'abstract':["The phenomenological early dark energy (EDE) provides a promising solution to the Hubble tension in the form of an extra beyond-ΛCDM component that acts like a cosmological constant at early times (z ≥ 3000) and then dilutes away as radiation or faster. We show that a rolling axion coupled to a non-Abelian gauge group, which we call the ‘dissipative axion’ (DA), mimics this phenomenological EDE at the background level and presents a particle-physics model solution to the Hubble tension, while also eliminating fine-tuning in the choice of scalar-field potential. We compare the DA model to the EDE fluid approximation at the background level and comment on their similarities and differences. We determine that CMB observables sensitive only to the background evolution of the Universe are expected to be similar in the two models, strengthening the case for exploring the perturbations of the DA as well as for this model to provide a viable solution to the Hubble tension"]}
df_test = pd.DataFrame(data=test_x)
print(df_test)

print('Classe prediction ', multi_label_rf_br_model.predict(df_test))
