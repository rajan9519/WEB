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
