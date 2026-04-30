"""
trading_tool.py
Integrates TradingAgents multi-agent system following the official usage pattern.
Uses OpenRouter to call free LLMs (OPENROUTER_API_KEY required).
"""

import sys
import os
import yfinance as yf
from datetime import date


def _fetch_realtime_price(ticker: str) -> str:
    """Fetch real-time price via yfinance and return a verified price block."""
    try:
        stock = yf.Ticker(ticker)
        hist  = stock.history(period="2d")
        info  = stock.info
        if hist.empty:
            return ""
        current  = hist["Close"].iloc[-1]
        previous = hist["Close"].iloc[-2]
        change   = current - previous
        pct      = (change / previous) * 100
        arrow    = "↑" if change >= 0 else "↓"
        high52   = info.get("fiftyTwoWeekHigh", "N/A")
        low52    = info.get("fiftyTwoWeekLow",  "N/A")
        return (
            f"### ✅ Verified Real-Time Price (yfinance)\n"
            f"**{ticker}:  ${current:.2f}**  "
            f"{change:+.2f} ({pct:.2f}%) {arrow} today\n"
            f"52-week range: ${low52} – ${high52}\n"
            f"> ⚠️ Use this verified price. Ignore any conflicting figures in the AI analysis below.\n"
        )
    except Exception:
        return ""

# Add TradingAgents to Python path
TRADING_AGENTS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "TradingAgents")
if TRADING_AGENTS_PATH not in sys.path:
    sys.path.append(TRADING_AGENTS_PATH)  # append, not insert(0), to avoid shadowing local main.py

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# Build config following official example
config = DEFAULT_CONFIG.copy()
config["llm_provider"]     = "openrouter"
config["deep_think_llm"]   = "z-ai/glm-4.5-air:free"              # Z.AI GLM 4.5 Air
config["quick_think_llm"]  = "nvidia/nemotron-3-nano-30b-a3b:free" # NVIDIA Nemotron 3 Nano 30B
config["max_debate_rounds"] = 1
config["max_risk_discuss_rounds"] = 1
config["data_vendors"] = {
    "core_stock_apis":      "yfinance",
    "technical_indicators": "yfinance",
    "fundamental_data":     "yfinance",
    "news_data":            "yfinance",
}

# Two singletons: one with deep thinking, one quick-only
_ta_deep: TradingAgentsGraph = None
_ta_quick: TradingAgentsGraph = None

def _get_ta(use_deep_thinking: bool = True) -> TradingAgentsGraph:
    global _ta_deep, _ta_quick
    if use_deep_thinking:
        if _ta_deep is None:
            _ta_deep = TradingAgentsGraph(debug=True, config=config)
        return _ta_deep
    else:
        if _ta_quick is None:
            quick_config = config.copy()
            quick_config["deep_think_llm"] = config["quick_think_llm"]  # use quick model for everything
            _ta_quick = TradingAgentsGraph(debug=True, config=quick_config)
        return _ta_quick


def _snip(text: str, n: int = 200) -> str:
    if not text:
        return "N/A"
    lines = [l.strip() for l in str(text).split("\n") if l.strip() and not l.strip().startswith("#")]
    clean = " ".join(lines)
    return clean[:n] + ("..." if len(clean) > n else "")


def _build_agents_flow(final_state: dict, decision: str) -> list[dict]:
    ds = final_state.get("investment_debate_state") or {}
    rs = final_state.get("risk_debate_state") or {}
    return [
        {"num":  1, "phase": "Phase 1 — Analysis",        "agent": "Market Analyst",       "summary": _snip(final_state.get("market_report", ""))},
        {"num":  2, "phase": "Phase 1 — Analysis",        "agent": "News Analyst",          "summary": _snip(final_state.get("news_report", ""))},
        {"num":  3, "phase": "Phase 1 — Analysis",        "agent": "Fundamentals Analyst",  "summary": _snip(final_state.get("fundamentals_report", ""))},
        {"num":  4, "phase": "Phase 1 — Analysis",        "agent": "Social Media Analyst",  "summary": _snip(final_state.get("sentiment_report", ""))},
        {"num":  5, "phase": "Phase 2 — Research Debate", "agent": "Bull Researcher",       "summary": _snip(ds.get("bull_history", ""))},
        {"num":  6, "phase": "Phase 2 — Research Debate", "agent": "Bear Researcher",       "summary": _snip(ds.get("bear_history", ""))},
        {"num":  7, "phase": "Phase 2 — Research Debate", "agent": "Research Manager",      "summary": _snip(ds.get("judge_decision", ""))},
        {"num":  8, "phase": "Phase 3 — Trading",         "agent": "Trader",                "summary": _snip(final_state.get("trader_investment_plan", ""))},
        {"num":  9, "phase": "Phase 4 — Risk Analysis",   "agent": "Aggressive Analyst",    "summary": _snip(rs.get("current_aggressive_response", ""))},
        {"num": 10, "phase": "Phase 4 — Risk Analysis",   "agent": "Conservative Analyst",  "summary": _snip(rs.get("current_conservative_response", ""))},
        {"num": 11, "phase": "Phase 4 — Risk Analysis",   "agent": "Neutral Analyst",       "summary": _snip(rs.get("current_neutral_response", ""))},
        {"num": 12, "phase": "Phase 4 — Risk Analysis",   "agent": "Risk Judge",            "summary": _snip(rs.get("judge_decision", ""))},
    ]


def deep_stock_analysis(query: str, use_deep_thinking: bool = True) -> str:
    report, _ = deep_stock_analysis_verbose(query, use_deep_thinking)
    return report


def deep_stock_analysis_verbose(query: str, use_deep_thinking: bool = True) -> tuple[str, list[dict]]:
    """Returns (report, agents_flow) — agents_flow is the 12-agent progression list."""
    if not os.environ.get("OPENROUTER_API_KEY"):
        return "Error: OPENROUTER_API_KEY is not set.", []

    parts = query.strip().split()
    ticker     = parts[0].upper()
    trade_date = parts[1] if len(parts) >= 2 else str(date.today())

    price_block = _fetch_realtime_price(ticker)

    max_retries = 3
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            ta = _get_ta(use_deep_thinking)
            final_state, decision = ta.propagate(ticker, trade_date)

            agents_flow = _build_agents_flow(final_state, decision)
            report = (
                f"## Deep Analysis: {ticker} ({trade_date})\n"
                f"**Decision: {decision}**\n\n"
                f"{price_block}\n"
                f"### Investment Plan\n{final_state.get('investment_plan', 'N/A')}\n\n"
                f"### Trader Plan\n{final_state.get('trader_investment_plan', 'N/A')}\n\n"
                f"### Risk Decision\n{final_state.get('final_trade_decision', 'N/A')}"
            )
            return report, agents_flow
        except Exception as e:
            last_error = e
            err_str = str(e)
            if attempt < max_retries and any(
                code in err_str for code in ("502", "503", "504", "Network connection lost", "Connection")
            ):
                import time
                wait = 10 * attempt
                print(f"[Retry {attempt}/{max_retries}] OpenRouter error: {e}. Retrying in {wait}s…")
                time.sleep(wait)
                continue
            break

    return f"Deep analysis failed for {ticker}: {last_error}\n\n{price_block}", []
