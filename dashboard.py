import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
from os import getenv
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Crypto Whale & Sentiment Tracker", layout="wide")

def get_db_connection():
    return psycopg2.connect(
        dbname=getenv("db_name"), user=getenv("db_user"),
        password=getenv("db_pass"), host=getenv("db_host")
    )

# --- DATA FETCHING ---
def load_data():
    conn = get_db_connection()
    # Get latest sentiment
    sent_df = pd.read_sql("select score from market_sentiment_history order by created_at desc limit 1", conn)
    # Get whale ratio (last 15 mins)
    whale_df = pd.read_sql("""
        select 
            sum(usd_value) filter (where is_whale = true) as whale_vol,
            sum(usd_value) as total_vol 
        from live_trades where received_at > now() - interval '15 minutes'
    """, conn)
    conn.close()
    
    s_score = float(sent_df['score'].iloc[0]) if not sent_df.empty else 0.5
    w_vol = float(whale_df['whale_vol'].iloc[0] or 0)
    t_vol = float(whale_df['total_vol'].iloc[0] or 1)
    w_score = min(w_vol / (t_vol * 0.5), 1.0) # Normalized whale strength
    
    return s_score, w_score

# --- UI LAYOUT ---
st.title("🌊 Crypto Whale & AI Sentiment Dashboard")

sent, whale = load_data()
# Hardcoded prediction for demo (replace with your actual model output)
pred = 0.65 

final_score = (sent * 0.3) + (whale * 0.3) + (pred * 0.4)

# Top Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Llama 3 Sentiment", f"{sent:.2f}", delta="Bullish" if sent > 0.5 else "Bearish")
col2.metric("Whale Strength", f"{whale:.2f}")
col3.metric("Final Market Health", f"{final_score:.2f}")

# Progress Bar for Final Score
st.write("### Total Market Confidence")
st.progress(final_score)

if final_score > 0.7:
    st.success("🚀 STRONG BUY SIGNAL")
elif final_score < 0.3:
    st.error("⚠️ STRONG SELL SIGNAL")
else:
    st.warning("⚖️ NEUTRAL / HOLD")

st.info("Note: Dashboard refreshes every 15 minutes automatically.")