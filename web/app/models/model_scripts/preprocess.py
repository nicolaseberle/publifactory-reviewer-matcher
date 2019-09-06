# IMPORTS

from nltk import word_tokenize
from nltk import download
from nltk.corpus import stopwords

from gensim.test.utils import get_tmpfile
from gensim import corpora


# DOWNLOADS

download('punkt')
download('stopwords')
stop_words = stopwords.words('english')


# FUNCTIONS

def preprocess(text):

    text = text.lower()
    doc = word_tokenize(text)
    doc = [word for word in doc if word not in stop_words]
    doc = [word for word in doc if word.isalnum()]
    return doc


def getCorpus(df):

    #index_temp = get_tmpfile("index")
    index_temp = "app/models/saves/index"
    corpus = []
    y = {}

    for index, row in df.iterrows():
        corpus.append(preprocess(row["_source"]["paperAbstract"]))
        y[index] = row["_id"]

    dictionary = corpora.Dictionary(corpus)
    corpus_gensim = [dictionary.doc2bow(doc) for doc in corpus]
    return corpus_gensim, index_temp, dictionary, y
