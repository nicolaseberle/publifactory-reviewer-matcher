from ..model_scripts.preprocess import preprocess
from ..model_scripts.requestsES import get_abstract


def getRev(es, value, dictionary, list_id, model):

    test = [preprocess(value)]
    test2 = [dictionary.doc2bow(doc) for doc in test]
    result = model.__getitem__(test2)

    list_authors = []

    for i in result[0]:
        #print(get_abstract(list_id[i[0]])["paperAbstract"])

        res = get_abstract(es, list_id[i[0]])["authors"]
        for auth in res:
            list_authors.append({"name": auth["name"], "score": i[1]})

    return list_authors
