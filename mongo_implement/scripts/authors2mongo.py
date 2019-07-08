# IMPORTS

import pandas as pd
import logging


# CONSTS

LOG_FILENAME = 'l.log'
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG, filemode='w')

# MAIN


def authors2mongo(coll_get, coll_add):
    cursor = coll_get.find({}, {"_id": 1, "title": 1, "entities": 1, "year": 1, "authors": 1})
    df = pd.DataFrame(list(cursor))

    k = 1

    for index, row in df.iterrows():
        logging.info('Iter : {}'.format(k))
        try:
            int(row['year'])
        except ValueError:
            year = -1
        else:
            year = int(row['year'])
        authors = row['authors']

        for author in list(authors):
            if author['ids'] == []:
                final_ids = -1
            else:
                final_ids = int(author['ids'][0])
            final_name = author['name']
            if row['entities'] == []:
                row['entities'] = ["-1"]
            for entitie in row['entities']:
                coll_add.update(
                    {'auth_id': final_ids, 'name': final_name},
                    {"$set": {'auth_id': final_ids, 'name': final_name},
                     "$addToSet": {'entities': [entitie, int(year), row['_id']]}},
                    upsert=True)

        k += 1
