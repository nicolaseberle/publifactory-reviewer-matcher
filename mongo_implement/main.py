# IMPORTS

from pymongo import MongoClient
import multiprocessing
# import time

# CONSTS

# MongoDB connection

db_client = MongoClient(host="localhost", port=27017)
db = db_client.reviewer_matcher
coll_art = db.articles
coll_aut = db.authors


# file path
PATH_NAME = 'corpus/'
# file name
FILE_NAME = 's2-corpus-'

# MAIN

# Add 1 articles file in MongoDB

# from scripts.articles2mongo import articles2mongo_file
# articles2mongo_file(coll_art, PATH_NAME, FILE_NAME, "00")


# Add multiple articles file in MongoDB

# from scripts.articles2mongo import articles2mongo_files
# articles2mongo_files(coll_art, PATH_NAME, FILE_NAME)


# Add authors in MongoDB

from scripts.authors2mongo import authors2mongo
# authors2mongo(coll_art)
#pool = multiprocessing.Pool(processes=20)
#pool.map(authors2mongo(coll_art))
#pool.close()
