from flask import Flask, render_template, redirect, session, g, request, flash
from os import getenv
#import axomeapis.auth as auth
import axomeapis.antixsrf as antixsrf
import axomeapis.sitemap as sitemap

app = Flask(__name__)
app.config["SECRET_KEY"] = getenv("SECRET_KEY")

@app.route("/")
def index():
    return render_template("index.html")

app.run(host="0.0.0.0", port=8080)