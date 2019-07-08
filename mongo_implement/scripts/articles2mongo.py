# IMPORTS

import json


def articles2mongo_file(coll, path_name, file_name, iterid):

    fd = open(path_name + file_name + iterid, 'r')
    k = 1
    for line in fd:
        data = json.loads(line)
        data['_id'] = data.pop('id')
        coll.update(data, data, upsert=True)
        k += 1
        if k > 10000:
            break


def articles2mongo_files(coll, path_name, file_name):
    for it in range(0, 46):
        if it < 10:
            iterid = "0"+str(it)
        else:
            iterid = str(it)
        articles2mongo_file(coll, path_name, file_name, iterid)
