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
        self.selected_model = os.getenv("OLLAMA_MODEL", "llama3:latest")
        self.conn = psycopg2.connect(
            dbname=os.getenv("db_name"),
            user=os.getenv("db_user"),
            password=os.getenv("db_pass"),
            host=os.getenv("db_host")
        )

    def get_recent_news(self):
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
            "model": self.selected_model,
            "prompt": prompt,
            "format": "json",
            "stream": False
        }
        try:
            res = requests.post(self.ollama_url, json=payload, timeout=15)
            response_data = res.json()
            # ollama returns the actual model output in the 'response' key
            inner_json = json.loads(response_data['response'])
            return float(inner_json.get('score', 0.5))
        except Exception as e:
            print(f"error analyzing item: {e}")
            return 0.5

    def get_final_signal(self):
        news_items = self.get_recent_news()
        if not news_items:
            print("no new news found in the last 15 mins.")
            return 0.5
        scores = []
        for item in news_items:
            data = item['raw_data']
            full_text = f"{data.get('title', '')} {data.get('summary', '')}"
            score = self.analyze_item(full_text)
            scores.append(score)
        final_score = sum(scores) / len(scores)
        return round(final_score, 4)

    def save_final_score(self, score):
        # make sure you have run 'create table market_sentiment_history (score numeric, created_at timestamp default now());'
        query = "insert into market_sentiment_history (score) values (%s)"
        with self.conn.cursor() as cur:
            cur.execute(query, (score,))
            self.conn.commit()

if __name__ == "__main__":
    analyzer = sentimentanalyzer()
    score = analyzer.get_final_signal()
    analyzer.save_final_score(score)
    print(f"final sentiment signal: {score}")