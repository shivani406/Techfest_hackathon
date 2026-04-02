import requests
import json

def test_sentiment():
    url = "http://localhost:11434/api/generate"
    model = "llama3:latest" # ensure this matches your 'ollama list'
    
    test_cases = [
        "Bitcoin hits all time high as institutional adoption doubles!",
        "Major exchange hacked, millions in crypto stolen overnight.",
        "The market is moving sideways with very little trading volume."
    ]
    
    print(f"testing model: {model}...\n")
    
    for text in test_cases:
        prompt = f'analyze crypto sentiment: "{text}". respond only in json: {{"score": 0.0-1.0}}'
        payload = {"model": model, "prompt": prompt, "format": "json", "stream": False}
        
        try:
            res = requests.post(url, json=payload, timeout=15)
            score = json.loads(res.json()['response'])['score']
            print(f"text: {text[:50]}...")
            print(f"score: {score} {'✅' if (score > 0.7 or score < 0.3) else '⚪'}\n")
        except Exception as e:
            print(f"❌ failed on text: {text[:20]} | error: {e}")

if __name__ == "__main__":
    test_sentiment()