from flask import Flask, render_template, redirect, session, g, request, flash
from os import getenv
import axomeapis.auth as auth
import axomeapis.antixsrf as antixsrf
import pymongo

app = Flask(__name__)
app.config["SECRET_KEY"] = getenv("SECRET_KEY")

client = pymongo.MongoClient("mongodb+srv://vocab-server:"+getenv("DB_SECRET")+"@axodb01.kpdbk.mongodb.net/Vocab?retryWrites=true&w=majority")

@app.before_request
def before_request():
  if "username" in session:
    g.user = session["username"]
  else:
    g.user = ""
  g.AUTH_URL = "https://auth.axome.de/signin?url=https%3A%2F%2Fvocab.axome.repl.co%2Flogin%2Frun"
    
@app.route("/")
def index():
  return render_template("index.html")

@app.route("/login")
def login():
  return render_template("login.html")

@app.route("/login/run")
def login_run():
  g.user = auth.login(request.args["usr"])
  flash("You have been signed in successfully", "success")
  return redirect("/")

app.run(host="0.0.0.0", port=8080)