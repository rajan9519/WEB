#set DATABASE_URL=postgres://xfiaqmwbuvpdjf:d03035de4ccfd64fffa4dfe025035f2b9cb476f24b11e2a5a7ac6445684a61a5@ec2-107-22-234-204.compute-1.amazonaws.com:5432/dbdsifjtu2f55m


import os

from flask import Flask, session, render_template,request,redirect,url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def home():
    if session:
        return redirect(url_for('user'))
    return render_template("home.html")

@app.route("/user", methods=["POST","GET"])
def user():
    if request.method == "GET":
        if session:
            dash = db.execute("SELECT uname FROM users WHERE id = :id",{"id":session["u_id"]}).fetchall()
            return render_template("user.html",uname = dash[0].uname)
        message = "please Login first"
        return render_template("message.html",message=message)
    elif request.method == "POST":
        uname = request.form.get("uname")
        password = request.form.get("psw")
        dash = db.execute("SELECT * FROM users WHERE uname = :uname AND password = :password",{"uname":uname,"password":password}).fetchall()
        if dash:
            u_id = dash[0].id
            session["u_id"] = u_id
            return render_template("user.html",uname=dash[0].uname)
        message = "Wrong username or Password"
        return render_template("message.html",message=message)

@app.route("/logout")
def logout():
    session.pop("u_id",None)
    return redirect(url_for('home'))

@app.route("/registeration")
def registration():
    return render_template("register.html")

@app.route("/register",methods=["POST","GET"])
def register():
    if request.method == "GET":
        return "please submit registeration form"
    uname = request.form.get("uname")
    password = request.form.get("psw")
    email = request.form.get("email")
    message = uname + " already exist"
    if db.execute("SELECT * FROM users WHERE uname = :uname",{"uname":uname}).rowcount==0:
        db.execute("INSERT INTO users (uname,email,password) VALUES(:uname,:email,:password)",
                    {"uname":uname,"email":email,"password":password})
        db.commit()
        message = uname + " Successfully Registered"
    return render_template("message.html",message=message)

@app.route("/search",methods=["POST"])
def search():
    isbn = request.form.get("isbn")
    title = request.form.get("title")
    author = request.form.get("author")

    isbn = isbn.strip()
    title = title.strip()
    author = author.strip()

    isbn = "%"+isbn+"%"
    title = "%"+title+"%"
    author = "%"+author+"%"

    isbn.lower()
    title.lower()
    author.lower()
    book_list = db.execute("SELECT * FROM books WHERE LOWER(isbn) LIKE :isbn AND LOWER(title) LIKE :title AND LOWER(author) LIKE :author",
    {"isbn":isbn,"title":title,"author":author}).fetchall()
    if book_list:
        return render_template("result.html",books=book_list)
    return "Search result not found"
@app.route("/book/<string:title>/<string:isbn>",methods=["POST","GET"])
def book(title,isbn):
    if session:
        book = db.execute("SELECT * FROM books WHERE isbn = :isbn",{"isbn":isbn}).fetchall()
        reviews = db.execute("""SELECT x.comment, users.uname FROM (SELECT * FROM reviews WHERE reviews.bid = :bid)
        as x
        INNER JOIN users ON x.uid = users.id""",{"bid":book[0].id}).fetchall()
        check = db.execute("SELECT * FROM users WHERE :uid IN (SELECT uid FROM reviews WHERE reviews.bid = :bid)",{"bid":book[0].id,"uid":session["u_id"]}).fetchall()
        given = False
        if check:
            given = True
        if request.method == "POST":
            bid = book[0].id
            uid = session["u_id"]
            comment = request.form.get("comments")
            db.execute("INSERT INTO reviews (uid,bid,comment) VALUES (:uid,:bid,:comment)",
                    {"uid":uid,"bid":bid,"comment":comment})
            db.commit()
            return redirect(url_for('book',title=title,isbn=isbn))
        return render_template("book.html",book=book[0],reviews=reviews,given=given)
    else:
        return "please login first"
