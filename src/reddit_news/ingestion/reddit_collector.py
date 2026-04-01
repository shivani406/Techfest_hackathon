import requests
import time

class redditcollector:
    def __init__(self):
        self.headers = {"user-agent": "mozilla/5.0"}
        self.base_url = "https://www.reddit.com/r/cryptocurrency/new.json"

    def clean_text(self, text):
        if not text: return ""
        return " ".join(text.lower().split())

    def fetch_data(self):
        res = requests.get(self.base_url, headers=self.headers)
        if res.status_code != 200: return []
        
        data = res.json()
        posts = []
        for post in data['data']['children']:
            p = post['data']
            posts.append({
                "id": p['id'],
                "type": "reddit_post",
                "data": {
                    "title": self.clean_text(p['title']),
                    "text": self.clean_text(p['selftext']),
                    "score": p['score'],
                    "url": p['url']
                }
            })
        return posts