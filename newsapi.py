# newsapi.py
import requests
from transformers import pipeline
import sqlite3
import time

FORTUNE_500_COMPANIES = [
    "Walmart", "Amazon", "UnitedHealth Group", "Apple", "CVS Health",
    "Berkshire Hathaway", "Alphabet", "Exxon Mobil", "McKesson", "Cencora"
    # Add more if needed
]

DB_FILE = "fortune500_news.db"

class NewsAPI:
    def __init__(self, api_token):
        self.api_token = api_token
        self.base_url = "https://api.thenewsapi.com/v1/news"

    def get_top_headlines(self, category="business", limit=5):
        url = f"{self.base_url}/top"
        params = {
            "api_token": self.api_token,
            "limit": limit,
            "categories": category,
            "language": "en"
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception(f"API Error {response.status_code}: {response.text}")

        articles = []
        for article in response.json().get("data", []):
            if article.get("language") != "en":
                continue
            articles.append({
                "title": article.get("title"),
                "description": article.get("description"),
                "url": article.get("url")
            })
        return articles


class SentimentAnalyzer:
    def __init__(self, model_name="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"):
        self.model = pipeline("text-classification", model=model_name)

    def analyze_text(self, text):
        if not text:
            return {"direction": "neutral", "strength": "neutral", "confidence": 0.0, "impulse_score": 0, "explanation": "No content to analyze."}
        result = self.model(text, truncation=True)[0]
        label = result["label"].lower()
        score = float(result["score"])
        if label == "neutral":
            strength = "neutral"
            impulse_value = 0
        elif score >= 0.75:
            strength = f"large {label}"
            impulse_value = 2 if label == "positive" else -2
        elif score >= 0.5:
            strength = f"small {label}"
            impulse_value = 1 if label == "positive" else -1
        else:
            strength = "neutral"
            impulse_value = 0
        return {
            "direction": label,
            "strength": strength,
            "confidence": round(score, 3),
            "impulse_score": impulse_value,
            "explanation": f"The article suggests a {strength} movement ({label}) with {score*100:.1f}% confidence."
        }


def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            title TEXT,
            description TEXT,
            url TEXT,
            direction TEXT,
            strength TEXT,
            confidence REAL,
            impulse_score INTEGER,
            explanation TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def store_article(company, article, impulse):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO news (company, title, description, url, direction, strength, confidence, impulse_score, explanation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        company,
        article["title"],
        article.get("description"),
        article["url"],
        impulse["direction"],
        impulse["strength"],
        impulse["confidence"],
        impulse["impulse_score"],
        impulse["explanation"]
    ))
    conn.commit()
    conn.close()


def run_pipeline(api_token, limit=5):
    news_api = NewsAPI(api_token)
    analyzer = SentimentAnalyzer()
    init_db()

    for company in FORTUNE_500_COMPANIES:
        print(f"\n=== Processing {company} ===")
        try:
            articles = news_api.get_top_headlines(category="business", limit=limit)
        except Exception as e:
            print(f"Failed to fetch news for {company}: {e}")
            continue

        for article in articles:
            analysis_text = article["description"] or article["title"]
            impulse = analyzer.analyze_text(analysis_text)
            store_article(company, article, impulse)
            print(f"[{company}] {article['title']} -> {impulse['strength']}, score: {impulse['confidence']}")

    print("\nPipeline finished. Data stored in SQLite database:", DB_FILE)
