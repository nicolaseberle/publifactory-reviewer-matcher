import numpy as np


def most_similar(i, X_sims, topn=None):

    r = np.argsort(X_sims[i])[::-1]
    if r is None:
        return r
    else:
        return r[:topn]
