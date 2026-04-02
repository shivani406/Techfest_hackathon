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

#-------------------------------------------------------------------


import time
import subprocess
import sys
import os

def run_step(script_path, description):
    print(f"\n--- [STEP] {description} ---")
    try:
        # Run the script and wait for it to finish
        result = subprocess.run([sys.executable, script_path], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in {description}: {e}")
        return False

def main():
    while True:
        print(f"\n🚀 Starting Pipeline Cycle: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 1. SCRAPE: Call your existing Reddit scraper
        # Adjust the path to your specific scraping script
        scrape_success = run_step(
            "src/live_trading/reddit_scraper.py", 
            "Scraping Reddit & RSS Data"
        )
        
        if scrape_success:
            # 2. ANALYZE: Call the Mistral/Ollama worker
            run_step(
                "sentiment-analysis-worker/sentiment_worker.py", 
                "Analyzing Sentiment with Mistral"
            )
            
            # 3. UPDATE DASHBOARD: (Optional) Call a script to push the final score
            # run_step("dashboard/update_live_score.py", "Updating Dashboard")
        
        print("\n✅ Cycle Complete. Sleeping for 15 minutes...")
        time.sleep(900) # 15 minutes

if __name__ == "__main__":
    main()