import requests
from textblob import TextBlob

# Your API key from https://www.thenewsapi.com/
API_KEY = "YOUR_API_KEY_HERE"

def analyze_sentiment(text):
    if not text:
        return "Neutral", 0.0
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.05:
        return "Positive", polarity
    elif polarity < -0.05:
        return "Negative", polarity
    else:
        return "Neutral", polarity

def fetch_articles(company, limit=3):
    url = f"https://api.thenewsapi.com/v1/news/all?api_token={API_KEY}&search={company}&language=en&limit={limit}&sort=published_at"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        articles = []

        for item in data.get("data", []):
            title = item.get("title", "No Title")
            description = item.get("description", "")
            published_at = item.get("published_at", "")
            url_link = item.get("url", "#")

            sentiment, score = analyze_sentiment(f"{title} {description}")

            articles.append({
                "company": company,
                "title": title,
                "description": description,
                "sentiment": sentiment,
                "score": round(score, 2),
                "timestamp": published_at,
                "url": url_link
            })
        return articles

    except Exception as e:
        print(f"Error fetching articles for {company}: {e}")
        return []
