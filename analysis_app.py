# analysis_app.py

from flask import Flask, render_template
import fortune_db  # make sure this is the fixed version from earlier

app = Flask(__name__)

@app.route("/")
def landing():
    return render_template("landing.html")  # simple landing page

@app.route("/analysis")
def analysis():
    # Fetch all articles from the DB
    articles = fortune_db.get_all_articles()
    return render_template("analysis.html", articles=articles)

if __name__ == "__main__":
    app.run(debug=True)
    