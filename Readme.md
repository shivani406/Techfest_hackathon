🔮 CryptoOracleAutonomous AI-Powered Crypto Sentiment & Signal EngineA self-hosted, end-to-end pipeline that ingests market data, analyzes social sentiment via local LLMs, tracks whale movements, forecasts prices, and generates explainable trading signals.Architecture • Modules • Tech Stack • Installation⚡ The Self-Hosted AdvantageCryptoOracle is designed to run entirely on Your Laptop (Self-Hosted Environment). By utilizing local LLMs (Ollama) and CPU-friendly forecasting models (Prophet), this architecture ensures zero API costs for inference, complete data privacy, and zero reliance on rate-limited external AI providers.🏗️ System Architecturegraph TD
    subgraph "1. Data Ingestion Layer"
        R[Reddit API] --> S[Python Scheduler <br> APScheduler/Celery]
        N[News API] --> S
        B[Binance API] --> S
        E[Etherscan/Solscan] --> S
    end

    subgraph "2. Storage Layer"
        S --> DB[(PostgreSQL / SQLite)]
        DB -.-> T1(reddit_posts)
        DB -.-> T2(news_articles)
        DB -.-> T3(price_candles)
        DB -.-> T4(whale_txs)
    end

    subgraph "3. Intelligence Layer"
        DB --> LLM[Ollama Local LLM <br> Sentiment Analyzer]
        DB --> PROPHET[Facebook Prophet <br> Price Predictor]
    end

    subgraph "4. Execution & UI Layer"
        LLM --> SG[Signal Generation Logic]
        PROPHET --> SG
        SG --> API[FastAPI Endpoints]
        API --> UI[Streamlit / Rich CLI Dashboard]
    end
⚙️ Core Modules (The Pipeline)1. 📡 Data Ingestion PipelineA high-throughput scheduler that manages API connections, handles rate limits, and safely stores raw data into our relational database.Sources: Reddit (via PRAW), NewsAPI.org, Binance API (python-binance), Etherscan/Solscan.Engine: APScheduler or Celery.Database Tables: reddit_posts, news_articles, price_candles, whale_txs.2. 🧠 LLM Sentiment Analysis PipelineRuns Ollama locally with Mistral 7B (or FinBERT as a lightweight fallback) to process raw text into quantifiable sentiment scores using advanced Few-Shot Prompt Engineering.Prompt Engineering Template:System: Classify the sentiment of this crypto post as BULLISH, BEARISH, or NEUTRAL.Examples:Post: 'Bitcoin is going to $100k!' → BULLISHPost: 'Massive sell-off incoming' → BEARISHPost: 'BTC trading sideways' → NEUTRALUser: Analyze: {post_text}Rule: Return only: BULLISH/BEARISH/NEUTRAL + confidenceOutput Example: BULLISH (confidence: 0.92) stored directly in PostgreSQL.3. 🐋 On-Chain Analytics PipelineTracks institutional and "whale" behavior by filtering blockchain data via web3.py.Filter: Transaction Value > $1M USD AND from != to (filters out self-transfers).Signal Interpretation:📉 Exchange Inflow: Possible selling pressure.📈 Exchange Outflow: Accumulation (Bullish).➖ Whale-to-Whale: Neutral (OTC trade).4. 📉 Price Prediction PipelineUtilizes Facebook Prophet, optimized for CPU-friendly financial time-series forecasting, handling missing data well, and mapping crypto-specific seasonality.Input Features (15-min windows):OHLCV (Open, High, Low, Close, Volume)Technical Indicators (RSI, MACD, Moving Averages)Sentiment (Avg bullish score from last hour)Whale Activity (Net inflow/outflow from last hour)Volatility (Price range %)Output: Predicted Direction (UP/DOWN/SIDEWAYS), Confidence (55-85% target), Timeframe (Next 1h, 4h, 24h).5. 🚦 Signal Generation EngineThe brain of the backend. It ingests data from all modules to generate transparent, explainable trading signals via FastAPI endpoints.Decision Matrix Logic:if sentiment > 0.7 and prediction == "UP" and whales == "Accumulating":
    return "STRONG BUY SIGNAL"
elif sentiment < 0.3 and prediction == "DOWN" and whales == "Distributing":
    return "STRONG SELL SIGNAL"
elif sentiment > 0.6 and prediction == "UP":
    return "MODERATE BUY"
else:
    return "HOLD / WAIT"
Final Explainable Output (passed to Frontend):{
  "SIGNAL": "BUY (STRONG)",
  "CONFIDENCE": "82%",
  "REASONING": [
    "Reddit sentiment very positive (0.82)",
    "Price model predicts +3.2% in next 4h",
    "Whales accumulated 2,500 BTC in last hour",
    "Trading volume 40% above average"
  ]
}
🛠️ Tech StackLayerTechnologiesData CollectionPython, PRAW, NewsAPI, python-binance, web3.pyOrchestration & DBAPScheduler / Celery, PostgreSQL / SQLiteAI / Machine LearningOllama (Mistral 7B / Llama 2 7B), FinBERT, Facebook ProphetBackend & APIsFastAPI, UvicornFrontend / UIStreamlit, Rich CLI, Plotly (Sentiment Heatmaps, Charts)🚀 QuickstartPrerequisitesPython 3.10+PostgreSQL running locallyOllama installed locallyAPI Keys (Reddit, News, Binance, Etherscan)1. Installationgit clone [https://github.com/yourusername/CryptoOracle.git](https://github.com/yourusername/CryptoOracle.git)
cd CryptoOracle

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
2. Initialize the Local LLM# Download and run the Mistral model
ollama pull mistral
ollama run mistral
3. Environment ConfigurationCreate a .env file in the root directory:REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret
NEWS_API_KEY=your_key
BINANCE_API_KEY=your_key
ETHERSCAN_API_KEY=your_key
DB_URL=postgresql://user:password@localhost/cryptodb
4. Run the StackOpen separate terminal windows for the following services:# Terminal 1: Start Data Ingestion Scheduler
python -m src.data.scheduler

# Terminal 2: Start FastAPI Backend
uvicorn src.backend.main:app --reload --port 8000

# Terminal 3: Launch Streamlit Dashboard
streamlit run src.frontend.app.py
(Alternatively, use the provided Rich CLI dashboard: python -m src.frontend.cli)Built with 💻 for the open-source crypto quantitative community.
