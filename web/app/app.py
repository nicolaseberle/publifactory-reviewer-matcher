#! /usr/bin/python
# -*- coding:utf-8 -*-

# IMPORT

from flask import Flask, Response, render_template, flash, request, jsonify, redirect
from wtforms import Form, TextAreaField, validators, StringField, SubmitField, IntegerField, FileField
from werkzeug.utils import secure_filename

from elasticsearch import Elasticsearch

import redis
from rq import Worker, Queue, Connection
from rq.job import Job

import time
import os
import datetime
import requests
import json
import gc

from markupsafe import Markup
import pickle

from waitress import serve

# APP CONFIG

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLD = 'uploads_pdf'
UPLOAD_FOLDER = os.path.join(APP_ROOT, UPLOAD_FOLD)
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
app.config.from_object(__name__)
app.debug = True
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

es_host = 'elasticsearch:9200'
es = Elasticsearch(hosts=[es_host])

listen = ['default']
redis_url = os.getenv('REDISTOGO_URL', 'redis://redis:6379')
conn = redis.from_url(redis_url)
q = Queue(connection=conn, is_async=False)


# PRELOAD

# list_id = pickle.load(open("app/models/saves/list_id.p", "rb"))
# dictionary = pickle.load(open("app/models/saves/dictionary.p", "rb"))
# model = pickle.load(open("app/models/saves/lsi_model.p", "rb"))


# CLASS (pour les formulaires)


class RequestESForm(Form):
    title = StringField('Titre Non Ordonné', (validators.Optional(),))
    title_ord = StringField('Titre Ordonné', (validators.Optional(),))
    abstract = TextAreaField('Abstract Non Ordonné', (validators.Optional(),))
    abstract_ord = TextAreaField('Abstract Ordonné', (validators.Optional(),))
    authors = StringField('Auteurs', (validators.Optional(),))
    keywords = StringField('Keywords Non Ordonné', (validators.Optional(),))
    keywords_ord = StringField('Keywords Ordonné', (validators.Optional(),))
    journal = StringField('Journal', (validators.Optional(),))
    year_alone = IntegerField('Année précise', (validators.Optional(),))
    year_range1 = IntegerField('Année de début', (validators.Optional(),))
    year_range2 = IntegerField('Année de fin', (validators.Optional(),))
    submit1 = SubmitField('Chercher')


class RequestESAuthors(Form):
    name = StringField('Nom', (validators.Optional(),))
    keywords = StringField('Keywords', (validators.Optional(),))
    article = StringField('Article', (validators.Optional(),))
    affil = StringField('Affiliation', (validators.Optional(),))

    
class UploadPDF(Form):
    pdf = FileField('Pdf')
    submit2 = SubmitField('Envoyer')


class SummarizeText(Form):
    text = TextAreaField('Texte', [validators.DataRequired()])
    nb_sent = IntegerField('Nombre de phrases', [validators.DataRequired()])
    submit = SubmitField('Résumer le texte')


class ArticleAsync(Form):
    title = StringField('Titre')


class RevMatcher(Form):
    abstract = TextAreaField('Abstract', [validators.DataRequired()])
    submit = SubmitField('Envoyer')

    
# FUNCTIONS


# Verification de l'intégrité du fichier (GROBID) 
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Libérer de la RAM
def free_memory():
    for name in dir():
        if not name.startswith('_'):
            del globals()[name]

    for name in dir():
        if not name.startswith('_'):
            del locals()[name]
                        
    gc.collect()
    gc.garbage[:]
    return "YAY"


# ROUTES (vues)


# Index
@app.route('/')
def index():
    return render_template('index.html', titre="Reviewer Matcher !")


# Vue Get Abstract
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
        title_ord = form1.title_ord.data
        abstract = form1.abstract.data
        abstract_ord = form1.abstract_ord.data
        authors = form1.authors.data
        keywords = form1.keywords.data
        keywords_ord = form1.keywords_ord.data
        journal = form1.journal.data
        if form1.year_alone.data:
            year1 = form1.year_alone.data
            year2 = form1.year_alone.data
        elif form1.year_range1.data and form1.year_range2.data:
            year1 = form1.year_range1.data
            year2 = form1.year_range2.data
        else:
            year1 = 1800
            year2 = now.year
        data = get_articles_es(title, title_ord, abstract, abstract_ord, authors, keywords, keywords_ord, journal, year1, year2)

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
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))

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

    verified_auth = []
    if data != -1 :
        from scripts.fvue_get_authors import get_authors_by_id
        for art in data :
            temp = get_authors_by_id(art["_source"]["doi"])
            verified_auth.append(temp)
            
    return render_template('request_base.html', titre="Request Base", form1=form1, form2=form2, data=data, results=results, doi=verified_auth)


