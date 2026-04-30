import streamlit as st
import pandas as pd
from datetime import date
from main import financial_advisor, financial_advisor_verbose
from trading_tool import deep_stock_analysis, deep_stock_analysis_verbose

st.set_page_config(page_title="AI Financial Advisor", layout="wide")
st.markdown("## AI Financial Advisor Agent: Your Own Wall Street Trading Firm")

# ---------------------------------------------------------------------------
# Sidebar – about
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("About")
    st.markdown("""
**Financial Advisor Agent**
- Real-time stock prices & indices
- Financial news (NYTimes)
- General financial advice

**Deep Stock Analysis** *(new)*
- 13 specialized AI agents
- Analyst → Research debate → Trader → Risk debate
- Final BUY / SELL / HOLD decision
- Powered by NVIDIA Nemotron 3 Nano and GLM 4.5 Air (free models)
- ⚠️ Takes 3–8 minutes per stock
""")

# ---------------------------------------------------------------------------
# Tab layout
# ---------------------------------------------------------------------------
tab_advisor, tab_deep, tab_expenses = st.tabs([
    "💬 Financial Advisor",
    "🔬 Deep Stock Analysis",
    "📊 Expense Tracker",
])

# ── Tab 1: Financial Advisor (existing) ────────────────────────────────────
with tab_advisor:
    st.subheader("Ask the Financial Advisor")
    st.caption(
        "Ask about stock prices, market indices, financial news, budgeting, "
        "or request a deep analysis (e.g. 'Should I buy NVDA?')."
    )

    user_input = st.text_input("Your question", key="advisor_input",
                               placeholder="e.g. What is the current price of AAPL?")

    if st.button("Submit", key="advisor_submit"):
        if user_input.strip():
            with st.spinner("Thinking... (deep analysis requests may take several minutes)"):
                response, steps = financial_advisor_verbose(user_input)

            if steps:
                with st.expander("🔍 Reasoning Process", expanded=False):
                    tool_num = 0
                    for step in steps:
                        if step["type"] == "ethics_check":
                            status = "✓ PASSED" if step["passed"] else "✗ FAILED"
                            color  = "green" if step["passed"] else "red"
                            st.markdown(f"**Ethics Check:** :{color}[{status}]")
                            st.divider()
                        elif step["type"] == "memory" and step["items"]:
                            st.markdown("**User Memory (Vector DB):**")
                            for mem in step["items"]:
                                st.markdown(f"- {mem}")
                            st.divider()
                        elif step["type"] == "tool_call":
                            tool_num += 1
                            st.markdown(f"**Tool {tool_num}: `{step['name']}`**")
                            st.markdown("*Input:*")
                            st.json(step["input"])
                            st.markdown("*Output:*")
                            st.text(step["output"][:2000] + ("..." if len(step["output"]) > 2000 else ""))
                            st.divider()

            st.subheader("Response")
            st.markdown(response)
        else:
            st.warning("Please enter a question.")

# ── Tab 2: Deep Stock Analysis (new) ───────────────────────────────────────
with tab_deep:
    st.subheader("Multi-Agent Deep Stock Analysis")
    st.markdown("""
Run a full institutional-grade analysis using **13 specialized AI agents**:

| Phase | Agents |
|-------|--------|
| 1. Analysis | Market, News, Fundamentals, Sentiment analysts |
| 2. Research | Bull researcher vs Bear researcher + Research Manager (judge) |
| 3. Trading | Trader agent creates execution plan |
| 4. Risk | Aggressive / Neutral / Conservative debaters + Risk Manager (judge) |

**Output:** BUY / SELL / HOLD with detailed reasoning at each stage.
""")

    col1, col2 = st.columns([2, 2])
    with col1:
        ticker_input = st.text_input("Stock Ticker", placeholder="e.g. NVDA",
                                     key="deep_ticker").upper().strip()
    with col2:
        analysis_date = st.date_input("Analysis Date", value=date.today(),
                                      key="deep_date")

    use_deep = st.toggle("Enable deep thinking (slower, more thorough)", value=False, key="deep_mode")

    if use_deep:
        st.warning("⏱️ Deep thinking enabled: 13 agents × 2 LLM tiers, typically **5–10 minutes**.")
    else:
        st.info("⚡ Quick mode: all agents use the fast model, typically **2–4 minutes**.")

    if st.button("Run Analysis", key="deep_submit", type="primary"):
        if not ticker_input:
            st.error("Please enter a stock ticker.")
        else:
            query = f"{ticker_input} {analysis_date}"
            mode_label = "deep" if use_deep else "quick"
            with st.spinner(f"Running {mode_label} analysis for {ticker_input}... please wait."):
                result, agents_flow = deep_stock_analysis_verbose(query, use_deep_thinking=use_deep)

            st.success("Analysis complete!")

            if agents_flow:
                with st.expander("🤖 Agent Progression (1 → 12)", expanded=True):
                    current_phase = None
                    for step in agents_flow:
                        if step["phase"] != current_phase:
                            current_phase = step["phase"]
                            st.markdown(f"**{current_phase}**")
                        st.markdown(
                            f"&nbsp;&nbsp;&nbsp;`{step['num']:02d}` **{step['agent']}** → {step['summary']}"
                        )

            st.markdown(result)

            # Extract decision for filename (matches CLI format)
            import re
            m = re.search(r'\*\*Decision:\s*(BUY|SELL|HOLD)\*\*', result, re.IGNORECASE)
            decision = m.group(1).upper() if m else "UNKNOWN"

            st.download_button(
                label="Download Report",
                data=result,
                file_name=f"{analysis_date}_{ticker_input}_{decision}.md",
                mime="text/markdown",
            )

# ── Tab 3: Expense Tracker (existing) ──────────────────────────────────────
with tab_expenses:
    st.subheader("Expense Tracker")
    st.caption("Upload an Excel file with 'Category' and 'Amount' columns.")

    uploaded_file = st.file_uploader("Upload your expense file", type=["xlsx"],
                                     key="expense_upload")

    if uploaded_file:
        df = pd.read_excel(uploaded_file)

        st.subheader("Uploaded Data")
        st.dataframe(df)

        if "Category" in df.columns and "Amount" in df.columns:
            st.subheader("Expense Summary")
            total = df["Amount"].sum()
            category_summary = df.groupby("Category")["Amount"].sum()

            st.write(f"**Total Expenses:** ${total:,.2f}")
            st.write("**Spending by Category**")
            st.bar_chart(category_summary)
        else:
            st.error("File must contain 'Category' and 'Amount' columns.")

    st.divider()
    st.subheader("Ask a Financial Question")
    user_input = st.text_input("Ask a financial question", key="expense_advisor_input",
                               placeholder="e.g. How can I reduce my food spending?")

    if st.button("Submit", key="expense_advisor_submit"):
        if user_input:
            with st.spinner("Thinking..."):
                response = financial_advisor(user_input)
            st.subheader("Agent Response")
            st.write(response)
        else:
            st.warning("Please enter a question.")
