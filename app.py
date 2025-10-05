from flask import Flask, render_template, request, jsonify, session, redirect, flash
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
import database
import os
import sqlite3
from dotenv import load_dotenv
import google.generativeai as genai
import fortune_db

# Initialize user database
database.init_db()

# Load environment variables
load_dotenv()
genai.api_key = os.getenv("GENAI_API_KEY")  # refers to .env for api key (redacted)

# Flask setup
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = os.urandom(24)  # session cookies
Session(app)

# ----------------------------
# User authentication routes
# ----------------------------
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
        return redirect("/home")

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

# ----------------------------
# Session memory helper
# ----------------------------
def init_memory():
    if "conversation" not in session:
        session["conversation"] = []

# ----------------------------
# /ask route for Gemini 2.0
# ----------------------------
@app.route("/ask", methods=["POST"])
def ask():
    init_memory()
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"reply": "Please enter a message."})

    session["conversation"].append({"role": "user", "content": user_message})

    try:
        full_prompt = "\n".join([msg["content"] for msg in session["conversation"]])
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(full_prompt)
        bot_reply_text = response.text if hasattr(response, "text") else "Gemini didn't respond."
        session["conversation"].append({"role": "assistant", "content": bot_reply_text})
    except Exception as e:
        bot_reply_text = f"Error: {str(e)}"

    return jsonify({"reply": bot_reply_text})

# ----------------------------
# Page routes
# ----------------------------
@app.route("/")
@app.route("/landing")
def landing():
    return render_template("landing.html")  # simple landing page

@app.route("/home")
def home():
    if "username" in session:
        return render_template("index.html", username=session["username"])
    else:
        return redirect("/login")

@app.route("/chatbot")
def chatbot():
    return render_template("chat.html")

@app.route("/track")
def track():
    return render_template("track.html")

@app.route("/analysis")
def analysis():
    # Fetch all articles from the fortune500_news.db
    conn = sqlite3.connect("fortune500_news.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM news ORDER BY id DESC")
    articles = c.fetchall()
    conn.close()
    return render_template("analysis.html", articles=articles)


import yfinance as yf

# ----------------------------
# Portfolio API
# ----------------------------
@app.route("/api/portfolio", methods=["GET"])
def api_portfolio():
    if "username" not in session:
        return jsonify({"ok": False, "error": "Not logged in"}), 403

    username = session["username"]
    conn = sqlite3.connect("portfolio.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            company_name TEXT,
            ticker TEXT,
            price_bought REAL,
            quantity INTEGER,
            current_price REAL DEFAULT 0,
            percentage_change REAL DEFAULT 0
        )
    """)
    conn.commit()

    c.execute("SELECT * FROM portfolio WHERE username=?", (username,))
    rows = c.fetchall()
    conn.close()

    portfolio = []
    for r in rows:
        portfolio.append({
            "company_name": r[2],
            "ticker": r[3],
            "price_bought": r[4],
            "quantity": r[5],
            "current_price": r[6],
            "percentage_change": r[7]
        })
    return jsonify({"ok": True, "portfolio": portfolio})


@app.route("/api/add_stock", methods=["POST"])
def api_add_stock():
    if "username" not in session:
        return jsonify({"ok": False, "error": "Not logged in"}), 403

    data = request.get_json()
    company_name = data.get("company_name", "").strip()
    price_bought = float(data.get("price_bought", 0))
    quantity = int(data.get("quantity", 0))

    if not company_name or price_bought <= 0 or quantity <= 0:
        return jsonify({"ok": False, "error": "Invalid input"}), 400

    # Try to find ticker using yfinance
    try:
        ticker = yf.Ticker(company_name).info.get("symbol", company_name)
        current_price = yf.Ticker(ticker).history(period="1d")["Close"].iloc[-1]
    except Exception:
        ticker = company_name
        current_price = price_bought

    percentage_change = ((current_price - price_bought) / price_bought) * 100

    conn = sqlite3.connect("portfolio.db")
    c = conn.cursor()
    c.execute("INSERT INTO portfolio (username, company_name, ticker, price_bought, quantity, current_price, percentage_change) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (session["username"], company_name, ticker, price_bought, quantity, current_price, percentage_change))
    conn.commit()
    conn.close()

    return jsonify({"ok": True})


@app.route("/api/update_prices", methods=["POST"])
def api_update_prices():
    if "username" not in session:
        return jsonify({"ok": False, "error": "Not logged in"}), 403

    conn = sqlite3.connect("portfolio.db")
    c = conn.cursor()
    c.execute("SELECT id, ticker, price_bought FROM portfolio WHERE username=?", (session["username"],))
    rows = c.fetchall()

    for r in rows:
        stock_id, ticker, price_bought = r
        try:
            current_price = yf.Ticker(ticker).history(period="1d")["Close"].iloc[-1]
            percentage_change = ((current_price - price_bought) / price_bought) * 100
            c.execute("UPDATE portfolio SET current_price=?, percentage_change=? WHERE id=?",
                      (current_price, percentage_change, stock_id))
        except Exception as e:
            print(f"Error updating {ticker}: {e}")

    conn.commit()
    conn.close()

    return jsonify({"ok": True})



# ----------------------------
# Run Flask
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

