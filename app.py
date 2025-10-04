from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os
from flask_session import Session

# ------------------------------
# Flask setup
# ------------------------------
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# ------------------------------
# Gemini setup
# ------------------------------
# Option 1: Use environment variable
# Make sure you run in terminal: export GEMINI_API_KEY="AIzaSyDOm-BROi6sZ3BseBWzWI7GfZ0PkGwxMD0"
genai.configure(api_key=os.environ.get("AIzaSyDOm-BROi6sZ3BseBWzWI7GfZ0PkGwxMD0"))

# ------------------------------
# Chatbot endpoint
# ------------------------------
@app.route('/ask', methods=['POST'])
def ask():
    message = request.json.get("message", "")
    if not message:
        return jsonify({"reply": "Please enter a message."})

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(message)

    return jsonify({"reply": response.text})

# ------------------------------
# Page routes
# ------------------------------
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

# ------------------------------
# Run Flask
# ------------------------------
if __name__ == "__main__":
    app.run(debug=True)

