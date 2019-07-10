#! /usr/bin/python
# -*- coding:utf-8 -*-

# IMPORT

from flask import Flask, render_template, flash, request, jsonify
# from flask import make_response
from wtforms import Form, TextAreaField, validators, StringField, SubmitField
from elasticsearch import Elasticsearch
import os

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
    title = StringField('Titre', [validators.DataRequired()])


# ROUTES


@app.route('/')
def index():
    return render_template('index.html', titre="Reviewer Matcher !")


@app.route('/model_test/')
def model_test():
    temp = [1, 2, 3]
    return render_template('model_test.html', titre="Model Test", data=temp)


@app.route('/request_base/', methods=['GET', 'POST'])
def request_base():
    form = RequestESForm(request.form)
    data = -1
    from scripts.fvue_get_article import get_articles_es
    if request.method == 'POST' and form.validate():
        title = form.title.data
        data = get_articles_es(title)
    return render_template('request_base.html', titre="Request Base", form=form, data=data)


@app.route('/request_base_mongo/', methods=['GET', 'POST'])
def request_base_mongo():
    form = RequestESForm(request.form)
    data = -1
    from scripts.fvue_get_article import get_articles_mongo
    if request.method == 'POST' and form.validate():
        title = form.title.data
        data = get_articles_mongo(title)
    return render_template('request_mongo.html', titre="Request Mongo", form=form, data=data)


@app.route('/reviewer_matcher/')
def reviewer_matcher():
    temp = [1, 2, 3]
    return render_template('reviewer_matcher.html', titre="Reviewer Matcher", data=temp)


@app.route('/results/')
def results():
    temp = [1, 2, 3]
    return render_template('results.html', titre="Results", data=temp)

# API


@app.route('/api/suggestReviewers/')
def suggest_reviewers():
    return "YAY"


@app.route('/api/es_info')
def es_info():
    return jsonify(es.info())

# ERRORS

# @app.errorhandler(401)
# @app.errorhandler(404)
# @app.errorhandler(500)
# def ma_page_erreur(error):
#     return "Erreur {}".format(error.code), error.code

# EXEC

if __name__ == '__main__':
    app.run("0.0.0.0", port=5000, debug=True)
