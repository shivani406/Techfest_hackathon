import subprocess
import time
import sys
import os

def run_script(subfolders, filename, name):
    # this builds the full path correctly: root\sub1\sub2\filename.py
    script_path = os.path.join(os.getcwd(), *subfolders, filename)
    
    print(f"\n>> starting {name}...")
    
    if not os.path.exists(script_path):
        print(f"❌ error: file not found at {script_path}")
        return False

    try:
        # shell=True handles complex windows paths best
        subprocess.run(f'python "{script_path}"', shell=True, check=True)
        print(f"✅ {name} finished.")
        return True
    except Exception as e:
        print(f"❌ {name} failed: {e}")
        return False

def main():
    while True:
        print(f"\n{'='*40}")
        print(f"cycle started: {time.ctime()}")
        print(f"{'='*40}")
        
        # 1. reddit collector
        # path from image: src -> reddit_news -> ingestion -> reddit_collector.py
        run_script(["src", "reddit_news", "ingestion"], "reddit_collector.py", "reddit scraper")
        
        # 2. news collector (if you want both)
        run_script(["src", "reddit_news", "ingestion"], "news_collector.py", "news scraper")
        
        # 3. llama sentiment
        # path from image: sentiment_analysis_worker -> sentiment_worker.py
        run_script(["sentiment_analysis_worker"], "sentiment_worker.py", "llama sentiment")
        
        print("\ncycle complete. waiting 15 mins...")
        time.sleep(900)

if __name__ == "__main__":
    main()