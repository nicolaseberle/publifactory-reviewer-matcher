#! /usr/bin/python
# -*- coding:utf-8 -*-

# IMPORT

from flask import Flask, render_template, flash, request
# from flask import make_response
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField

# APP CONFIG

DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'


# CLASS

class RequestESForm(Form):
    title = StringField('Title', [validators.DataRequired()])


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
        keyword = form.keyword.data
        data = get_articles_es(keyword)
    return render_template('request_base.html', titre="Request Base", form=form, data=data)


@app.route('/reviewer_matcher/')
def reviewer_matcher():
    temp = [1, 2, 3]
    return render_template('reviewer_matcher.html', titre="Reviewer Matcher", data=temp)


@app.route('/results/')
def results():
    temp = [1, 2, 3]
    return render_template('results.html', titre="Results", data=temp)


# ERRORS

# @app.errorhandler(401)
# @app.errorhandler(404)
# @app.errorhandler(500)
# def ma_page_erreur(error):
#     return "Erreur {}".format(error.code), error.code


# EXEC

if __name__ == '__main__':
    app.run(debug=True)
