#! /usr/bin/python
# -*- coding:utf-8 -*-

# IMPORT

from flask import Flask, render_template, flash, request, jsonify
# from flask import make_response
from wtforms import Form, TextAreaField, validators, StringField, SubmitField, IntegerField
from elasticsearch import Elasticsearch
import os
import datetime

# APP CONFIG

DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

# es_host = os.environ['DOCKER_MACHINE_IP']
es_host = 'elasticsearch:9200'
es = Elasticsearch(hosts=[es_host])


# CLASS


class RequestESForm(Form):
    title = StringField('Titre', (validators.Optional(),))
    abstract = StringField('Abstract', (validators.Optional(),))
    authors = StringField('Auteurs', (validators.Optional(),))
    keywords = StringField('Keywords', (validators.Optional(),))
    journal = StringField('Journal', (validators.Optional(),))
    year_alone = IntegerField('Année précise', (validators.Optional(),))
    year_range1 = IntegerField('Année de début', (validators.Optional(),))
    year_range2 = IntegerField('Année de fin', (validators.Optional(),))


class RequestESAuthors(Form):
    name = StringField('Nom', (validators.Optional(),))
    keywords = StringField('Keywords', (validators.Optional(),))
    journal = StringField('Journal', (validators.Optional(),))
    
# ROUTES


@app.route('/')
def index():
    return render_template('index.html', titre="Reviewer Matcher !")


@app.route('/request_base/', methods=['GET', 'POST'])
def request_base():
    form = RequestESForm(request.form)
    data = -1
    now = datetime.datetime.now()
    from scripts.fvue_get_article import get_articles_es
    if request.method == 'POST' and form.validate():
        title = form.title.data
        abstract = form.abstract.data
        authors = form.authors.data
        keywords = form.keywords.data
        journal = form.journal.data
        if form.year_alone.data :
            year1 = form.year_alone.data
            year2 = form.year_alone.data
        elif (form.year_range1.data) and (form.year_range2.data) :
            year1 = form.year_range1.data
            year2 = form.year_range2.data
        else :
            year1 = 1800
            year2 = now.year
        data = get_articles_es(title, abstract, authors, keywords, journal, year1, year2)
    return render_template('request_base.html', titre="Request Base", form=form, data=data)


@app.route('/request_base_authors', methods=['GET', 'POST'])
def request_base_authors():
    form = RequestESAuthors(request.form)
    data = -1
    from scripts.fvue_get_authors import get_authors_es
    if request.method == 'POST' and form.validate():
        name = form.name.data
        keywords = form.keywords.data
        journal = form.journal.data
        data = get_authors_es(name, keywords, journal)
    return render_template('request_base_authors.html', titre="Request Authors", form=form, data=data)


@app.route('/get_one_article/<id_art>')
def get_one_article(id_art):
    from scripts.fvue_get_article import get_article_es
    data = get_article_es(id_art)
    return render_template('show_article.html', titre="Article", data=data, id_art=id_art)


# API


@app.route('/api/suggestReviewers/')
def suggest_reviewers():
    return "YAY"


@app.route('/api/es_info')
def es_info():
    return jsonify(es.info())


# EXEC

if __name__ == '__main__':
    app.run("0.0.0.0", port=5000, debug=True)
