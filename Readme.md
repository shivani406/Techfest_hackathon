🔮 CryptoOracleAutonomous AI-Powered Quantitative & Sentiment Alpha EngineMission Statement: A strictly self-hosted, end-to-end algorithmic pipeline that ingests real-time market data, processes social sentiment via local LLMs, tracks on-chain whale movements, forecasts price action, and generates deterministic, explainable trading signals.⚡ The Self-Hosted ArchitectureCryptoOracle is engineered to run entirely on dedicated local hardware (Self-Hosted Environment). By leveraging local LLMs (Ollama) and CPU-optimized forecasting models (Facebook Prophet), the architecture guarantees zero API inference costs, 100% data privacy, and immunity to third-party API rate limits.🏗️ High-Level System FlowBased on the system topology and data ingestion models.flowchart TB
    subgraph "Data Ingestion Layer (APScheduler / Celery)"
        direction LR
        R[Reddit API <br> PRAW] --> S{Python Scheduler}
        N[NewsAPI.org] --> S
        B[Binance API] --> S
        E[Etherscan / Solscan] --> S
    end

    subgraph "Relational Storage (PostgreSQL / SQLite)"
        S --> DB[(Raw Data Storage)]
        DB -.-> T1(reddit_posts)
        DB -.-> T2(news_articles)
        DB -.-> T3(price_candles)
        DB -.-> T4(whale_txs)
    end

    subgraph "Intelligence & AI Layer"
        direction LR
        DB --> LLM[Ollama Local LLM <br> Sentiment Analyzer]
        DB --> PROPHET[ML Model <br> Price Predictor]
    end

    subgraph "Presentation & Execution"
        LLM --> SG((Signal Generation Logic))
        PROPHET --> SG
        SG --> API[FastAPI Endpoints]
        API --> UI[Dashboard <br> Streamlit / Rich CLI]
    end
