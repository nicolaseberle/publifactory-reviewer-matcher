# IMPORTS

import pandas as pd
import numpy as np
import datetime


def score_authors_fake(es, index_name_fake):

    res = es.search(index=index_name_fake, body={"query": {"match_all": {}}})
    res = res['hits']['hits']

    df = pd.DataFrame(res)
    base = df["_source"]
    final = {}
    now = datetime.datetime.now()

    for line in base:
        nbArt = len(set([x[2] for x in line['entities']]))
        keywords = {}
        temp = {}
        for entitie in line['entities']:
            if entitie[0] in keywords:
                keywords[entitie[0]][0] += 1
                if entitie[1] > keywords[entitie[0]][1]:
                    keywords[entitie[0]][1] = entitie[1]
            else:
                keywords[entitie[0]] = [1, entitie[1]]

        for keyword in keywords:
            if (now.year - int(keywords[keyword][1])) > 2:
                pondYear = np.sqrt(np.log(2) / np.log(now.year - int(keywords[keyword][1])))
            elif (now.year - int(keywords[keyword][1])) == 2:
                pondYear = 0.9
            elif (now.year - int(keywords[keyword][1])) == 1:
                pondYear = 0.95
            else:
                pondYear = 1
            temp[keyword] = (np.exp(keywords[keyword][0]/nbArt)*pondYear)/np.exp(1)
        final[line['name']] = temp
    print(final)
