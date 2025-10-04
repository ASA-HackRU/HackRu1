import sqlite3

DB_NAME = "articles.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT,
            content TEXT,
            sentiment_score REAL,
            sentiment_explanation TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def insert_article(title, url, content, score, explanation):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO articles (title, url, content, sentiment_score, sentiment_explanation)
        VALUES (?, ?, ?, ?, ?)
    ''', (title, url, content, score, explanation))
    conn.commit()
    conn.close()

def get_latest_articles(limit=10):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT title, url, sentiment_score, sentiment_explanation, timestamp FROM articles ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows
