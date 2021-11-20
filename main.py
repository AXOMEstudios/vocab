from flask import Flask, render_template, redirect, session, g, request, flash
from os import getenv
import axomeapis.auth as auth
import axomeapis.antixsrf as antixsrf
import pymongo, threading, requests, json
from bson import ObjectId

def pingAuth():
  requests.get("https://auth.axome.de/")
threading.Thread(target=pingAuth).start()

app = Flask(__name__)
app.config["SECRET_KEY"] = getenv("SECRET_KEY")

client = pymongo.MongoClient("mongodb+srv://vocab-server:"+getenv("DB_SECRET")+"@axodb01.kpdbk.mongodb.net/Vocab?retryWrites=true&w=majority")

app.jinja_env.globals.update(_list=list)

db = client["Vocab"]
users = db["users"]
sets = db["sets"]
data = db["data"]

### HELPER FUNCTIONS ###

def getVocabulary(voc, arr):
  for i in arr:
    if list(i)[0] == voc:
      return i[list(i)[0]]
  else:
    return "This card has been deleted."

### BASIC VIEWS ###

@app.before_request
def before_request():
  session.permanent = True
  if "username" in session:
    g.user = session["username"]
  else:
    g.user = ""
  g.AUTH_URL = "https://auth.axome.de/signin?url=https%3A%2F%2Fvocab.axome.repl.co%2Flogin%2Frun"

def getUserData(user,data):
  return users.find_one({"name": user})[data]

def getUser(user):
  return users.find_one({"name": user})

def getData(user):
  return data.find_one({"user": user})
  
@app.route("/")
def index():
  if g.user:
    d = getUser(g.user)
    i = getData(g.user)
    return render_template("home.html", learning=d["learning"], recently=d["recent"], diamonds=i["diamonds"])
  return render_template("index.html")

@app.route("/login")
def login():
  return render_template("login.html")

@app.route("/login/run")
def login_run():
  if request.args.get("guest"):
    g.user = "vocabguest"
    session["username"] = g.user
  else:
    g.user = auth.login(request.args["usr"])
    session["username"] = g.user
  flash("You have been signed in successfully as "+g.user, "success")
  if users.count_documents({'name': g.user }, limit = 1) == 0:
    users.insert_one({
      "name": g.user,
      "bio": "Hello, I'm @"+g.user,
      "sets": [],
      "learning": {},
      "recent": ""
    })
    data.insert_one({
      "user": g.user,
      "diamonds": 0,
      "messages": [],
    })
    return render_template("welcome.html")
  return redirect("/")

@app.route("/new/set")
def new_set():
  if (not g.user) or (g.user == "vocabguest"):
    return redirect("/login")
  return render_template("new/set.html", token=antixsrf.createEndpoint(g.user, "new-set"))

@app.route("/new/set/run", methods=["POST"])
def new_set_run():
  if (not g.user) or (g.user == "vocabguest"):
    return redirect("/login")

  if not antixsrf.validateEndpoint(request.form["token"], g.user, "new-set"):
    flash("Invallid Cross-Site-Request-Forgery prevention token.", "danger")
    return redirect("/new/set")

  for i in ["lang-from", "lang-to", "title", "description"]:
    if (not i in request.form.keys()) or (request.form[i] == ""):
      flash("You missed out the field '%s'" % i, "warning")
      return redirect("/new/set")
  
  if len(request.form["title"]) > 50:
    flash("The title must be shorter than 50 characters.", "warning")
  if len(request.form["description"]) > 2000:
    flash("The title must be shorter than 2000 characters.", "warning")

  allowed_langs = [
    "spain",
    "french",
    "german",
    "latin",
    "english"
  ]

  if (not request.form["lang-from"] in allowed_langs) or (not request.form["lang-to"] in allowed_langs):
    flash("Do not send modified requests to Vocab.", "danger")
    return "request declined", 400
    
  if request.form["lang-to"] == request.form["lang-from"]:
    flash("The both languages you selected are the same. Please select different ones.", "warning")
    return redirect("/new/set")

  inserted = sets.insert_one({
    "name": request.form["title"],
    "description": request.form["description"],
    "langs": (request.form["lang-from"],request.form["lang-to"]),
    "vocabs": [],
    "author": g.user,
    "editors": [g.user]
  }).inserted_id
  
  return redirect("/set/"+str(inserted))

@app.route("/set/<i>")
def set_view(i):
  d = sets.find_one({
    "_id": ObjectId(i)
  })
  return render_template("/views/set.html", d=d)

### EDITOR ###

open_editors = []

@app.route("/editor/<i>")
def editor(i):
  s = sets.find_one({
    "_id": ObjectId(i)
  })
  open_editors.append(g.user)
  return render_template("views/editor.html", d = s, token=antixsrf.createEndpoint(g.user, "add-vocabulary-card"))

@app.route("/editor/<i>/api", methods=["POST"])
def editor_api(i):
  d = json.loads(request.data)
  if not antixsrf.validateEndpoint(d["token"], g.user, "add-vocabulary-card", False):
    return "Invalid security key. Reload the page.", 400
  if d["action"] == "add-card":
    if (not d["fr"]) or (not d["to"]):
      return "Please provide both the word and it's translation.", 400
    sets.update_one({
      "_id": ObjectId(i)
    }, {
      "$push": {
        "vocabs": {
          d["fr"]: d["to"]
        }
      }
    })
  if d["action"] == "get-card":
    return getVocabulary(d["fr"], sets.find_one({
      "_id": ObjectId(i)
    })["vocabs"])

  if d["action"] == "delete-card":
    sets.update_one({
      "_id": ObjectId(i)
    }, {
      "$pull":
        {"vocabs":
          {d["card"]:
            {"$exists": True}
          }
        }
    })

  return "success"

### EXPLORE ###


app.run(host="0.0.0.0", port=8080)