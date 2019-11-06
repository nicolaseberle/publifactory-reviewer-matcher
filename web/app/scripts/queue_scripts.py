import os
import json

from models.model import getReviewers
from app import es, app, secure_filename


def request_reviewer_func(abstr, auth, dictionary):
    # from models.model import getReviewers
    auth = auth[0].split(",")
    auth = [x.lower() for x in auth]
    # title = request.args.get('title')
    # keywords = request.args.get('keywords')

    data = getReviewers(es, abstr, auth, dictionary)
    result = sorted(data, key=lambda i: i['score'], reverse=True)
    return result


def extract_pdf_func(results):
    if not "title" in results and not "abstract" in results and results["keywords"] == [] and results["authors"] == []:
        results["abstract"] = "We can't extract values from your PDF"
    if not "title" in results:
        results["title"] = ""
    if not "abstract" in results:
        results["abstract"] = ""
    if not "keywords" in results or results["keywords"] == []:
        results["keywords"] = ""
    if not "authors" in results or results["authors"] == []:
        results["authors"] = ""
    data = [{"title": results["title"], "abstract": results["abstract"], "keywords": results["keywords"],
             "authors": results["authors"]}]
    return json.dumps(data)
