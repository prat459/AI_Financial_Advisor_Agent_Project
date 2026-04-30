import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, Tool
from tools import get_stock_price, store_investment_preference, get_market_index, nytimes_search
from memory import save_user_preference, build_vector_db, retrieve_memory
from ethics import safety_check


# LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    convert_system_message_to_human=True
)


# Short-term memory
memory = ConversationBufferMemory(memory_key="chat_history")

tools = [

    Tool(
        name="StockPrice",
        func=get_stock_price,
        description="Get detailed stock information for a public company using its ticker symbol. Example inputs: AAPL, TSLA, MSFT, NVDA. Return the tool output EXACTLY as the final answer without summarizing or modifying it."
    ),

    Tool(
        name="MarketIndex",
        func=get_market_index,
        description="Get the current value and daily change of major market indices such as Nifty 50, Sensex, S&P 500, NASDAQ, or Dow Jones.Return the tool output EXACTLY as the final answer without summarizing or modifying it."
    ),

##    Tool(
  #      name="SaveInvestmentPreference",
   #     func=store_investment_preference,
    #    description="Store the user's investment preference such as low risk, prefers ETFs, avoids crypto, or long-term investing."
##  )

Tool(
    name="FinancialNews",
    func=nytimes_search,
    description="Search recent financial news using the New York Times API. Use this tool when the user asks why a stock or market is moving.Return the tool output EXACTLY as the final answer without summarizing or modifying it."
)

]


# Initialize agent
agent = initialize_agent(
    tools,
    llm,
    agent="chat-zero-shot-react-description",
    memory=memory,
    verbose=True, 
    handle_parsing_errors = True
)


# Example long-term memory storage
save_user_preference("User risk tolerance is low")
save_user_preference("User wants to save 20 percent of income")

vector_db = build_vector_db()


def financial_advisor(query):

    # Ethics check
    if not safety_check(query):
        return "Sorry, I cannot assist with unsafe or illegal financial requests."

    # Retrieve long-term memory
    memories = retrieve_memory(vector_db, query)

    context = f"""
You are an AI financial advisor.

You have tools to fetch stock prices, market index values, and financial news.

Use the tools ONLY when the user asks for real-time financial data
such as stock prices, indices, or market news.

If the user asks for general financial advice (for example budgeting,
saving money, investment strategies, or financial planning),
answer directly without using tools.

User financial preferences:
{memories}

User question:
{query}
"""

    response = agent.run(context)

    return response


# CLI Demo
if __name__ == "__main__":

    print("💰 AI Financial Advisor Agent")

    while True:

        user_input = input("\nAsk your financial question: ")

        if user_input == "exit":
            break

        answer = financial_advisor(user_input)

        print("\nAgent response:", answer)
