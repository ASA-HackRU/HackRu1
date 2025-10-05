import requests
import sqlite3
from datetime import datetime
from transformers import pipeline

class NewsAPI:
    def __init__(self, api_token, db_path="news.db"):
        self.api_token = api_token
        self.base_url = "https://api.thenewsapi.com/v1/news/top"
        self.db_path = db_path

        # force CPU to avoid MPS hang on Mac
        self.sentiment = pipeline("sentiment-analysis", model="ProsusAI/finbert", device=-1)

        # setup database
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS news_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT,
                title TEXT,
                url TEXT,
                score INTEGER,
                strength TEXT,
                explanation TEXT,
                timestamp TEXT
            )
        """)
        conn.commit()
        conn.close()

    def _classify(self, text):
        """Run sentiment + map to ImpulseScore + explanation."""
        result = self.sentiment(text[:512])[0]  # truncate to 512 chars
        label = result["label"]
        score = result["score"]

        # map to 1-5 score
        if label == "negative":
            if score > 0.75:
                mapped_score, strength = 1, "large negative"
            else:
                mapped_score, strength = 2, "small negative"
        elif label == "positive":
            if score > 0.75:
                mapped_score, strength = 5, "large positive"
            else:
                mapped_score, strength = 4, "small positive"
        else:
            mapped_score, strength = 3, "neutral"

        # explanation
        explanation = (
            f"This article suggests a {strength} market reaction. "
            f"The model judged the tone as {label} with confidence {score:.2f}. "
            f"This implies potential {strength} sentiment toward the company’s stock."
        )

        return mapped_score, strength, explanation

    def get_top_headlines(self, query, limit=3):
        params = {
            "api_token": self.api_token,
            "limit": limit,
            "language": "en",
            "search": query
        }
        response = requests.get(self.base_url, params=params)
        if response.status_code != 200:
            raise Exception(f"API Error {response.status_code}: {response.text}")

        data = response.json()
        results = []

        for article in data.get("data", []):
            title = article.get("title", "")
            description = article.get("description", "")
            url = article.get("url", "")
            combined_text = f"{title}. {description}"

            score, strength, explanation = self._classify(combined_text)

            results.append({
                "company": query,
                "title": title,
                "url": url,
                "score": score,
                "strength": strength,
                "explanation": explanation,
                "timestamp": datetime.utcnow().isoformat()
            })

            # save to db
            self._save_to_db(query, title, url, score, strength, explanation)

        return results

    def _save_to_db(self, company, title, url, score, strength, explanation):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            INSERT INTO news_analysis
            (company, title, url, score, strength, explanation, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (company, title, url, score, strength, explanation, datetime.utcnow().isoformat()))
        conn.commit()
        conn.close()