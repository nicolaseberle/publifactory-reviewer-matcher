# IMPORTS

import logging
import io
import os
import gzip


# MAIN


def articles2es_file(es, path_name, file_name, index_name, doc_type, iterid):
    fd = gzip.open(path_name + file_name + iterid + '.gz', 'rb')
    #fd = io.open(path_name + file_name + iterid, "r", encoding="utf8")
    k = 1
    for line in fd:
        es.index(index=index_name, doc_type=doc_type, body=line, id=iterid + "-" + str(k))
        print(iterid + "-" + str(k))
        k = k + 1

def articles2es_files(es, path_name, file_name, index_name, doc_type):

    for it in range(15, 47):
        if it < 10:
            iterid = "0"+str(it)
        else:
            iterid = str(it)
        articles2es_file(es, path_name, file_name, index_name, doc_type, iterid)
        os.remove(path_name + file_name + iterid + ".gz")
