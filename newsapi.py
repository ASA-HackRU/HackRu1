
#APi key is from TheNewsAPI.com
    #MD9SRQGgfM8S8pmV3pxCFaP51x94WtB6C5iwPlSo
#title, article itself

import requests

class NewsAPI:

    def __init__(self, api_token):
        self.api_token = api_token
        self.base_url = "https://api.thenewsapi.com/v1/news"


    def get_top_headlines(self, category="business", limit=3):
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