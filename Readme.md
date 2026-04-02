<h1>🚀 Crypto Sentinel: Self-Hosted Sentiment & Price Terminal<h1></h1>

An open-source, locally-hosted intelligence terminal that bridges the gap between social media "hype" and market movements. By leveraging Local LLMs, we provide professional-grade sentiment analysis without the expensive API costs or privacy concerns of cloud-based solutions.


<h4>📖 Project Overview<h4></h4>

Professional traders pay thousands for sentiment data. Crypto Sentinel democratizes this by running a complete data-mining and inference pipeline on a standard laptop.

<h4>Key Features<h4>

Privacy-First AI : All text analysis happens locally via Ollama & Mistral 7B. Your data never leaves your machine.

Multi-Source Ingestion : Real-time monitoring of Reddit (r/CryptoCurrency, r/Bitcoin) and major News RSS feeds.

Hybrid Prediction : Combines LLM-derived sentiment scores with historical price data using Facebook Prophet.

Whale Tracking : Monitors the blockchain for large exchange inflows/outflows to detect institutional manipulation.


<h4>📊 System Architecture & Workflow</h4>

The project follows a modular pipeline where data is ingested, analyzed by a local LLM, correlated with price data, and visualized for the trader.

<h4>🔄 The Detailed Workflow:</h4>

Data Ingestion : Python scripts (PRAW/NewsAPI) fetch the latest posts from Reddit and news outlets every 15 minutes.

Sentiment Analysis (My Module) : Raw text is sent to a local Ollama server running Mistral 7B. The LLM classifies the "mood" (BULLISH/BEARISH/NEUTRAL) and assigns a confidence score.

On-Chain Tracking : The system monitors the blockchain (via Web3.py) for "Whale" movements (transactions >$1M).

Price Correlation : Historical price data from Binance is merged with the sentiment scores in a PostgreSQL/SQLite database.

Signal Generation : An ML model (Facebook Prophet) analyzes the combined features to output a "Buy/Sell/Hold" signal.

Terminal Dashboard : Results are displayed in a real-time CLI (Rich) or a web-based Streamlit dashboard.


<img width="661" height="546" alt="image" src="https://github.com/user-attachments/assets/4e8073c7-0e5e-4444-974b-f9abf5651348" />


<h4>🛠 Tech Stack</h4>

Language - Python

AI Engine -	Ollama (Mistral 7B)

Database - PostgreSQL	Storage for Posts, Prices, and Signals

Data Fetching	- PRAW (Reddit), NewsAPI	Social Media & News Ingestion

Time-Series ML	Facebook Prophet	Price Prediction & Trend Forecasting

UI/Dashboard	- Streamlit / Rich CLI



<h4>Complete Workflow Breakdown</h4>

<h4>Step 1: Data Ingestion</h4>

<img width="557" height="589" alt="image" src="https://github.com/user-attachments/assets/94453de6-c776-4eda-9057-b58103e663a5" />


<h4>Step 2: Sentiment Analysis with Self-Hosted LLMStep 2: Sentiment Analysis with Self-Hosted LLM

<img width="507" height="670" alt="image" src="https://github.com/user-attachments/assets/d730995c-479d-482d-a909-f67278c3ac9b" />
<img width="504" height="250" alt="image" src="https://github.com/user-attachments/assets/56f9fa62-06e2-4a2c-b798-04871c6f9177" />





