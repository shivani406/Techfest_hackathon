import feedparser

class newscollector:
    def __init__(self):
        self.feeds = [
            "https://www.coindesk.com/arc/outboundfeeds/rss/",
            "https://cointelegraph.com/rss",
            "https://bitcoinmagazine.com/.rss/full/"
        ]

    def clean_text(self, text):
        import re
        clean = re.compile('<.*?>')
        text = re.sub(clean, '', text)
        return " ".join(text.lower().split())

    def fetch_all(self):
        all_news = []
        for url in self.feeds:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                all_news.append({
                    "id": entry.get('id', entry.link),
                    "type": "news_article",
                    "data": {
                        "title": self.clean_text(entry.title),
                        "summary": self.clean_text(entry.get('summary', '')),
                        "link": entry.link,
                        "published": entry.get('published', '')
                    }
                })
        return all_news