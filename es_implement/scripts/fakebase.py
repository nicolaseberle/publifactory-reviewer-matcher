def fake_authors(es, index_name_fake, doc_type_fake):
    k = 1

    fd = [
        {
            "id": "1",
            "name": "Author 1",
            "entities": [
                [
                    "Sujet 1",
                    "2011",
                    "Titre 1"
                ],
                [
                    "Sujet 2",
                    "2011",
                    "Titre 1"
                ],
                [
                    "Sujet 3",
                    "2011",
                    "Titre 1"
                ],
                [
                    "Sujet 4",
                    "2011",
                    "Titre 1"
                ],
                [
                    "Sujet 2",
                    "2013",
                    "Titre 2"
                ]
            ]
        },
        {
            "id": "2",
            "name": "Author 2",
            "entities": [
                [
                    "Sujet 3",
                    "2011",
                    "Titre 3"
                ],
                [
                    "Sujet 5",
                    "2011",
                    "Titre 3"
                ],
                [
                    "Sujet 3",
                    "2015",
                    "Titre 4"
                ]
            ]
        },
        {
            "id": "3",
            "name": "Author 3",
            "entities": [
                [
                    "Sujet 1",
                    "2018",
                    "Titre 5"
                ],
                [
                    "Sujet 3",
                    "2018",
                    "Titre 5"
                ],
                [
                    "Sujet 4",
                    "2018",
                    "Titre 5"
                ],
                [
                    "Sujet 5",
                    "2018",
                    "Titre 5"
                ],
                [
                    "Sujet 1",
                    "2017",
                    "Titre 6"
                ],
                [
                    "Sujet 3",
                    "2017",
                    "Titre 6"
                ]
            ]
        },
        {
            "id": "4",
            "name": "Author 4",
            "entities": [
                [
                    "Sujet 3",
                    "2014",
                    "Titre 7"
                ],
                [
                    "Sujet 5",
                    "2014",
                    "Titre 7"
                ],
                [
                    "Sujet 3",
                    "2016",
                    "Titre 8"
                ],
                [
                    "Sujet 4",
                    "2016",
                    "Titre 8"
                ]
            ]
        },
        {
            "id": "5",
            "name": "Author 5",
            "entities": [
                [
                    "Sujet 1",
                    "2013",
                    "Titre 9"
                ]
            ]
        }
    ]

    for line in fd:
        es.index(index=index_name_fake, doc_type=doc_type_fake, body=line, id=k)
        k = k + 1
