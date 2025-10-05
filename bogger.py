import sqlite3

DB_PATH = "news.db"  # make sure this matches your newsapi.py config

def view_db(limit=20):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    print(f"--- Last {limit} entries in news.db ---\n")
    for row in c.execute("""
        SELECT company, title, score, strength, explanation, timestamp
        FROM news_analysis
        ORDER BY id DESC
        LIMIT ?
    """, (limit,)):
        company, title, score, strength, explanation, timestamp = row
        print(f"[{timestamp}] {company} | Score {score} ({strength})")
        print(f"Title: {title}")
        print(f"Explanation: {explanation}\n")

    conn.close()

if __name__ == "__main__":
    view_db(limit=20)

