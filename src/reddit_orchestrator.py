import time
from datetime import datetime
from dotenv import load_dotenv
from reddit_news.ingestion.reddit_collector import redditcollector
from reddit_news.ingestion.news_collector import newscollector
from reddit_news.database.db_manager import databasemanager

load_dotenv()

def run_pipeline():
    print(f"[{datetime.now()}] starting ingestion cycle...")
    
    db = databasemanager()
    rc = redditcollector()
    nc = newscollector()

    try:
        # reddit
        print("fetching reddit...")
        reddit_data = rc.fetch_data()
        db.save_batch("reddit", reddit_data)
        
        # news
        print("fetching rss news...")
        news_data = nc.fetch_all()
        db.save_batch("news_rss", news_data)
        
        print(f"[{datetime.now()}] cycle complete. success.")
    except Exception as e:
        print(f"error in pipeline: {e}")

if __name__ == "__main__":
    # run immediately on start
    run_pipeline()
    
    # then schedule every 15 mins
    while True:
        time.sleep(900) # 15 minutes in seconds
        run_pipeline()