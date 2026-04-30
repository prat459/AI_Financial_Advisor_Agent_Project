# AI Financial Advisor Agent: Your Own Wall Street Trading Firm

### An AI-powered financial advisor that simulates a trading firm with 13 specialized agents, providing institutional-level professional stock investment advice. It includes real-time stock data, spending analysis, and ethics checks, along with a function to save reports. ###
---

## Project Structure

Architecture: Two-Layer Pipeline

```
User (Streamlit UI / Terminal)
        │
        ▼
[ Layer 1 ]  Financial Advisor Agent        ←  main.py / app1.py
             LangChain + Google Gemini
             Tools: StockPrice, MarketIndex, FinancialNews, DeepStockAnalysis
        │
        │  (calls deep_stock_analysis in trading_tool.py)
        ▼
[ Layer 2 ]  TradingAgents Multi-Agent System
             13 AI agents:
            Analysis (4 Agents):Market, News, Fundamentals, Sentiment.
            Research Debate(3 Agents)(Bull, Bear, Manager)
            Trading (1 Agent):Trader
            Risk team(4 Agent):Aggressive,Neutral,Conservative, Manager.
            Signal (1 Agent): Signal Processor

             LLMs via OpenRouter, NVIDIA Nemotron 3 Nano for quick thinking, and GLM 4.5 Air for deep thinking.

             Returns: BUY / SELL / HOLD + full reasoning
```

Layer 1 handles the conversational interface and simple queries. Layer 2 is only triggered for deep stock analysis requests and runs the full 13-agent pipeline.

---

## Features

- Real-time stock prices, P/E ratios, dividends, 52-week range (via yfinance)
- Major market indices: S&P 500, NASDAQ, Dow Jones
- Financial news search via New York Times API
- Deep multi-agent stock analysis (BUY / SELL / HOLD recommendation)
- User preference memory (vector DB)
- Ethics & safety guardrails

---

## Prerequisites

- Python 3.10+
- API keys for the services below

---

## API Keys Required

| Key | Purpose | Get it at |
|-----|---------|-----------|
| `GOOGLE_API_KEY` | Gemini LLM (advisor) | Google AI Studio |
| `HF_TOKEN` | HuggingFace embeddings | huggingface.co/settings/tokens |
| `NYT_API_KEY` | Financial news | developer.nytimes.com |
| `OPENROUTER_API_KEY` | Deep analysis LLMs (free) | openrouter.ai/keys |

Edit `api_keys.bat` and fill in your keys.

---

## How to Run

###  Open CMD and activate the conda environment (If use Anaconda)

```cmd
conda activate YOUR_ENV_NAME (fin_ai)
```

### 1. Install dependencies
```cmd
install pip

# Layer 1
pip install langchain-huggingface faiss-cpu sentence-transformers
pip install yfinance pandas openpyxl requests

# Layer 2 
pip install -r "Your directory of TradingAgents\requirements.txt"
pip install streamlit langchain langchain-google-genai langchain-community
```


### 2. Load API keys (must do this first, every new CMD session)

```cmd
###Edit `api_keys.bat` and fill in your keys.
cd Your Directory\FINANCIAL_ADVISOR_AGENT_ADDED
api_keys.bat
```

### 3a. Run the Streamlit web app

```cmd
streamlit run app1.py
```

Then open http://localhost:8501 in your browser.

### 3b. Or run the CLI version

```cmd
python main.py
```

---

## Features

### Financial Advisor (Tab 1 / CLI)
- Real-time stock prices, P/E ratio, dividends, 52-week range
- Major market indices: S&P 500, NASDAQ, Dow Jones, Nifty 50, Sensex
- Financial news via New York Times API
- General financial advice: budgeting, saving, planning
- Long-term memory of user preferences (FAISS vector store)

### Deep Stock Analysis (Tab 2)
Uses **13 specialized AI agents** powered by NVIDIA Nemotron 3 Nano and GLM 4.5 Air (free models via OpenRouter):

| Phase | Agents |
|-------|--------|
| 1. Analysis | Market, News, Fundamentals, Sentiment analysts |
| 2. Research | Bull vs Bear researcher + Research Manager |
| 3. Trading | Trader agent creates execution plan |
| 4. Risk | Aggressive / Neutral / Conservative + Risk Manager |

Output: **BUY / SELL / HOLD** with full reasoning. Takes 3–8 minutes per stock.

### Expense Tracker (Tab 3)
Upload an Excel file with `Category` and `Amount` columns for spending breakdown.

---

## Citation

This project utilizes the open-source code from the paper **[TradingAgents: Multi-Agent LLM Financial Trading Framework](https://arxiv.org/abs/2412.20138) for the second layer**.