⚙️ Core Engineering PipelinesThe system is decoupled into four highly specialized micro-pipelines.1. Natural Language Processing (Sentiment)Utilizes Mistral 7B (via Ollama) or FinBERT (fallback) for zero-cost, context-aware NLP classification.┌─────────────────────────────────────────────────────────────────┐
│                 SENTIMENT ANALYSIS PIPELINE                     │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐                                              │
│  │ Raw Post     │  "Bitcoin just broke ATH! 🚀 This is        │
│  │ from DB      │   the start of the next bull run!"          │
│  └──────┬───────┘                                              │
│         ▼                                                       │
│  ┌──────────────────────────────────────────────────────┐      │
│  │            OLLAMA (Local LLM Server)                 │      │
│  │  ┌────────────────────────────────────────────┐     │      │
│  │  │  Mistral 7B or Llama 2 7B Model           │     │      │
│  │  └────────────────────────────────────────────┘     │      │
│  └──────────────────────────────────────────────────────┘      │
│         ▼                                                       │
│  ┌──────────────────────────────────────────────────────┐      │
│  │  Prompt Engineering (Few-shot Learning)              │      │
│  │                                                       │      │
│  │  Prompt Template:                                     │      │
│  │  "Classify the sentiment of this crypto post as      │      │
│  │   BULLISH, BEARISH, or NEUTRAL.                      │      │
│  │   Examples:                                           │      │
│  │   Post: 'Bitcoin is going to $100k!' → BULLISH       │      │
│  │   Now analyze: {post_text}                            │      │
│  │   Return only: BULLISH/BEARISH/NEUTRAL + confidence" │      │
│  └──────────────────────────────────────────────────────┘      │
│         ▼                                                       │
│  ┌──────────────┐                                              │
│  │ Output:      │  BULLISH (confidence: 0.92)                 │
│  │ Stored in DB │                                              │
│  └──────────────┘                                              │
└─────────────────────────────────────────────────────────────────┘
2. On-Chain ForensicsMonitors mempools and block explorers for high-net-worth capital rotation.┌─────────────────────────────────────────────────────────────────┐
│                   ON-CHAIN ANALYTICS PIPELINE                   │
├─────────────────────────────────────────────────────────────────┤
│  Etherscan API ────┐                                           │
│  (web3.py)         │    ┌──────────────────────────────┐       │
│                    ├───▶│  Filter: Value > $1M USD    │       │
│  Solscan API ──────┘    │  AND from != to (not self)  │       │
│                         └──────────────────────────────┘       │
│                                    ▼                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  SIGNAL INTERPRETATION                                  │   │
│  │  • Exchange inflow  →  Possible selling pressure       │   │
│  │  • Exchange outflow →  Accumulation (bullish)          │   │
│  │  • Whale-to-whale   →  Neutral (OTC trade)             │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
3. Quantitative Price PredictionUses Facebook's Prophet model. Optimized for CPU environments, handling missing datasets, and mapping volatile crypto market seasonality.┌─────────────────────────────────────────────────────────────────┐
│                   PRICE PREDICTION PIPELINE                     │
├─────────────────────────────────────────────────────────────────┤
│  INPUT FEATURES (15-min rolling windows):                      │
│  • OHLCV (Open, High, Low, Close, Volume)                      │
│  • Tech Indicators: RSI, MACD, Moving Averages                 │
│  • NLP Sentiment: Avg bullish score (last 1hr)                 │
│  • Whale Activity: Net inflow/outflow (last 1hr)               │
│                              ▼                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │           PROPHET (Facebook) - CPU Friendly            │    │
│  └────────────────────────────────────────────────────────┘    │
│                              ▼                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  OUTPUT:                                               │    │
│  │  • Direction: UP/DOWN/SIDEWAYS                        │    │
│  │  • Confidence: 55-85% (target >55% accuracy)          │    │
│  │  • Timeframe: Next 1h, 4h, 24h                        │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
4. Deterministic Signal EngineThe convergence layer. Applies strict logical matrices to the aggregated multi-modal data to produce actionable, explainable trade signals.┌─────────────────────────────────────────────────────────────────┐
│                    SIGNAL GENERATION ENGINE                     │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  DECISION MATRIX LOGIC                                  │   │
│  │                                                         │   │
│  │  IF sentiment > 0.7 AND prediction = UP AND whales =   │   │
│  │     accumulating:                                      │   │
│  │         → STRONG BUY SIGNAL                            │   │
│  │                                                         │   │
│  │  IF sentiment < 0.3 AND prediction = DOWN AND whales = │   │
│  │     distributing:                                      │   │
│  │         → STRONG SELL SIGNAL                           │   │
│  │                                                         │   │
│  │  IF sentiment > 0.6 AND prediction = UP:               │   │
│  │         → MODERATE BUY                                 │   │
│  │                                                         │   │
│  │  ELSE: → HOLD / WAIT                                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  JSON OUTPUT (EXPLAINABLE AI)                           │   │
│  │  {                                                      │   │
│  │    "SIGNAL": "BUY (STRONG)",                            │   │
│  │    "CONFIDENCE": "82%",                                 │   │
│  │    "REASONING": [                                       │   │
│  │      "Reddit sentiment very positive (0.82)",           │   │
│  │      "Price model predicts +3.2% in next 4h",           │   │
│  │      "Whales accumulated 2,500 BTC in last hour"        │   │
│  │    ]                                                    │   │
│  │  }                                                      │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
💻 Tech Stack SummaryDomainFrameworks & LibrariesData EngineeringPython 3.10, PRAW, NewsAPI, python-binance, web3.py, APScheduler / CeleryRelational DBPostgreSQL 15+ / SQLite (via SQLAlchemy ORM)Machine LearningOllama (Mistral 7B / Llama 2), HuggingFace FinBERT, Facebook ProphetBackend & RoutingFastAPI, Uvicorn, PydanticFrontend UIStreamlit, Rich (CLI Dashboards), Plotly🛠️ Deployment & Installation1. System RequirementsLinux/macOS/Windows (WSL2 recommended for Windows)Python 3.10+PostgreSQL Service runningMinimum 16GB RAM (for running 7B LLM models locally)2. Environment SetupClone the repository and initialize the Python environment:git clone [https://github.com/yourusername/CryptoOracle.git](https://github.com/yourusername/CryptoOracle.git)
cd CryptoOracle

# Initialize isolated environment
python3 -m venv venv
source venv/bin/activate

# Install core and ML dependencies
pip install -r requirements.txt
3. Local LLM Initialization (Ollama)Install Ollama, then pull the inference model:ollama pull mistral
ollama serve
4. Configuration (.env)Create a .env file in the root directory to authorize ingestion endpoints:# API Keys for Data Ingestion
REDDIT_CLIENT_ID="your_reddit_id"
REDDIT_CLIENT_SECRET="your_reddit_secret"
NEWS_API_KEY="your_newsapi_key"
BINANCE_API_KEY="your_binance_key"
ETHERSCAN_API_KEY="your_etherscan_key"

# Database Configuration
DB_URL="postgresql://admin:password@localhost:5432/cryptooracle"
5. Executing the StackFor a full local deployment, start the services in separate terminal instances:# 1. Start the Data Ingestion & Orchestration Layer
python -m src.orchestration.scheduler

# 2. Boot the FastAPI Backend Engine
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# 3. Launch the Streamlit Analytical Dashboard
streamlit run src.ui.dashboard.py
Disclaimer: This software is for educational and research purposes only. It does not constitute financial advice. Cryptocurrency markets are highly volatile.
