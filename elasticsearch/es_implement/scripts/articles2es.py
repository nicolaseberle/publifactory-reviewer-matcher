# IMPORTS

import logging
import io

# CONSTS

#LOG_FILENAME = 'l.log'
#logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG, filemode='w')

# MAIN


def articles2es_file(es, path_name, file_name, index_name, doc_type, iterid):
    fd = io.open(path_name + file_name + iterid, "r", encoding="utf8")
    k = 1
    for line in fd:
        #logging.info('Iter : {}'.format(k))
        es.index(index=index_name, doc_type=doc_type, body=line, id=iterid + "-" + str(k))
        k = k + 1


def articles2es_files(es, path_name, file_name, index_name, doc_type):

    for it in range(0, 46):
        if it < 10:
            iterid = "0"+str(it)
        else:
            iterid = str(it)
        articles2es_file(es, path_name, file_name, index_name, doc_type, iterid)