# Vue Get Authors
@app.route('/request_base_authors', methods=['GET', 'POST'])
def request_base_authors():
    form = RequestESAuthors(request.form)
    data = -1
    from scripts.fvue_get_authors import get_authors_es_v2
    if request.method == 'POST' and form.validate():
        name = form.name.data
        keywords = form.keywords.data
        article = form.article.data
        affil = form.affil.data
        data = get_authors_es_v2(name, keywords, article, affil)
    #return render_template('request_base_authors.html', titre="Request Authors", form=form, data=data)
    return data


# Vue reviewer matcher
@app.route('/api/test_reviewer_matcher', methods=['GET', 'POST'])
def test_reviewer_matcher():
    form = RevMatcher(request.form)
    data = -1
    from models.model import getReviewers
    if request.method == 'POST' and form.validate():            
        abstract = form.abstract.data
        data = getReviewers(es, abstract)
        data = sorted(data, key = lambda i: i['score'], reverse=True)
    return render_template('test_reviewer_matcher.html', titre="Reviewer Matcher Alpha", form=form, data=data)

# Vue Show article
@app.route('/get_one_article/<id_art>')
def get_one_article(id_art):
    from scripts.fvue_get_article import get_article_es
    data = get_article_es(id_art)
    return render_template('show_article.html', titre="Article", data=data, id_art=id_art)


# Vue Show author
@app.route('/get_one_author/<orcid>')
def get_one_author(orcid):
    from scripts.fvue_get_authors import get_author_es
    data = get_author_es(orcid)
    return render_template('show_author.html', titre="Auteur", data=data, orcid=orcid)


# Vue Summarize text
@app.route('/summarize_text', methods=['GET', 'POST'])
def summarize_text():
    form = SummarizeText(request.form)
    data = -1
    from scripts.summarize_text import multiple_summary, generate_summary
    if request.method == 'POST' and form.validate():
        text = form.text.data
        nb_sent = form.nb_sent.data
        #data = generate_summary(text, nb_sent)
        data = multiple_summary(text, nb_sent)

    return render_template('summarize_text.html', titre="Summarize Text", form=form, data=data)


# Vue Synchro references
@app.route('/synchro_ref', methods=['GET', 'POST'])
def synchro_ref():
    form = ArticleAsync(request.form)
    data = -1
    
    return render_template('synchro_ref.html', titre="Synchro References", form=form, data=data)


# ASYNC FONCTIONS


@app.route('/api/sync_ref')
def sync_ref():
    data = request.args.get('title', '', type=str)
    if data != '':
        from scripts.fvue_get_article import get_article_async
        temp = data.split(' ')
        if len(temp) > 1:
            last = temp[-1]
            data = ' '.join(temp[0:-1])
        else:
            last = data
            data = ''
        try:
            data = get_article_async(data, last)
            result = []
            for temp in data:
                result.append({"title": temp["_source"]["title"], "authors": temp["_source"]["authors"], "year": temp["_source"]["year"], "journalName": temp["_source"]["journalName"], "journalVolume": temp["_source"]["journalVolume"], "journalPages": temp["_source"]["journalPages"]})
            data = result
        except:
            data = ''
            
    return Markup(json.dumps(data))


# API


# API test
@app.route('/api/ping/')
def ping_api():
    return "YAY"


@app.route('/api/clear_memory')
def clear_memory():
    result = free_memory()
    return result

    
# API Build Model
@app.route('/api/buildModel/')
def buildLSI():
    from models.model import buildModel
    buildModel(es)

    free_memory()
    return "YAY"


@app.route('/api/updateModel/')
def updateLSI():
    from models.model import updateModel
    for i in range(0, 10):
        updateModel(es)
        free_memory()
    
    return "YAY"


