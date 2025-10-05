from newsapi import NewsAPI
import sqlite3

API_KEY = "sp8yMhbsJEkoyYMJNoDbDyrmEjTxeo5rvJM7Thh0"  # replace with your key

# Top Fortune 500 / major companies list
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

# Initialize NewsAPI wrapper
newsapi = NewsAPI(API_KEY)

# Limit calls to 20 companies max
companies_to_fetch = COMPANIES[:20]

for company in companies_to_fetch:
    print(f"\nFetching headlines for {company}...")
    try:
        results = newsapi.get_top_headlines(company, limit=3)
        for r in results:
            print(f"{r['company']} | {r['title']} | Score {r['score']} ({r['strength']})")
            print(f"Explanation: {r['explanation']}\n")
    except Exception as e:
        print(f"Error fetching {company}: {e}")

# Now view a sample of the DB contents
print("\n--- DATABASE SAMPLE (last 10 entries) ---")
conn = sqlite3.connect("news.db")
c = conn.cursor()
for row in c.execute("SELECT company, title, score, strength FROM news_analysis ORDER BY id DESC LIMIT 10"):
    print(row)
conn.close()