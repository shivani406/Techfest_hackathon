import feedparser
import time
from datetime import datetime
from ..database.db_manager import RedditNewsDB

RSS_FEEDS = [
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://cointelegraph.com/rss",
    "https://www.theblock.co/rss"
]

class NewsCollector:
    def __init__(self):
        self.db = RedditNewsDB()

    def fetch_news(self):
        for feed_url in RSS_FEEDS:
            print(f"Fetching {feed_url}...")
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:50]:
                    published = entry.get('published_parsed')
                    if published:
                        published = datetime.fromtimestamp(time.mktime(published))
                    else:
                        published = datetime.now()
                    news_data = {
                        'url': entry.get('link', ''),
                        'title': entry.get('title', ''),
                        'description': entry.get('summary', ''),
                        'content': entry.get('content', [{'value': ''}])[0]['value'],
                        'published_at': published,
                        'source': feed_url.split('/')[2] if '//' in feed_url else 'unknown',
                        'coin': None
                    }
                    if news_data['url']:
                        self.db.insert_news_article(news_data)
                time.sleep(2)
            except Exception as e:
                print(f"Error: {e}")
        self.db.close()