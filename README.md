# Reviewer Matcher

An IA to help associate editors/researchers to find quickly the best reviewers

## Functionnal summary

The project work with 4 big steps :
* Set up 2 databases (articles & authors)
* Set up a model to create a dictionnary and get in output a list of themes link with the publication (with a publication in input)
* Set up a model that order themes of each author
* Correlate the 2 results to get in output a list of authors that cover all the themes of the publication when you have a publication in input.

## Composers

In the folder 'veille', there is all the research done to set up the project.

## Steps

* Set up the working environment (webapp flask + venv)
* Set up the Docker structure
* Set up databases (List of publications + list of authors)
* Shape databases with elastic search
* Requête sous Node de recherche d’article
* Set up the model (training + test)
  * First, work with only few data
  * First, work with only keywords and not others features
  * Set up our own dictionary with NLP
* Get in output the main theme of the article
* Link this theme to a list of reviewer
* Upgrade the model to get in output the differents themes of the article (if there is different themes)
* Add a list of reviewer with the notion of "Matched Skill"
* Add new features (conflict of interest, H-Index, qualifying the expertise of a reviewer with the year)


## Use the project

*Nothing for the moment*

## Work on the project

*Nothing for the moment*