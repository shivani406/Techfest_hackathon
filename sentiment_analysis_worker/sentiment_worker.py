import psycopg2
from psycopg2.extras import RealDictCursor
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

class sentimentanalyzer:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.conn = psycopg2.connect(
            dbname=os.getenv("db_name"),
            user=os.getenv("db_user"),
            password=os.getenv("db_pass"),
            host=os.getenv("db_host")
        )

    def get_recent_news(self):
        # fetch news from the last 15 minutes
        query = """
        select raw_data from raw_content 
        where created_at > now() - interval '15 minutes'
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            return cur.fetchall()

    def analyze_item(self, text):
        prompt = f"""
        analyze crypto market sentiment for this text: "{text[:500]}"
        respond only in valid json: {{"score": <float between 0 and 1>}}
        0 = extreme bearish, 0.5 = neutral, 1 = extreme bullish.
        """
        payload = {
            "model": "mistral",
            "prompt": prompt,
            "format": "json",
            "stream": False
        }
        try:
            res = requests.post(self.ollama_url, json=payload, timeout=15)
            return json.loads(res.json()['response'])['score']
        except:
            return 0.5 # default to neutral on error

    def get_final_signal(self):
        news_items = self.get_recent_news()
        if not news_items:
            print("no new news found in the last 15 mins.")
            return 0.5
            
        scores = []
        for item in news_items:
            data = item['raw_data']
            # combine title and snippet for better context
            full_text = f"{data.get('title', '')} {data.get('summary', '')}"
            score = self.analyze_item(full_text)
            scores.append(score)
            
        final_score = sum(scores) / len(scores)
        return round(final_score, 4)

    def save_final_score(self, score):
        query = "insert into market_sentiment_history (score) values (%s)"
        with self.conn.cursor() as cur:
            cur.execute(query, (score,))
            self.conn.commit()
            
if __name__ == "__main__":
    analyzer = sentimentanalyzer()
    score = analyzer.get_final_signal()
    print(f"final sentiment signal: {score}")