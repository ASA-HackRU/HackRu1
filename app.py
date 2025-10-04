from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from flask import redirect, render_template, request, session
from functools import wraps
from datetime import datetime

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/landing')
def landing():
    return render_template("landing.html")

@app.route('/home')
def home():
    return render_template("index.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/chatbot')
def chatbot():
    return render_template("chat.html")

@app.route('/track')
def track():
    return render_template("track.html")

@app.route('/signup')
def signup():
    return render_template("signup.html")
