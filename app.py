#! /usr/bin/python
# -*- coding:utf-8 -*-

# IMPORT

from flask import Flask
# from flask import make_response
from flask import render_template

# APP

app = Flask(__name__)

# ROUTES


@app.route('/')
def index():
    return render_template('index.html', titre="Reviewer Matcher !")


@app.route('/model_test/')
def model_test():
    temp = [1, 2, 3]
    return render_template('model_test.html', titre="Model Test", data=temp)


@app.route('/request_base/')
def request_base():
    temp = [1, 2, 3]
    return render_template('request_base.html', titre="Request Base", data=temp)


@app.route('/reviewer_matcher/')
def reviewer_matcher():
    temp = [1, 2, 3]
    return render_template('reviewer_matcher.html', titre="Reviewer Matcher", data=temp)


@app.route('/results/')
def results():
    temp = [1, 2, 3]
    return render_template('results.html', titre="Results", data=temp)


# ERRORS

@app.errorhandler(401)
@app.errorhandler(404)
@app.errorhandler(500)
def ma_page_erreur(error):
    return "Erreur {}".format(error.code), error.code


# EXEC

if __name__ == '__main__':
    app.run(debug=True)
