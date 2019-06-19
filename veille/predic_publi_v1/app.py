#! /usr/bin/python
# -*- coding:utf-8 -*-

#IMPORT

from flask import Flask
from flask import make_response
from flask import render_template

#APP

app = Flask(__name__)


#ROUTES

@app.route('/')
def index():
    return render_template('index.html', titre="Reviewer Matcher !")

@app.route('/results/')
def results():
    temp = [1, 2, 3]
    return render_template('results.html', titre="Resultats !", result=temp)




#ERRORS

@app.errorhandler(401)
@app.errorhandler(404)
@app.errorhandler(500)
def ma_page_erreur(error):
    return "Erreur {}".format(error.code), error.code


#EXEC

if __name__ == '__main__':
    app.run(debug=True)
