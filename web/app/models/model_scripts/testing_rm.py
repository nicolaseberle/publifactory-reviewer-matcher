from ..model_scripts.preprocess import preprocess
from ..model_scripts.requestsES import get_abstract
from ..model_scripts.requestsES import get_authors_doi
from ..model_scripts.requestsES import get_authors_name
from ..model_scripts.requestsES import get_authors_orcid

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


def getRev_v3(es, value, dictionary, list_id, model):
    preprocess_value = [preprocess(value)]
    new_dict = [dictionary.doc2bow(doc) for doc in preprocess_value]
    result = model.__getitem__(new_dict)
        
    resultats = []

    y = 0

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
                        name = name1[0]+" "+name2[0]
 
                # Add the author
                if orcid and name:
                    authors.append({"name": name, "ids": [orcid], "contact": []})

                    # Check and add the mail
                    if list(find("email:email", a)):
                        tempMail = list(find("email:email", a))[0]
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
       
        
         # If not, get authors from the article
        else:
            authors = article["authors"]
        for auth in authors:
            if len(auth["ids"]) > 0:

                # Check if contact exist
                if "contact" not in auth:
                    auth["contact"] = []
                
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

                    auth["ids"] = [orc]
                    auth["name"] = name
                    
                    # Check and add the mail
                    if list(find("email:email", au)):
                        tempMail = list(find("email:email", au))[0]
                        for m in list(find("email:email", tempMail)):
                            auth["contact"].append({"mail": m})
                            
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

                # Test if the author is already in the list
                temp = False
            
                for res in resultats:
                # If true, we add score and article
                    if res["id"] == auth["ids"][0]:
                        res["score"] += i[1]
                        res["article"].append(article["title"])
                        res["abstract"].append(article["paperAbstract"])
                        temp = True                
                    
                # Else we add a new author
                if not temp:
                    resultats.append(
                        {"name": auth["name"], "id": auth["ids"][0], "affiliation": "soon", "conflit": "soon",
                         "score": i[1], "article": [article["title"]], "abstract": [article["paperAbstract"]],"contact": auth["contact"]})

    return resultats[0:20]


def getRev_test(es, value, dictionary, list_id, model):
    preprocess_value = [preprocess(value)]
    new_dict = [dictionary.doc2bow(doc) for doc in preprocess_value]
    result = model.__getitem__(new_dict)
        
    resultats = []

    y = 0

    for i in result[0]:
        # Get article from ES
        article = get_abstract(es, list_id[i[0]])
        
        # Get verified authors
        if get_authors_doi(es, article["doi"]):
            orcid_doi = get_authors_doi(es, article["doi"])
            authors = []
            
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
                        name = name1[0]+" "+name2[0]
 
                # Add the author
                if orcid and name:
                    authors.append({"name": name, "ids": [orcid], "contact": []})

                    # Check and add the mail
                    if list(find("email:email", a)):
                        tempMail = list(find("email:email", a))[0]
                        for m in list(find("email:email", tempMail)):
                            authors[-1]["contact"].append({"mail": m})

                    # Check and add website
                    if list(find("researcher-url:researcher-url", a)):
                        tempWeb = list(find("researcher-url:researcher-url", a))[0]
                        if type(tempWeb) == type([]):
                            for r in range(0, len(tempWeb)):
                                authors[-1]["contact"].append({tempWeb[r]["researcher-url:url-name"]: tempWeb[r]["researcher-url:url"]})
                        else:
                            authors[-1]["contact"].append({tempWeb["researcher-url:url-name"]: tempWeb["researcher-url:url"]})
        # If not, get authors from the article
        else:
            authors = article["authors"]

        for auth in authors:
            if len(auth["ids"]) > 0:

                # Check if contact exist
                if "contact" not in auth:
                    auth["contact"] = []
                
                # Check if the name exist in orcid
                if get_authors_name(es, auth["name"]):
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

                    auth["ids"] = [orc]
                    auth["name"] = name
                    
                    # Check and add the mail
                    if list(find("email:email", au)):
                        tempMail = list(find("email:email", au))[0]
                        for m in list(find("email:email", tempMail)):
                            auth["contact"].append({"mail": m})
                            
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

                # Test if the author is already in the list
                temp = False
            
                for res in resultats:
                # If true, we add score and article
                    if res["id"] == auth["ids"][0]:
                        res["score"] += i[1]
                        res["article"].append(article["title"])
                        temp = True                
                    
                # Else we add a new author
                if not temp:
                    resultats.append(
                        {"name": auth["name"], "id": auth["ids"][0], "affiliation": "soon", "conflit": "soon",
                         "score": i[1], "article": [article["title"]], "contact": auth["contact"]})

    return resultats[0:20]

def getRev_v2(es, value, dictionary, list_id, model):
    preprocess_value = [preprocess(value)]
    new_dict = [dictionary.doc2bow(doc) for doc in preprocess_value]
    result = model.__getitem__(new_dict)
    resultats = []
    y = 0

    for i in result[0]:
        # Get article from ES
        article = get_abstract(es, list_id[i[0]])
        # Get verified authors
        if get_authors_doi(es, article["doi"]):
            orcid_doi = get_authors_doi(es, article["doi"])
            authors = []
            
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
                        name = name1[0]+" "+name2[0]
 
                # Add the author
                if orcid and name:
                    authors.append({"name": name, "ids": [orcid], "contact": []})

                    # Check and add the mail
                    if list(find("email:email", a)):
                        tempMail = list(find("email:email", a))[0]
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
        # If not, get authors from the article
        else:
            authors = article["authors"]

        for auth in authors:
            if len(auth["ids"]) > 0:
                # Check if contact exist
                if "contact" not in auth:
                    auth["contact"] = []

            # Test if the author is already in the list
                temp = False
            
                for res in resultats:
                    # If true, we add score and article
                        if res["id"] == auth["ids"][0]:
                            res["score"] += i[1]
                            res["article"].append(article["title"])
                            res["abstract"].append(article["paperAbstract"])
                            temp = True
                    
                # Else we add a new author
                if not temp:
                    resultats.append(
                        {"name": auth["name"], "id": auth["ids"][0], "affiliation": "soon", "conflit": "soon",
                         "score": i[1], "article": [article["title"]], "abstract": [article["paperAbstract"]], "contact": auth["contact"]})

    return resultats[0:20]



def getRev(es, value, dictionary, list_id, model):
    test = [preprocess(value)]
    test2 = [dictionary.doc2bow(doc) for doc in test]
    result = model.__getitem__(test2)
    
    list_authors = []
    y = 0
    
    for i in result[0]:
        article = get_abstract(es, list_id[i[0]])
        authors_list = article["authors"]
        for auth in authors_list:
            list_authors.append(
                {"name": auth["name"], "id": auth["ids"], "affiliation": "soon", "conflit": "soon",
                 "score": i[1], "article": article["title"], "email": "soon", "rs": "soon"})
        if y > 5:
            break
        y += 1
            
    return list_authors
