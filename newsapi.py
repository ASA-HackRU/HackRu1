# newsapi.py

import requests
from transformers import pipeline


class NewsAPI:
    def __init__(self, api_token):
        self.api_token = api_token
        self.base_url = "https://api.thenewsapi.com/v1/news"

    def get_top_headlines(self, category="business", limit=3):
        """
        Pull fresh articles from TheNewsAPI.
        """
        url = f"{self.base_url}/top"
        params = {
            "api_token": self.api_token,
            "limit": limit,
            "categories": category
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception(f"API Error {response.status_code}: {response.text}")

        data = response.json()
        articles = []
        for article in data.get("data", []):
            articles.append({
                "title": article.get("title"),
                "description": article.get("description"),
                "url": article.get("url")
            })

        return articles


class SentimentAnalyzer:
    def __init__(self, model_name="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"):
        """
        Initialize HuggingFace sentiment pipeline (finance-tuned model).
        """
        self.model = pipeline("text-classification", model=model_name)

    def analyze_text(self, text):
        """
        Run sentiment analysis on a string of text and return ImpulseScore
        with strength (small/large).
        """
        if not text:
            return {
                "direction": "neutral",
                "strength": "neutral",
                "confidence": 0.0,
                "impulse_score": 0,
                "explanation": "No content to analyze."
            }

        result = self.model(text, truncation=True)[0]
        label = result["label"].lower()      # e.g., positive/negative/neutral
        score = float(result["score"])       # confidence

        # Map raw model output into Small/Large categories
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
            "impulse_score": impulse_value,  # -2 = strong neg, +2 = strong pos
            "explanation": f"The article suggests a {strength} movement ({label}) "
                           f"with {score*100:.1f}% confidence."
        }


def run_pipeline(api_token, category="business", limit=3):
    """
    Full pipeline:
    - Fetch latest news
    - Run HuggingFace sentiment analysis
    - Return articles with ImpulseScores
    """
    # Step 1: Get articles
    news = NewsAPI(api_token)
    articles = news.get_top_headlines(category=category, limit=limit)

    # Step 2: Init sentiment analyzer
    analyzer = SentimentAnalyzer()

    # Step 3: Attach ImpulseScore to each article
    results = []
    for article in articles:
        analysis_text = article["description"] or article["title"]
        impulse = analyzer.analyze_text(analysis_text)
        results.append({
            "title": article["title"],
            "url": article["url"],
            "impulse": impulse
        })

    return results
