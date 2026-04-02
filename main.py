import subprocess
import time
import sys

def run_script(path, name):
    print(f"\n>> Starting {name}...")
    try:
        subprocess.run([sys.executable, path], check=True)
        print(f"✅ {name} finished.")
    except Exception as e:
        print(f"❌ {name} failed: {e}")

def main():
    while True:
        print(f"\n{'='*30}\nCycle Started: {time.ctime()}\n{'='*30}")
        
        # 1. Scrape Reddit/News
        run_script("src/live_trading/reddit_scraper.py", "Reddit Scraper")
        
        # 2. Run Llama 3 Sentiment Analysis
        run_script("sentiment-analysis-worker/sentiment_worker.py", "Llama Sentiment")
        
        # # 3. Run Price Prediction Model
        # run_script("ml_prediction/train_model.py", "ML Prediction")
        
        print("\nCycle complete. Waiting 15 mins...")
        time.sleep(900)

if __name__ == "__main__":
    main()