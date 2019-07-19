# IMPORTS

from xml.etree.ElementTree import fromstring
import requests
import os

# MAIN


def get_infos_pdf(filename, upload_folder):
    rep = requests.post('http://grobid:8070/api/processHeaderDocument',
                        files=dict(input=open(os.path.join(upload_folder, filename), 'rb')))
    rep = fromstring(rep.text)

    ns = {'d': 'http://www.tei-c.org/ns/1.0'}

    results = {}
    list_authors = []
    list_keywords = []

    for teiHeader in rep.iterfind("d:teiHeader", ns):
        for fileDesc in teiHeader.iterfind("d:fileDesc", ns):
            for titleStmt in fileDesc.iterfind("d:titleStmt", ns):
                for title in titleStmt.iterfind("d:title", ns):
                    results["title"] = title.text
            for publicationStmt in fileDesc.iterfind("d:publicationStmt", ns):
                for publisher in publicationStmt.iterfind("d:publisher", ns):
                    results["journal"] = publisher.text
                for date in publicationStmt.iterfind("d:date", ns):
                    results["year"] = date.text
            for sourceDesc in fileDesc.iterfind("d:sourceDesc", ns):
                for biblStruct in sourceDesc.iterfind("d:biblStruct", ns):
                    for analytic in biblStruct.iterfind("d:analytic", ns):
                        for author in analytic.iterfind("d:author", ns):
                            for persName in author.iterfind("d:persName", ns):
                                for forename in persName.iterfind("d:forename", ns):
                                    list_authors.append(forename.text)
                                for surname in persName.iterfind("d:surname", ns):
                                    list_authors.append(surname.text)
        for profileDesc in rep[0].iterfind("d:profileDesc", ns):
            for textClass in profileDesc.iterfind("d:textClass", ns):
                for keywords in textClass.iterfind("d:keywords", ns):
                    for term in keywords.iterfind("d:term", ns):
                        list_keywords.append(term.text)
            for abstract in profileDesc.iterfind("d:abstract", ns):
                if abstract:
                    results["abstract"] = abstract[0].text

    results["authors"] = list_authors
    results["keywords"] = list_keywords

    return results