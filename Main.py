from flask import Flask, render_template, request, redirect

import webbrowser

from threading import Timer

import Utilities

app = Flask(__name__)

companies = Utilities.scrape_companies()

@app.route("/")
def index():
    return render_template("index.html", companies=companies)

@app.route("/company_details/<code>/<name>/<der>/<pbv>/<roe>/<per>/<passed>")
def company_details(code, name, der, pbv, roe, per, passed):
    return render_template("company_details.html", code=code, name=name, der=der, pbv=pbv, roe=roe, per=per, passed=passed)

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

Timer(1, open_browser).start()
app.run(port=5000)