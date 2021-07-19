from flask import Flask, render_template, request, redirect, url_for
from bs4 import BeautifulSoup
from crawling_n_db import *
from selenium import webdriver
from pprint import pprint
import cx_Oracle

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html')


@app.route("/search", methods=['POST', 'GET'])
def search():
    search_name = request.form['nm']
    return redirect(url_for('search_result', name = search_name))

@app.route("/search_result/<name>")
def search_result(name):
    return render_template('search_result.html', user_search = select_from_user_search(name), name = name)

def sort():
    print("hi")

@app.errorhandler(404) # 오류 처리 (에러코드: 404)
def page_not_found(error):
    return render_template('404_error.html'), 404


@app.route('/json')
def json():
    return render_template('json.html')

#background process happening without any refreshing
@app.route('/background_process_test')
def background_process_test():
    print ("Hello")
    return ("nothing")

# @app.route("/bookinfo")
# def bookinfo():
#     return render_template('bookinfo_db.html', bookinfo_db = select_from_bookinfo_db())
#
# @app.route("/onlinestore")
# def onlinestore():
#     return render_template('onlinestore_db.html', onlinestore_db = select_from_onlinestore_db())


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
