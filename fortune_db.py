# fortune_db.py
import sqlite3

DB_PATH = "fortune500_news.db"  # match the DB_FILE in newsapi.py

def get_connection():
    """Open a connection to the fortune news DB"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # rows behave like dicts
    return conn

def get_all_articles():
    """Fetch all articles from the DB"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM news ORDER BY id DESC")  # use 'news' table
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_articles_by_company(company):
    """Fetch articles filtered by company"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM news WHERE company = ? ORDER BY id DESC", (company,))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]
