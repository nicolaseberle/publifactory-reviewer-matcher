from ..model_scripts.preprocess import preprocess
from ..model_scripts.requestsES import get_abstract, get_authors_doi, get_authors_name, get_authors_id
import datetime
import numpy as np


def find(key, dictionary):
    for k, v in dictionary.items():
        if k == key:
            yield v
        elif isinstance(v, dict):
            for result in find(key, v):
                yield result
        elif isinstance(v, list):
            for d in v:
                for result in find(key, d):
                    yield result


def getRev_v3(es, value, auth_input, dictionary, list_id, model, field, sub_cat):
    preprocess_value = [preprocess(value)]
    new_dict = [dictionary.doc2bow(doc) for doc in preprocess_value]

    result = model.__getitem__(new_dict)

    resultats = []

    # y = 0

    for i in result[0]:
        # Get article from ES
        article = get_abstract(es, list_id[i[0]])

        is_doi = False
        # Get verified authors
        if get_authors_doi(es, article["doi"]):
            orcid_doi = get_authors_doi(es, article["doi"])
            authors = []
            is_doi = True

            for a in orcid_doi:
                # Get the orcid
                orcid = list(find("record:record", a))[0]["common:orcid-identifier"]["common:path"]

                # Get the name
                name = list(find("personal-details:credit-name", a))
                if name:
                    name = name[0]
                if not name:
                    name1 = list(find("personal-details:given-names", a))
                    name2 = list(find("personal-details:family-name", a))
                    if name1 and name2:
                        if name1[0] and name2[0]:
                            name = name1[0]+" "+name2[0]
                        else:
                            name = "Unknown"
                    else:
                        name = "Unknown"

                # Get the affiliation
                affil = list(find("employment:employment-summary", a))
                
                if affil:
                    affil = affil[0]
                    if type([]) == type(affil):
                        if "employment:organization" in affil[0]:
                            affil = affil[0]["employment:organization"]["common:name"] + ": " +\
                                    affil[0]["employment:organization"]["common:address"]["common:city"] + ", " + \
                                    affil[0]["employment:organization"]["common:address"]["common:country"]
                        else:
                            affil = []
                    else:
                        if "employment:organization" in affil:
                            affil = affil["employment:organization"]["common:name"] + ": " + \
                                    affil["employment:organization"]["common:address"]["common:city"] + ", " + \
                                    affil["employment:organization"]["common:address"]["common:country"]
                        else:
                            affil = []

                country = list(find("address:country", a))
                if not country:
                    country = "N/A"

                # Add the author
                if orcid and name:
                    authors.append({
                        "name": name,
                        "ids": [orcid],
                        "orig_id": -1,
                        "affiliation": affil,
                        "country": country,
                        "contact": [{"Personal ORCID": "https://orcid.org/"+orcid}],
                        "verif": 2})

                    # Check and add the mail
                    if list(find("email:email", a)):
                        tempMail = list(find("email:email", a))[0]
                        if type(tempMail) == type({}):
                            for m in list(find("email:email", tempMail)):
                                authors[-1]["contact"].append({"mail": m})

                    # Check and add website
                    if list(find("researcher-url:researcher-url", a)):
                        tempWeb = list(find("researcher-url:researcher-url", a))[0]
                        if type(tempWeb) == type([]):
                            for r in range(0, len(tempWeb)):
                                if "researcher-url:url-name" in tempWeb[r] and "researcher-url:url" in tempWeb[r]:
                                    authors[-1]["contact"].append({tempWeb[r]["researcher-url:url-name"]: tempWeb[r]["researcher-url:url"]})
                        else:
                            if "researcher-url:url-name" in tempWeb and "researcher-url:url" in tempWeb:
                                authors[-1]["contact"].append({tempWeb["researcher-url:url-name"]: tempWeb["researcher-url:url"]})

                    # Check and add external IDS
                    if list(find("external-identifier:external-identifier", a)):
                        tempExt = list(find("external-identifier:external-identifier", a))[0]
                        if type(tempExt) == type([]):
                            for e in range(0, len(tempExt)):
                                if "common:external-id-type" in tempExt[e] and "common:external-id-url" in tempExt[e]:
                                    authors[-1]["contact"].append({tempExt[e]["common:external-id-type"]: tempExt[e]["common:external-id-url"]})
                        else:
                            if "common:external-id-type" in tempExt and "common:external-id-url" in tempExt:
                                authors[-1]["contact"].append({tempExt["common:external-id-type"]: tempExt["common:external-id-url"]})

                for x in article["authors"]:
                    for y in authors:
                        if y["name"].split()[-1] == x["name"].split()[-1]:
                            y["orig_id"] = x["ids"]

        # If not, get authors from the article
        else:
            authors = article["authors"]
        co = 0
        auth_last = [x.split()[-1] for x in auth_input]
        for auth in authors:
            if len(auth["ids"]) > 0 and auth["name"].split()[-1].lower() not in auth_last and auth["name"].lower() not in auth_input:
            # if len(auth["ids"]) > 0:

                # Check if contact exist
                if "contact" not in auth:
                    auth["contact"] = []

                if "affiliation" not in auth:
                    auth["affiliation"] = []

                if "verif" not in auth:
                    auth["verif"] = 0

                if "country" not in auth:
                    auth["country"] = "N/A"

                # Check if the name exist in orcid
                if get_authors_name(es, auth["name"]) and not is_doi:
                    au = get_authors_name(es, auth["name"])[0]

                    # Get the orcid
                    orc = list(find("record:record", au))[0]["common:orcid-identifier"]["common:path"]

                    # Get the name
                    name = list(find("personal-details:credit-name", au))
                    if name:
                        name = name[0]
                    if not name:
                        name1 = list(find("personal-details:given-names", au))
                        name2 = list(find("personal-details:family-name", au))
                        if name1 and name2:
                            name = name1[0]+" "+name2[0]

                    # Get the affiliation
                    affil = list(find("employment:employment-summary", au))

                    if affil:
                        affil = affil[0]
                        if type([]) == type(affil):
                            if "employment:organization" in affil[0]:
                                affil = affil[0]["employment:organization"]["common:name"] + ": " + \
                                        affil[0]["employment:organization"]["common:address"]["common:city"] + ", " + \
                                        affil[0]["employment:organization"]["common:address"]["common:country"]
                            else:
                                affil = []
                        else:
                            if "employment:organization" in affil:
                                affil = affil["employment:organization"]["common:name"] + ": " + \
                                        affil["employment:organization"]["common:address"]["common:city"] + ", " + \
                                        affil["employment:organization"]["common:address"]["common:country"]
                            else:
                                affil = []

                    country = list(find("address:country", au))
                    if not country:
                        country = "N/A"

                    auth["orig_id"] = auth["ids"]
                    auth["ids"] = [orc]
                    auth["name"] = name
                    auth["affiliation"] = affil
                    auth["country"] = country
                    auth["verif"] = 1
                    auth["contact"] = [{"Personal ORCID": "https://orcid.org/"+orc}]

                    # Check and add the mail
                    if list(find("email:email", au)):
                        tempMail = list(find("email:email", au))[0]
                        if type(tempMail) == type({}):
                            for m in list(find("email:email", tempMail)):
                                auth["contact"].append({"mail": m})

                    # Check and add website
                    if list(find("researcher-url:researcher-url", au)):
                        tempWeb = list(find("researcher-url:researcher-url", au))[0]
                        if type(tempWeb) == type([]):
                            for r in range(0, len(tempWeb)):
                                if "researcher-url:url-name" in tempWeb[r] and "researcher-url:url" in tempWeb[r]:
                                    auth["contact"].append({tempWeb[r]["researcher-url:url-name"]: tempWeb[r]["researcher-url:url"]})
                        else:
                            if "researcher-url:url-name" in tempWeb and "researcher-url:url" in tempWeb:
                                auth["contact"].append({tempWeb["researcher-url:url-name"]: tempWeb["researcher-url:url"]})

                    # Check and add external IDS
                    if list(find("external-identifier:external-identifier", au)):
                        tempExt = list(find("external-identifier:external-identifier", au))[0]
                        if type(tempExt) == type([]):
                            for e in range(0, len(tempExt)):
                                if "common:external-id-type" in tempExt[e] and "common:external-id-url" in tempExt[e]:
                                    auth["contact"].append({tempExt[e]["common:external-id-type"]: tempExt[e]["common:external-id-url"]})
                        else:
                            if "common:external-id-type" in tempExt and "common:external-id-url" in tempExt:
                                auth["contact"].append({tempExt["common:external-id-type"]: tempExt["common:external-id-url"]})

                # Test if the author is already in the list
                temp = False

                # Calcul the ponderation
                newScore = 0
                year = "-1"
                if "year" in article:
                    now = datetime.datetime.now()
                    year = article["year"]
                    diff = now.year - int(article["year"])
                    if diff > 2:
                        pondYear = np.sqrt(np.log(2) / np.log(now.year - int(article["year"])))
                    elif diff > 2 and diff <= 4:
                        pondYear = 0.9
                    elif diff == 2:
                        pondYear = 0.95
                    else:
                        pondYear = 1

                    newScore = (np.exp(i[1])*pondYear)/np.exp(1)

                # impact author on score
                if co > 0:
                    score_temp = i[1]*0.7
                    co_auth = "Co-author"
                else :
                    score_temp = i[1]
                    co_auth = "Author"

                # impact sub_cat on score
                for cat in sub_cat:
                    for x in article["sub_cat"]:
                        if cat != -1 and x != -1:
                            if cat.lower() == x.lower():
                                score_temp *= 1.1

                for res in resultats:

                    # If true, we add score and article
                    if res["id"] == auth["ids"][0]:
                        res["score"] += (score_temp*0.2)
                        res["score"] = round(res["score"], 3)

                        res["scorePond"] += (newScore*0.2)
                        res["scorePond"] = round(res["scorePond"], 3)

                        title = article["title"].replace('[', "")
                        title = title.replace(']', "")

                        res["article"].append({
                            "title": title,
                            "abstract": article["paperAbstract"],
                            "journal": article["venue"],
                            "year": str(year),
                            "co_auth": co_auth,
                            "fields": str(article["fields"]),
                            "sub_cat": str(article["sub_cat"]),
                            "score": round(score_temp, 3),
                            "doi": article["doiUrl"]})

                        temp = True

                # Else we add a new author
                if not temp:
                    #if int(year) > 2014:

                    if "orig_id" not in auth:
                        auth["orig_id"] = auth["ids"]
                    auth_id = get_authors_id(es, auth["orig_id"])
                    if not auth_id:
                        cita = "Unknown"
                        conflit = -1
                    else:
                        cita = str(auth_id[0]["_source"]["citations"]) + "+"
                        conflit = 0
                        it = 0
                        now = datetime.datetime.now()
                        for x in auth_id[0]["_source"]["auth_conflit"]:
                            for y in auth_input:
                                if x['auth_name'].lower() == y.lower():
                                    diff = now.year - int(x["auth_year"])
                                    conflit += x["auth_iter"]*(2/diff)
                                    it += 1
                        if it > 1:
                            conflit = round(conflit/(it-(it/4)), 3)
                        else:
                            conflit = round(conflit, 3)

                    title = article["title"].replace('[', "")
                    title = title.replace(']', "")

                    if type([]) == type(auth["orig_id"]):
                        original_id = auth["orig_id"][0]
                    else:
                        original_id = auth["orig_id"]

                    resultats.append(
                        {"verification": auth["verif"],
                         "name": auth["name"],
                         "original_id": original_id,
                         "id": auth["ids"][0],
                         "affiliation": auth["affiliation"],
                         "country": auth["country"],
                         "conflit": conflit,
                         "list_auth": authors,
                         "pos": co,
                         "fields": [field],
                         "score": round(score_temp, 3),
                         "scorePond": round(newScore, 3),
                         "citations": cita,
                         "article": [{
                             "title": title,
                             "abstract": article["paperAbstract"],
                             "journal": article["venue"],
                             "year": str(year),
                             "co_auth": co_auth,
                             "fields": str(article["fields"]),
                             "sub_cat": str(article["sub_cat"]),
                             "score": round(score_temp, 3),
                             "doi": str(article["doiUrl"]),
                             "inCitations": len(article["inCitations"])
                         }],
                         "contact": auth["contact"]})
            co += 1

    del dictionary
    del list_id
    del model
    del preprocess_value
    del new_dict
    del result

    return resultats[0:50]
