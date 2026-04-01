import psycopg2
from ...shared.config import Config

class RedditNewsDB:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_tables()

    def _connect(self):
        self.conn = psycopg2.connect(
            host=Config.POSTGRES_HOST,
            port=Config.POSTGRES_PORT,
            dbname=Config.POSTGRES_DB,
            user=Config.POSTGRES_USER,
            password=Config.POSTGRES_PASSWORD
        )
        self.cursor = self.conn.cursor()

    def _create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS reddit_posts (
            id TEXT PRIMARY KEY,
            title TEXT,
            body TEXT,
            score INTEGER,
            created_utc INTEGER,
            subreddit TEXT,
            coin TEXT,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            sentiment_score REAL,
            sentiment_label TEXT
        );
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS news_articles (
            url TEXT PRIMARY KEY,
            title TEXT,
            description TEXT,
            content TEXT,
            published_at TIMESTAMP,
            source TEXT,
            coin TEXT,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            sentiment_score REAL,
            sentiment_label TEXT
        );
        """)
        self.conn.commit()

    def insert_reddit_post(self, post_data):
        self.cursor.execute("""
        INSERT INTO reddit_posts (id, title, body, score, created_utc, subreddit, coin)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING;
        """, (post_data['id'], post_data['title'], post_data['body'][:5000],
              post_data['score'], post_data['created_utc'],
              post_data['subreddit'], post_data.get('coin')))
        self.conn.commit()

    def insert_news_article(self, news_data):
        self.cursor.execute("""
        INSERT INTO news_articles (url, title, description, content, published_at, source, coin)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (url) DO NOTHING;
        """, (news_data['url'], news_data['title'], news_data['description'][:2000],
              news_data['content'][:5000], news_data['published_at'],
              news_data['source'], news_data.get('coin')))
        self.conn.commit()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()