import sqlite3
from datetime import datetime
from newsapi import fetch_articles

DB_FILE = "news.db"

COMPANIES = [
    "Amazon", "Walmart", "Apple", "Microsoft", "Tesla",
    "Alphabet", "Facebook", "Meta Platforms", "NVIDIA", "Intel",
    "Exxon Mobil", "Chevron", "Berkshire Hathaway", "JPMorgan Chase",
    "Visa", "Mastercard", "Coca-Cola", "PepsiCo", "Procter & Gamble",
    "Johnson & Johnson", "Pfizer", "Merck", "Disney", "Netflix",
    "Costco Wholesale", "CVS Health", "UnitedHealth Group", "McKesson",
    "Cardinal Health", "Cencora", "Salesforce", "Adobe", "Oracle",
    "IBM", "Qualcomm", "AMD", "Samsung", "Alibaba", "Tencent",
    "Toyota", "Ford", "General Motors", "Nike", "Starbucks"
]

def run_pipeline():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Create table if not exists
    c.execute("""
    CREATE TABLE IF NOT EXISTS news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT,
        title TEXT,
        content TEXT,
        sentiment TEXT,
        score REAL,
        published_at TEXT
    )
    """)

    for company in COMPANIES:
        # Delete old article for this company
        c.execute("DELETE FROM news WHERE company = ?", (company,))

        # Fetch latest articles
        articles = fetch_articles(company, limit=1)

        if not articles:
            print(f"No articles fetched for {company}")
            continue

        for article in articles:
            c.execute("""
            INSERT INTO news (company, title, content, sentiment, score, published_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                company,
                article["title"],
                article["content"],
                article["sentiment"],
                article["score"],
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))

        print(f"[{company}] Latest article stored.")

    conn.commit()
    conn.close()
    print("Pipeline finished. Database updated with latest articles.")

if __name__ == "__main__":
    print("=== Starting News Pipeline ===")
    run_pipeline()
