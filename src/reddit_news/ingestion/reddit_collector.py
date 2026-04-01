import praw
import time
from ..database.db_manager import RedditNewsDB
from ...shared.config import Config

SUBREDDITS = ['cryptocurrency', 'bitcoin', 'ethereum', 'CryptoMarkets']
POST_LIMIT = 100

class RedditCollector:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=Config.REDDIT_CLIENT_ID,
            client_secret=Config.REDDIT_CLIENT_SECRET,
            user_agent=Config.REDDIT_USER_AGENT
        )
        self.db = RedditNewsDB()

    def fetch_posts(self):
        for subreddit_name in SUBREDDITS:
            print(f"Fetching r/{subreddit_name}...")
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                for post in subreddit.new(limit=POST_LIMIT):
                    post_data = {
                        'id': post.id,
                        'title': post.title,
                        'body': post.selftext,
                        'score': post.score,
                        'created_utc': post.created_utc,
                        'subreddit': subreddit_name,
                        'coin': None
                    }
                    self.db.insert_reddit_post(post_data)
                time.sleep(2)
            except Exception as e:
                print(f"Error: {e}")
        self.db.close()