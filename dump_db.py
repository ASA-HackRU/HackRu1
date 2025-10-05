import sqlite3
import json

DB_FILE = "fortune500_news.db"

conn = sqlite3.connect(DB_FILE)
c = conn.cursor()

c.execute("SELECT * FROM news")
rows = c.fetchall()

# Get column names
columns = [description[0] for description in c.description]

# Convert to list of dicts
data = [dict(zip(columns, row)) for row in rows]

# Print JSON to terminal
print(json.dumps(data, indent=2))

# Optionally, save to file
with open("fortune500_news_dump.json", "w") as f:
    json.dump(data, f, indent=2)

conn.close()
print(f"Dumped {len(rows)} articles to fortune500_news_dump.json")
