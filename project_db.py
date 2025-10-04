import sqlite3

conn = sqlite3.connect('articles.db')
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    content TEXT,
    source TEXT,
    sentiment_direction TEXT,
    sentiment_confidence REAL,
    reasoning TEXT,
    published_at TEXT
)
""")

conn.commit()
conn.close()