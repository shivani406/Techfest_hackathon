🔮 CryptoOracle: AI-Powered Quantitative Alpha Engine

MISSION STATEMENT
A strictly self-hosted, end-to-end algorithmic pipeline that ingests real-time market data, processes social sentiment via local LLMs, tracks on-chain whale movements, forecasts price action, and generates deterministic, explainable trading signals.

⚡ The Self-Hosted Architecture Advantage

CryptoOracle is engineered to run entirely on dedicated local hardware. By leveraging local Large Language Models (Ollama) and CPU-optimized forecasting models (Prophet), the architecture guarantees:

🔒 100% Data Privacy (No data leaves your machine)

💸 Zero API Inference Costs (No paying for OpenAI/Anthropic tokens)

🛡️ Immunity to External Rate Limits ---

🏗️ High-Level System Architecture

The system operates in four distinct layers, running asynchronously to feed the final trading algorithm.

📥 Data Ingestion Layer: Reddit (PRAW), NewsAPI, Binance API, and Etherscan/Solscan APIs fetch data via APScheduler or Celery.

🗄️ Relational Storage Layer: All raw and processed data is saved to a local PostgreSQL or SQLite database.

🧠 Intelligence & AI Layer: Data is routed through the Local LLM (Sentiment) and Prophet (Price Forecasting).

📊 Execution & UI Layer: The Signal Generation Logic processes the AI outputs and serves them via FastAPI to a Streamlit dashboard.

⚙️ Core Engineering Pipelines

The system is decoupled into four highly specialized micro-pipelines. Here is the exact data flow for each module:

1️⃣ Natural Language Processing (Sentiment)

Utilizes Mistral 7B (via Ollama) or FinBERT for zero-cost, context-aware NLP classification.

Pipeline Stage

Component

Detail / Example Data

1. Input

Raw Post from DB

"Bitcoin just broke ATH! 🚀 This is the start of the next bull run!"

2. Engine

Local LLM Server

Ollama running Mistral 7B or Llama 2 7B

3. Prompt

Few-Shot Learning

"Classify as BULLISH, BEARISH, or NEUTRAL. Return only classification + confidence."

4. Output

Database Storage

🟢 BULLISH (Confidence: 0.92)

2️⃣ On-Chain Forensics (Whale Tracking)

Monitors mempools and block explorers for high-net-worth capital rotation to detect institutional accumulation or distribution.

Filter Criteria

Detected Action

Signal Interpretation

Value > $1M USD

Exchange Inflow

🔴 Bearish (Possible selling pressure)

From != To

Exchange Outflow

🟢 Bullish (Accumulation phase)

(No self-transfers)

Whale-to-Whale

⚪ Neutral (OTC Trade)

3️⃣ Quantitative Price Prediction

Uses Facebook's Prophet model. Optimized for CPU environments, handling missing datasets, and mapping volatile crypto market seasonality.

📥 Input Features (15-min rolling windows):

Price Action: OHLCV (Open, High, Low, Close, Volume)

Tech Indicators: RSI, MACD, Moving Averages

NLP Sentiment: Average bullish score from the last 1 hour

Whale Activity: Net inflow/outflow from the last 1 hour

🤖 Engine: Prophet Time-Series Model

📤 Outputs:

Direction: UP / DOWN / SIDEWAYS

Timeframes: Next 1h, 4h, 24h

Target Confidence: > 55% accuracy

4️⃣ Deterministic Signal Engine

The convergence layer. Applies strict logical matrices to the aggregated multi-modal data to produce actionable, explainable trade signals.

The Decision Matrix Logic:

🟢 STRONG BUY: IF Sentiment > 0.7 AND Prediction = UP AND Whales = Accumulating

🔴 STRONG SELL: IF Sentiment < 0.3 AND Prediction = DOWN AND Whales = Distributing

🟡 MODERATE BUY: IF Sentiment > 0.6 AND Prediction = UP

⚪ HOLD / WAIT: ELSE (Default Fallback)

JSON Output Example (Explainable AI):

{
  "SIGNAL": "BUY (STRONG)",
  "CONFIDENCE": "82%",
  "REASONING": [
    "Reddit sentiment very positive (0.82)",
    "Price model predicts +3.2% in next 4h",
    "Whales accumulated 2,500 BTC in last hour",
    "Trading volume 40% above average"
  ]
}


💻 Tech Stack Summary

Domain

Frameworks & Libraries

Data Engineering

Python 3.10, PRAW, NewsAPI, python-binance, web3.py, APScheduler

Relational DB

PostgreSQL 15+ / SQLite (via SQLAlchemy ORM)

Machine Learning

Ollama (Mistral 7B / Llama 2), HuggingFace FinBERT, Prophet

Backend & Routing

FastAPI, Uvicorn, Pydantic

Frontend UI

Streamlit, Rich (CLI Dashboards), Plotly

🛠️ Deployment & Installation

1. System Requirements

Linux / macOS / Windows (WSL2 recommended)

Python 3.10+

PostgreSQL Service running

Minimum 16GB RAM (Required for running 7B LLM models locally)

2. Environment Setup

Clone the repository and initialize the Python environment:

git clone [https://github.com/yourusername/CryptoOracle.git](https://github.com/yourusername/CryptoOracle.git)
cd CryptoOracle

# Initialize isolated environment
python3 -m venv venv
source venv/bin/activate

# Install core and ML dependencies
pip install -r requirements.txt


3. Local LLM Initialization (Ollama)

Install Ollama, then pull and serve the inference model:

ollama pull mistral
ollama serve


4. Configuration (.env)

Create a .env file in the root directory to authorize ingestion endpoints:

# API Keys for Data Ingestion
REDDIT_CLIENT_ID="your_reddit_id"
REDDIT_CLIENT_SECRET="your_reddit_secret"
NEWS_API_KEY="your_newsapi_key"
BINANCE_API_KEY="your_binance_key"
ETHERSCAN_API_KEY="your_etherscan_key"

# Database Configuration
DB_URL="postgresql://admin:password@localhost:5432/cryptooracle"


5. Executing the Stack

For a full local deployment, start the services in separate terminal instances:

# Terminal 1: Start the Data Ingestion Layer
python -m src.orchestration.scheduler

# Terminal 2: Boot the FastAPI Backend Engine
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 3: Launch the Streamlit Analytical Dashboard
streamlit run src.ui.dashboard.py


Disclaimer: This software is for educational and research purposes only. It does not constitute financial advice. Cryptocurrency markets are highly volatile.
