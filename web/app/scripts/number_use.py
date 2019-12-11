# IMPORTS

# MAIN


def update_nb_use(es):
    es.update(index='number_of_use', request_timeout=100, id=1, body={
        "script": {
            "source": "ctx._source.total += params.total;",
            "lang": "painless",
            "params": {
                "total": 1
            }
        }
    })
