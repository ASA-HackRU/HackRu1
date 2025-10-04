import sqlite3
from datetime import datetime

# Configure CS50 Library to use SQLite database
#prod_db = SQL("sqlite:///productivity_final_proj.db")
prod_db = sqlite3.connect('productivity_final_proj.db', check_same_thread=False)
prod_db.row_factory = sqlite3.Row

def get_cursor():
    return prod_db.cursor()

def close_connection():
    """Close the database connection"""
    if prod_db:
        prod_db.close()

def query_user_accounts(username):
    """Query user accounts table to check user"""
    cur = get_cursor()
    cur.execute(
        "SELECT * FROM user_accounts WHERE username = ?", (username)
    )
    return cur.fetchall()


def insert_user(username, password):
    cur = get_cursor()
    cur.execute("INSERT INTO user_accounts (username, password) VALUES (?, ?)", (username, password))
    prod_db.commit()
    return cur.lastrowid
