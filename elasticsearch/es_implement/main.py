# IMPORTS

from elasticsearch import Elasticsearch

# CONSTS

# ES server host
ES_HOST = 'localhost'
# ES server port
ES_PORT = '9200'

# ES index name for articles
INDEX_NAME_ART = 'articles_large'
# ES index type for article
DOC_TYPE_ART = 'articles_large'
# ES index name for authors
INDEX_NAME_AUT = 'authors_large'
# ES index type for authors
DOC_TYPE_AUT = 'authors_large'
# ES index name for fake base
INDEX_NAME_FAKE = 'authors_fake'
# ES index type for fake base
DOC_TYPE_FAKE = 'authors_fake'

# file path
PATH_NAME = 'corpus/'
# file name
FILE_NAME = 's2-corpus-'

# connexion to ES
es = Elasticsearch(hosts=[ES_HOST])


# MAIN

# Add 1 articles file in new ES index

# from scripts.articles2es import articles2es_file
# articles2es_file(es, PATH_NAME, FILE_NAME, INDEX_NAME_ART, DOC_TYPE_ART, "02")


# Add multiple articles files in new ES index

from scripts.articles2es import articles2es_files
articles2es_files(es, PATH_NAME, FILE_NAME, INDEX_NAME_ART, DOC_TYPE_ART)


# Add authors in new ES index

# from scripts.authors2es import authors2es
# authors2es(es, INDEX_NAME_ART, INDEX_NAME_AUT, DOC_TYPE_AUT)


# Create a fake authors base with redundancy of information

# from scripts.fakebase import fake_authors
# fake_authors(es, INDEX_NAME_FAKE, DOC_TYPE_FAKE)

# Generate a score for each keyword from an author

# from scripts.score_fakebase import score_authors_fake
# score_authors_fake(es, INDEX_NAME_FAKE)
