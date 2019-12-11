# IMPORTS

from elasticsearch import helpers
from app import es

# MAIN


def update_nb_use():

    months = {"month": "12/2019", "use": 1}

    action = {
        "_op_type": "update",
        "_index": "number_of_use",
        "_id": 1,
        "_source": {
            "script": {
                "inline": "if (ctx._source.total != null)"
                          "{ctx._source.total += params.incr}"
                          ""
                          "def test = 0;"
                          "for (value in ctx._source.months){"
                            "if (params.months.month = value.month){"
                                "test = 1;"
                                "value.use += params.incr"
                            "}"
                          "}"
                          ""
                          "if (test == 0){"
                            "ctx._source.months.add(months)"
                          "}"
                          ,
                "params": {
                    "incr": 1,
                    "months": months
                }
            },
            "upsert": {
                "total": 1,
                "months": months
            }
        }
    }
    helpers.bulk(es, [action])

    return 123