#functions
'''
#yahoo finance 
get_data - daily
get_live_price - yearly? - done
get_options_chain - monthly


#yfinance
get_income_statement() - yearly- last 4 years - done
get_balance_sheet()
get_cash_flow()

#analyst info - weekly 
ticker.recommendations
ticker.info.get('targetMeanPrice')

'''
#note: some of these functions return a df automatically, others don't 
from yahoo_fin import stock_info, news, options 
# from ticker_loader import get_tradable_tickers
# from my_scrapers.sec import get_sec_filings_incremental 
# # from db import get_last_scraped_date, update_last_scraped_date, store_to_db #yep, need to import get_last_date
# from utils import get_default_start_date
# from ticker_loader import get_tradable_tickers
import yfinance as yf
import pandas as pd
'''
def get_yahoo_price(ticker_symbol: str) -> float:
    """Returns the current live price for a given ticker."""
    return stock_info.get_live_price(ticker_symbol)

def get_yahoo_historical_data(ticker_symbol: str, start_date=None, end_date=None, index_as_date=True):
    """Fetches historical price data for a ticker using yahoo_fin."""
    return stock_info.get_data(ticker_symbol, start_date=start_date, end_date=end_date, index_as_date=index_as_date)
'''
def get_yahoo_options_data(ticker_symbol: str): ###runs 
    """Returns two DataFrames: calls and puts."""
    from yahoo_fin import options
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    chain = options.get_options_chain(ticker_symbol)
    calls_df = chain["calls"]
    puts_df = chain["puts"]
    return calls_df, puts_df

# def get_yahoo_options_data(ticker_symbol: str):
#     """Gets options chain data for a ticker."""
#     return options.get_options_chain(ticker_symbol)
'''
def get_yfinance_fundamentals(ticker_symbol: str):
    """Returns a combined DataFrame of income, balance sheet, and cash flow."""
    import yfinance as yf
    import pandas as pd

    ticker = yf.Ticker(ticker_symbol)
    income = ticker.financials
    balance = ticker.balance_sheet
    cashflow = ticker.cashflow

    # Add labels and concatenate
    income.index.name = "metric"
    income_df = income.T.assign(statement="income")

    balance.index.name = "metric"
    balance_df = balance.T.assign(statement="balance")

    cashflow.index.name = "metric"
    cashflow_df = cashflow.T.assign(statement="cashflow")

    df = pd.concat([income_df, balance_df, cashflow_df])
    df["ticker"] = ticker_symbol
    return df.reset_index()

# def get_yfinance_fundamentals(ticker_symbol: str):
#     """Fetches income statement, balance sheet, and cash flow data from yfinance."""
#     ticker = yf.Ticker(ticker_symbol)
#     return {
#         "income_statement": ticker.financials,
#         "balance_sheet": ticker.balance_sheet,
#         "cash_flow": ticker.cashflow
#     }
def get_yfinance_recommendations_df(ticker_symbol: str): #runs 
    """Returns analyst recommendations as a DataFrame."""
    import yfinance as yf
    ticker = yf.Ticker(ticker_symbol)
    return ticker.recommendations

def get_yfinance_target_price(ticker_symbol: str): #runs 
    """Returns the target mean price as a float (or None)."""
    import yfinance as yf
    ticker = yf.Ticker(ticker_symbol)
    return ticker.info.get("targetMeanPrice")

# def get_yfinance_analyst_insights(ticker_symbol: str):
#     """Returns recommendations and target price as two DataFrames."""
#     import yfinance as yf
#     import pandas as pd

#     ticker = yf.Ticker(ticker_symbol)

#     recs_df = ticker.recommendations
#     target_price = ticker.info.get("targetMeanPrice")

#     # Wrap scalar in DataFrame
#     target_df = pd.DataFrame([{
#         "ticker": ticker_symbol,
#         "target_mean_price": target_price
#     }])

#     return recs_df, target_df

# def get_yfinance_analyst_insights(ticker_symbol: str): #don't know if this returns a df 
#     """Fetches analyst recommendations and target price from yfinance."""
#     ticker = yf.Ticker(ticker_symbol)
#     return {
#         "recommendations": ticker.recommendations,
#         "target_mean_price": ticker.info.get("targetMeanPrice")
#     }
# price = get_yahoo_price("AAPL")
# print(f"AAPL live price: ${price:.2f}")
'''
#don't know if I need the following 
# def get_last_scraped(ticker_symbol: str):
#     """Fetches the last scraped date from the database."""
#     return get_last_scraped_date(ticker_symbol)

# def update_scrape_date(ticker_symbol: str, date_str: str):
#     """Updates the last scraped date in the database."""
#     update_last_scraped_date(ticker_symbol, date_str)

# def store_data_to_db(data, table_name: str):
#     """Stores processed data to a specific table in the database."""
#     store_to_db(data, table_name)

# def get_default_start():
#     """Returns the default scraping start date."""
#     return get_default_start_date()

'''
#finnacial statemtns 
income_statement = ticker.financials
balance_sheet = ticker.balance_sheet
cash_flow = ticker.cashflow
#analyst insights
recommendations = ticker.recommendations
target_mean_price = ticker.info.get('targetMeanPrice')

price = stock_info.get_live_price("AAPL")
data=stock_info.get_data(ticker, start_date = None, end_date = None, index_as_date = True)
options_data=options.get_options_chain("AAPL")

#amazon_weekly= stock_info.get_data("amzn", start_date="12/04/2009", end_date="12/04/2019", index_as_date = True, interval="1wk") # start date - retrive it from db function, end date, interval depends on the scraping - put a dictionary 
#print(amazon_weekly)

#ticker = yf.Ticker("AAPL")

# Income Statement
#income_statement = ticker.financials
#print(income_statement)

# Balance Sheet
#balance_sheet = ticker.balance_sheet
#print(balance_sheet)

# Cash Flow
#cash_flow = ticker.cashflow
#print(cash_flow)

#income_statement = stock_info.get_income_statement("AAPL") #out of index error 
#print(income_statement)

#balance_sheet = stock_info.get_balance_sheet("AAPL") # out of index error 
#print(balance_sheet)

#cash_flow = stock_info.get_cash_flow("AAPL") #out of range 
#print(cash_flow)

#analysts_info = stock_info.get_analysts_info("AAPL") #didn't work 
#print(analysts_info) #yfinance 


earnings_history = stock_info.get_earnings_history("AAPL") #out of range 
print(earnings_history)

#options_chain = options.get_options_chain("AAPL") #ran 
#print(options_chain)
##print(options_chain["calls"])  # DataFrame of call options
##print(options_chain["puts"])   # DataFrame of put options

#gainers = stock_info.get_day_gainers() #didn't run 
#print(gainers)

#losers = stock_info.get_day_losers() #same error as above 
#print(losers)

#most_active = stock_info.get_day_most_active()#same error as above 
#print(most_active)
'''