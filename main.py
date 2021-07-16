from flask import (
    Flask,
    render_template,
    request,
    flash,
    get_flashed_messages,
    redirect,
    url_for,
    session,
)

import json
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3' #Connects to database using SQL protocol thing idk
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #To prevent warnings


secrex = json.loads(open("secrets.json", "r").read())
db = SQLAlchemy(app)


class Titles(db.Model):
    _id = db.Column(db.Integer(), primary_key=True)
    title_content = db.Column(db.String(1000))
    ranking = db.Column(db.Integer())
    author = db.Column(db.String(500))

    def __init__(self, title_content, author):
        self.title_content = title_content
        self.ranking = 0
        self.author = author

class User(db.Model):
    _id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        all = Titles.query.order_by(Titles.ranking).all()
        all.reverse()
        return render_template("home.html", titles=all)
    else:
        formrank = request.form["title_rank"]
        upvotedpost = Titles.query.filter_by(ranking=formrank).first()
        upvotedpost.ranking = upvotedpost.ranking + 1
        db.session.add(upvotedpost)
        db.session.commit()
        flash("Upvoted!")
        return redirect(url_for("home"))


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        usr = User.query.filter_by(username=request.form["username"]).first()
        if usr is not None:
            if request.form["password"] == usr.password:
                session["un"] = request.form["username"]
                flash("Logged in!")
                return redirect(url_for("home"))
            else:
                flash("The password you entered is wrong!")
                return redirect(url_for("login"))
        else:
            rusr = User(request.form["username"], request.form["password"])
            db.session.add(rusr)
            db.session.commit()
            session["un"] = request.form["username"]
            flash("Registered a new account!")
            return redirect(url_for("home"))


@app.route('/profile/<usr>')
def profile(usr):
    ttls = Titles.query.filter_by(author=usr).all()
    return render_template('profile.html', titles=ttls)

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "GET":
        try:
            return render_template("add.html", un=session["un"])
        except KeyError:
            return render_template("add.html", un="")
    else:
        ttl = Titles(request.form["title_name"], request.form["author"])
        db.session.add(ttl)
        db.session.commit()
        session["un"] = request.form["title_name"]
        flash("Title added!")
        return redirect(url_for("home"))

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if request.method == 'GET':
        return render_template('edit.html')
    else:
        ttl = Titles.query.filter_by(_id=request.form["title_id"]).first()
        ttl.title_content = request.form['new_title']
        db.session.add(ttl)
        db.session.commit()
        flash("Title edited!")
        return redirect(url_for("home"))

@app.route("/delete", methods=["POST"])
def delete():
    ttl = Titles.query.filter_by(title_content=request.form["title_content"]).first()
    db.session.delete(ttl)
    db.session.commit()
    flash("Title deleted!")
    return redirect(url_for("home"))

db.create_all()
app.run(debug=True)