@app.route('/api/request_reviewer')
def request_reviewer():
    from scripts.queue_scripts import request_reviewer_func
    abstr = request.args.get('abstract')
    auth = request.args.getlist('authors')
    _result = q.enqueue(request_reviewer_func, abstr, auth)
    free_memory()
    return json.dumps(_result.id)


@app.route("/api/results_rev/<job_key>", methods=['GET'])
def get_results(job_key):
    if conn:
        job = Job.fetch(job_key, connection=conn)
        while not job.is_finished:
            time.sleep(1)
        _result = job.result
        free_memory()
        return json.dumps(_result)


@app.route('/api/suggest_ae')
def suggest_ae():
    id_article = request.args.get('id_article')
    data = [
        {"name": "associate_editor1", "affiliation": "univ2", "conflit": "32%", "score": "0.853425", "email": ["email@example.com", "email2@example.com"], "rs": ["https://linkedin.com", "https://blognul.com"]}
    ]
    data = json.dumps(data)
    return Response(response=data, status=200, mimetype="application/json")


@app.route('/api/suggest_pertinent_art')
def suggest_pertient_art():
    domain = request.args.get('domain')
    keywords = request.args.get('keywords')
    rec_or_acc = request.args.get('recent_or_accurate') 
    data = [
        {
            "title": "art1",
            "abstract": "abs1",
            "authors": ["aut1", "aut2", "aut3"],
            "keywords": ["key1", "key2"],
            "journal": "journal1", 
            "year": "1996"
        }
        
    ]
    data = json.dumps(data)
    return Response(response=data, status=200, mimetype="application/json")


@app.route('/api/extract_infos_pdf', methods=['GET', 'POST'])
def extract_infos_pdf():
    from scripts.queue_scripts import extract_pdf_func
    file = request.files['pdf_file']
    if file.filename == '':
        return "empty file"
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        from scripts.upload_pdf import get_infos_pdf
        results = get_infos_pdf(filename, app.config['UPLOAD_FOLDER'])
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        _result = q.enqueue(extract_pdf_func, results)
        free_memory()
        return json.dumps(_result.id)


@app.route("/api/results_pdf/<job_key>", methods=['GET'])
def get_results_pdf(job_key):
    if conn:
        job = Job.fetch(job_key, connection=conn)
        while not job.is_finished:
            time.sleep(1)
        _result = job.result
        free_memory()
        return Response(response=_result, status=200, mimetype="application/json")

        
@app.route('/api/get_articles')
def get_articles():
    now = datetime.datetime.now()
    from scripts.fvue_get_article import get_articles_es
    title = request.args.get('title')
    title_ord = request.args.get('title_ord')
    abstract = request.args.get('abstract')
    abstract_ord = request.args.get('abstract_ord')
    authors = request.args.get('authors')
    keywords = request.args.get('keywords')
    keywords_ord = request.args.get('keywords_ord')
    journal = request.args.get('journal')
    if request.args.get('year_alone'):
        year1 = request.args.get('year_alone')
        year2 = request.args.get('year_alone')
    elif request.args.get('year_range1') and request.args.get('year_range2'):
        year1 = request.args.get('year_range1')
        year2 = request.args.get('year_range2')
    else:
        year1 = 1800
        year2 = now.year
    data = get_articles_es(title, title_ord, abstract, abstract_ord, authors, keywords, keywords_ord, journal, year1, year2)
    return json.dumps(data)


@app.route('/api/summary_generator', methods=['GET', 'POST'])
def summary_generator():
    from scripts.summarize_text import multiple_summary
    text = request.args.get('text')
    text = text.replace("{", " ")
    text = text.replace("}", " ")
    text = text.replace("[", " ")
    text = text.replace("]", " ")
    text = text.replace('"', " ")
    text = text.replace("'", " ")
    nb_sent = int(request.args.get('nb_sent'))
    data = multiple_summary(text, nb_sent)

    data = json.dumps(data)
    return Response(response=data, status=200, mimetype="application/json")


@app.route('/api/get_mail_id', methods=['GET', 'POST'])
def get_mail_id():
    from scripts.fvue_get_authors import get_mail_id

    id = request.args.get('id')
    data = get_mail_id(id)
    return json.dumps(data)


# EXEC

if __name__ == '__main__':
    app.run("0.0.0.0", port=5000, debug=True)
    #serve(app, host='0.0.0.0', port=5000)
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()
