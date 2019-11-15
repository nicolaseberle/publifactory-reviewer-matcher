# IMPORT

from sklearn.externals import joblib
from sklearn.base import BaseEstimator
from sklearn.pipeline import FeatureUnion

from gensim.models.doc2vec import TaggedDocument, Doc2Vec

import pickle
import numpy as np
import multiprocessing

# MAIN

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


multi_label_rf_br_model = joblib.load('w2v/model.joblib', 'r+')

test_x = [["In 6 dogs the influence of consecutively a selective proximal vagotomy (SPV) and a truncal vagotomy (TV) on gallbladder bile composition was studied. Following SPV no significant changes in biliary lipids were observed. On the other hand, after TV an increase of deoxycholic acid (D) and a concomitant decrease of cholic acid (C) occurred, resulting in a marked increase of the D/C ratio. Although a positive correlation was found between the D/C ratio and the lithogenic index of bile, the change in bile acid composition after TV was accompanied with only a slight, statistically not significant increase of the lithogenic index. It is concluded that in the dog neither SPV nor TV is a definitely lithogenic procedure."]]


print('TEST ', multi_label_rf_br_model.predict(test_x))
