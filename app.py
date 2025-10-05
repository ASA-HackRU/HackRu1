from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
import database
from flask import redirect, flash
from dotenv import load_dotenv
import google.generativeai as genai
import os
import sqlite3

database.init_db()

genai.configure(api_key=os.getenv("AIzaSyDOm-BROi6sZ3BseBWzWI7GfZ0PkGwxMD0"))

# Flask setup
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = os.urandom(24)  # session cookies
Session(app)

@app.route("/signup", methods=["GET", "POST"])
def signup_route():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        hashed_pw = generate_password_hash(password)

        try:
            database.add_user(username, hashed_pw)
        except Exception as e:
            flash("Username already exists. Try another.")
            return redirect("/signup")

        session["username"] = username
        return redirect("/home")  # Redirect to home after signup

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login_route():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = database.get_user(username)
        if user and check_password_hash(user[2], password):
            session["username"] = username
            return redirect("/home")
        else:
            flash("Invalid username or password. Try again.")
            return redirect("/login")

    return render_template("login.html")


# Load environment variables
load_dotenv()
genai.api_key = os.getenv("GENAI_API_KEY")  # refers to .env for api key (redacted)

# Session memory helper
def init_memory():
    if "conversation" not in session:
        session["conversation"] = []

@app.route("/ask", methods=["POST"])
def ask():
    # Initialize session memory if it doesn't exist
    if "conversation" not in session:
        session["conversation"] = []

    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"reply": "Please enter a message."})

    # Append user message to session memory
    session["conversation"].append({"role": "user", "content": user_message})

    try:
        # Combine all previous messages into one prompt for Gemini
        full_prompt = "\n".join([msg["content"] for msg in session["conversation"]])

        # Generate response from Gemini
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(full_prompt)
        bot_reply_text = response.text if hasattr(response, "text") else "Gemini didn't respond."

        # Save Gemini's reply in session memory
        session["conversation"].append({"role": "assistant", "content": bot_reply_text})

    except Exception as e:
        bot_reply_text = f"Error: {str(e)}"

    return jsonify({"reply": bot_reply_text})


# Page routes
@app.route('/landing')
def landing():
    return render_template("landing.html")

@app.route('/home')
def home():
    if "username" in session:
        return render_template("index.html", username=session["username"])
    else:
        return redirect("/login")
    return render_template("index.html")

@app.route('/chatbot')
def chatbot():
    return render_template("chat.html")

@app.route('/track')
def track():
    return render_template("track.html")


@app.route('/analysis')
def analysis():
    # FIXED: point to correct DB and table
    conn = sqlite3.connect("fortune500_news.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM news ORDER BY id DESC")
    articles = c.fetchall()
    conn.close()
    return render_template("analysis.html", articles=articles)

# Run Flask
if __name__ == "__main__":
    app.run(debug=True)
