import yfinance as yf


def store_investment_preference(preference: str):
    """
    Store the user's investment preference into memory.
    Example: 'low risk investments and prefers ETFs'
    """
    from memory import save_user_preference

    save_user_preference(preference)

    return f"Saved user investment preference: {preference}"


def get_stock_price(symbol: str):

    symbol = symbol.upper().strip()

    stock = yf.Ticker(symbol)
    info = stock.info
    hist = stock.history(period="5d")

    current = hist["Close"].iloc[-1]
    if len(hist) >= 2:
        previous = hist["Close"].iloc[-2]
        change = current - previous
        percent = (change / previous) * 100
        arrow = "↑" if change > 0 else "↓"
        change_str = f"{change:+.2f} ({percent:.2f}%) {arrow} vs prev close"
    else:
        change_str = "Change data unavailable (market may be closed)"

    open_price = info.get("open")
    high = info.get("dayHigh")
    low = info.get("dayLow")
    market_cap = info.get("marketCap")
    pe = info.get("trailingPE")
    high52 = info.get("fiftyTwoWeekHigh")
    low52 = info.get("fiftyTwoWeekLow")
    dividend_yield = info.get("dividendYield")
    dividend_rate = info.get("dividendRate")

    if dividend_yield:
        dividend_yield = f"{dividend_yield*100:.2f}%"

    if pe is None:
         interpretation = "P/E ratio not available."
    elif pe < 15:
         interpretation = "This suggests the stock may be undervalued relative to earnings."
    elif 15 <= pe <= 25:
         interpretation = "This suggests the stock is fairly valued compared to earnings."
    else:
         interpretation = "This suggests the stock may be relatively expensive compared to earnings."

    return f"""
{symbol}

{current:.2f} USD
{change_str}

Open: {open_price}
High: {high}
Low: {low}

Market Cap: {market_cap}
P/E Ratio: {pe}
Interpretation of PE ratio: {interpretation}

Dividend Yield: {dividend_yield}
Quarterly Dividend Amount: {dividend_rate}

52-week High: {high52}
52-week Low: {low52}
"""

def get_market_index(index_name: str):

    import yfinance as yf

    index_map = {
        "nifty": ("^NSEI", "Nifty 50"),
        "sensex": ("^BSESN", "Sensex"),
        "s&p": ("^GSPC", "S&P 500"),
        "nasdaq": ("^IXIC", "NASDAQ"),
        "dow": ("^DJI", "Dow Jones")
    }

    index_name = index_name.lower()

    ticker = None
    label = None

    for key in index_map:
        if key in index_name:
            ticker, label = index_map[key]
            break

    if ticker is None:
        return "Market index not supported."

    index = yf.Ticker(ticker)

    hist = index.history(period="5d")
    info = index.info

    current = hist["Close"].iloc[-1]
    if len(hist) >= 2:
        previous = hist["Close"].iloc[-2]
        change = current - previous
        percent = (change / previous) * 100
        arrow = "↑" if change > 0 else "↓"
        change_str = f"{change:+.2f} ({percent:.2f}%) {arrow} vs prev close"
    else:
        change_str = "Change data unavailable (market may be closed)"

    open_price = info.get("open")
    high = info.get("dayHigh")
    low = info.get("dayLow")
    prev_close = info.get("previousClose")

    high52 = info.get("fiftyTwoWeekHigh")
    low52 = info.get("fiftyTwoWeekLow")

    return f"""
{label}

{current:,.2f}
{change_str}

Open: {open_price}
High: {high}
Low: {low}

Previous Close: {prev_close}

52-week High: {high52}
52-week Low: {low52}
"""

import requests
import os

def nytimes_search(query):

    NYT_API_KEY="Vl9nGJAq2mcXBUx9mbdG8n4EGUbMiT3RjdpcEF4C0BNvrykV"
    
    # Improve search relevance for financial questions
    enhanced_query = f"{query} stock market finance"

    url = "https://api.nytimes.com/svc/search/v2/articlesearch.json"
    params = {"q": enhanced_query, "api-key": NYT_API_KEY}

    try:
        response = requests.get(url, params=params)

        if response.status_code != 200:
            return "Error retrieving data from NYTimes API."

        data = response.json()

        if "response" not in data or "docs" not in data["response"]:
            return "No financial news found."

        articles = data["response"]["docs"][:3]

        if not articles:
            return "No recent financial news found."

        results = []

        for a in articles:
            title = a.get("headline", {}).get("main", "No title available")
            date = a.get("pub_date", "Unknown date")
            summary = a.get("abstract", "No summary available")
            link = a.get("web_url", "")

            results.append(
                f"Title: {title}\nPublished: {date}\nSummary: {summary}\nLink: {link}\n"
            )

        return "Recent Financial News:\n\n" + "\n".join(results)

    except Exception as e:
        return f"Error accessing NYTimes API: {str(e)}"
