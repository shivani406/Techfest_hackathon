import pandas as pd
import psycopg2
import json
from os import getenv
from dotenv import load_dotenv

load_dotenv()

def get_latest_trading_data(limit=5000):
    """
    fetches raw crypto data from postgres and serializes it for ML.
    """
    conn = psycopg2.connect(
        dbname=getenv("db_name"),
        user=getenv("db_user"),
        password=getenv("db_pass"),
        host=getenv("db_host")
    )
    
    # 1. pull raw data
    query = f"select exchange, raw_payload, received_at from live_trades order by received_at desc limit {limit}"
    df = pd.read_sql(query, conn)
    conn.close()

    if df.empty:
        return pd.DataFrame()

    # 2. serialization: extract nested json fields into columns
    # logic depends on exchange format (e.g., binance uses 'p' for price)
    def parse_payload(row):
        payload = row['raw_payload']
        if isinstance(payload, str):
            payload = json.loads(payload)
        
        # simple flattening logic
        return {
            'price': float(payload.get('p', payload.get('price', 0))),
            'quantity': float(payload.get('q', payload.get('size', 0))),
            'exchange': row['exchange'],
            'time': row['received_at']
        }

    serialized_df = pd.DataFrame([parse_payload(r) for _, r in df.iterrows()])
    return serialized_df