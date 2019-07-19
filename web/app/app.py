#! /usr/bin/python
# -*- coding:utf-8 -*-

# IMPORT

from flask import Flask, render_template, flash, request, jsonify, redirect, url_for
from wtforms import Form, TextAreaField, validators, StringField, SubmitField, IntegerField, FileField
from wtforms.validators import InputRequired
from elasticsearch import Elasticsearch
import os
import datetime
from werkzeug.utils import secure_filename

# APP CONFIG

# UPLOAD_FOLDER = '/uploads_pdf'
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLD = 'uploads_pdf'
UPLOAD_FOLDER = os.path.join(APP_ROOT, UPLOAD_FOLD)
ALLOWED_EXTENSIONS = {'pdf'}

DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# es_host = os.environ['DOCKER_MACHINE_IP']
es_host = 'elasticsearch:9200'
es = Elasticsearch(hosts=[es_host])


# CLASS


class RequestESForm(Form):
    title = StringField('Titre', (validators.Optional(),))
    abstract = TextAreaField('Abstract', (validators.Optional(),))
    authors = StringField('Auteurs', (validators.Optional(),))
    keywords = StringField('Keywords', (validators.Optional(),))
    journal = StringField('Journal', (validators.Optional(),))
    year_alone = IntegerField('Année précise', (validators.Optional(),))
    year_range1 = IntegerField('Année de début', (validators.Optional(),))
    year_range2 = IntegerField('Année de fin', (validators.Optional(),))
    submit1 = SubmitField('Chercher')


class RequestESAuthors(Form):
    name = StringField('Nom', (validators.Optional(),))
    keywords = StringField('Keywords', (validators.Optional(),))
    journal = StringField('Journal', (validators.Optional(),))


class UploadPDF(Form):
    pdf = FileField('Pdf')
    submit2 = SubmitField('Envoyer')


# FUNCTIONS


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ROUTES


@app.route('/')
def index():
    return render_template('index.html', titre="Reviewer Matcher !")


@app.route('/request_base/', methods=['GET', 'POST'])
def request_base():
    form1 = RequestESForm(request.form)
    form2 = UploadPDF(request.form)
    data = -1
    results = -1
    now = datetime.datetime.now()
    from scripts.fvue_get_article import get_articles_es
    if request.method == 'POST' and form1.validate() and form1.submit1.data:
        title = form1.title.data
        abstract = form1.abstract.data
        authors = form1.authors.data
        keywords = form1.keywords.data
        journal = form1.journal.data
        if form1.year_alone.data :
            year1 = form1.year_alone.data
            year2 = form1.year_alone.data
        elif (form1.year_range1.data) and (form1.year_range2.data) :
            year1 = form1.year_range1.data
            year2 = form1.year_range2.data
        else :
            year1 = 1800
            year2 = now.year
        data = get_articles_es(title, abstract, authors, keywords, journal, year1, year2)

    if request.method == 'POST' and form2.validate() and form2.submit2.data:
        if 'pdf' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['pdf']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            from scripts.upload_pdf import get_infos_pdf
            results = get_infos_pdf(filename, app.config['UPLOAD_FOLDER'])

    if results != -1:
        if "title" in results:
            form1.title.data = results["title"]
        if "journal" in results:
            form1.journal.data = results["journal"]
        if "authors" in results:
            form1.authors.data = ' '.join(results["authors"])
        if "abstract" in results:
            form1.abstract.data = results["abstract"]
        if "year" in results:
            form1.year_alone.data = results["year"]
        if "keywords" in results:
            form1.keywords.data = ' '.join(results["keywords"])

    return render_template('request_base.html', titre="Request Base", form1=form1, form2=form2, data=data, results=results)


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
