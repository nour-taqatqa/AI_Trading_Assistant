# my_scrapers/alpaca.py
#downloaded the new alpaca-py instead of the alpaca_trade_api - rewrote functions 
import os
from dotenv import load_dotenv
#import alpaca_trade_api as tradeapi - removed this as it's depreciated 
from alpaca.data.historical import StockHistoricalDataClient #to import get_stock_bars
from alpaca.data.requests import StockBarsRequest #to import StockBarsRequest to set up the request params
from alpaca.data.timeframe import TimeFrame
from datetime import datetime,timedelta
from alpaca.data.live import StockDataStream #function 2 - didn't use 
from alpaca.data.requests import StockLatestTradeRequest #function 2 - didn't use 
import requests #function 2,3 
import pandas as pd #function 2,3
from alpaca.trading.client import TradingClient #function 5



load_dotenv() #Loads environment variables from a .env file into your Python process (i.e., into os.environ).

# Create a single REST API client instance to reuse
#api = tradeapi.REST( #I might comment this out 
#    os.getenv("ALPACA_API_KEY"),
#    os.getenv("ALPACA_SECRET_KEY"),
#    base_url=os.getenv("ALPACA_BASE_URL"),
#    api_version="v2"
#)
market_client = StockHistoricalDataClient( #starting from here, used for functions 1 and 2
    os.getenv("ALPACA_API_KEY"),
    os.getenv("ALPACA_SECRET_KEY")
)
trading_client = TradingClient(
    os.getenv("ALPACA_API_KEY"),
    os.getenv("ALPACA_SECRET_KEY")
)

headers = { #defining it globally for better repetitive usage
        "APCA-API-KEY-ID": os.getenv("ALPACA_API_KEY"),
        "APCA-API-SECRET-KEY": os.getenv("ALPACA_SECRET_KEY")
    }
#def get_barset(symbols, timeframe="day", limit=100): #can call for a 10 year period and for as many stocks as I want 
#    return api.get_bars(symbols, timeframe, limit=limit) #will go into hourly data 
'''
def get_barset(symbols, timeframe="1h", limit=None, start=None, end=None) -> pd.DataFrame: #hourly
    """
    Fetch recent OHLCV bars (hourly) for one or more symbols.
    By default, fetches the previous full hour.
    Works great if your script runs during trading hours (e.g., 9:30am–4pm ET).
    Will return empty data if run after hours, like at night or early morning

    Returns:
        A pandas DataFrame containing OHLCV data with the following columns:
            - 'open': Opening price of the interval
            - 'high': Highest price in the interval
            - 'low': Lowest price in the interval
            - 'close': Closing price of the interval
            - 'volume': Volume traded during the interval
            - 'timestamp': Start time of each bar
            - 'symbol': Stock symbol (present if multiple symbols requested)

    """
    # Dynamically set time range for previous full hour if none given
    if not start and not limit:
        now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        end = now
        start = now - timedelta(hours=1)
    
    request_params = StockBarsRequest(
    symbol_or_symbols=symbols,  # or a list like ["AAPL", "MSFT"]
    timeframe=timeframe,
    limit=limit,                      
    start=start,
    end=end
)
    bars = market_client.get_stock_bars(request_params).df

    return bars
'''

def get_barset_new(symbols, timeframe="day", limit=100)-> pd.DataFrame: #scrapes for last 3 years 
    """
    Fetch historical OHLCV bars for one or more symbols.
    """
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockBarsRequest
    from alpaca.trading.client import TradingClient
    from alpaca.data.timeframe import TimeFrame 
    from datetime import datetime, timedelta
    import pandas as pd
    import requests
    request_params = StockBarsRequest(
    symbol_or_symbols=symbols,  # or a list like ["AAPL", "MSFT"]
    timeframe=TimeFrame.Day,
    limit=None,
    start=datetime(2022, 1, 1),
    end=datetime(2025, 5, 1)
    )


    bars = market_client.get_stock_bars(request_params).df
    bars=bars.reset_index()

    return bars
#def get_last_trade(symbol): #doesn't work out anymore - depreciated 
#    return api.get_last_trade(symbol)
def get_latest_trade_df(symbol: str) -> pd.DataFrame: #hourly #can only accept a single stock #runs - can only return one trade at a time
    """
    Fetches the latest trade information for a single stock symbol using the Alpaca v2 Market Data API
    and returns the result as a one-row pandas DataFrame suitable for hourly scraping and database insertion.
    
    Returns:
        A one-row DataFrame containing the most recent trade data with the following columns:

        - 'p' : float — Trade price
        - 's' : int — Trade size (number of shares)
        - 't' : str — ISO-formatted timestamp of the trade (UTC)
        - 'x' : str — Exchange code where the trade occurred (e.g., "Q" = NASDAQ)
        - 'i' : str — Trade ID
        - 'z' : str — Tape identifier (A/B/C = different SIPs for reporting)
        - 'symbol' : str — The stock symbol provided to the function
        - 'retrieved_at' : datetime — The timestamp when the data was pulled (useful for logging/syncing)
    
    """
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockBarsRequest
    from alpaca.trading.client import TradingClient
    from alpaca.data.timeframe import TimeFrame 
    from datetime import datetime, timedelta
    import pandas as pd
    import requests
    url = f"https://data.alpaca.markets/v2/stocks/{symbol}/trades/latest"
    #headers = {
    #    "APCA-API-KEY-ID": os.getenv("ALPACA_API_KEY"),
    #    "APCA-API-SECRET-KEY": os.getenv("ALPACA_SECRET_KEY")
    #}

    response = requests.get(url, headers=headers)
    data = response.json()

    # Flatten & format
    trade_data = data.get("trade", {})
    trade_data["symbol"] = symbol
    trade_data["retrieved_at"] = datetime.utcnow()

    df = pd.DataFrame([trade_data])  # single row
    df["c"] = df["c"].apply(lambda x: x if isinstance(x, list) else [x] if pd.notna(x) else [])

    return df

#def get_last_quote(symbol): #depreciated and needs to be changed
#    return api.get_last_quote(symbol)

def get_last_quote_df(symbol: str)-> pd.DataFrame: #hourly - works on one trade only, returns 
    """
    Fetches the latest quote data for a given stock symbol from the Alpaca Market Data API.

    Returns:
        A single-row pandas DataFrame containing the latest quote information, with the following columns:

        - 'ap': Ask price — the lowest price a seller is willing to accept
        - 'bp': Bid price — the highest price a buyer is willing to pay
        - 'as': Ask size — number of shares available at the ask price
        - 'bs': Bid size — number of shares available at the bid price
        - 't': Timestamp (ISO format) of when the quote was recorded
        - 'symbol': The ticker symbol used in the request
        - 'retrieved_at': The UTC datetime when the API response was received (used for logging/ETL)

    """
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockBarsRequest
    from alpaca.trading.client import TradingClient
    from alpaca.data.timeframe import TimeFrame 
    from datetime import datetime, timedelta
    import pandas as pd
    import requests
    url = f"https://data.alpaca.markets/v2/stocks/{symbol}/quotes/latest"

    #headers = {
    #    "APCA-API-KEY-ID": os.getenv("ALPACA_API_KEY"),
    #    "APCA-API-SECRET-KEY": os.getenv("ALPACA_SECRET_KEY")
    #}
    response = requests.get(url, headers=headers)
    data = response.json().get("quote", {})
    data["symbol"] = symbol
    data["retrieved_at"] = datetime.utcnow()
    df=pd.DataFrame([data])
    #the following line tackles special charecters like [] in col c 
    df["c"] = df["c"].apply(lambda x: x if isinstance(x, list) else [x] if pd.notna(x) else [])


    return df

"""
def submit_order(symbol, qty, side, type="market", time_in_force="gtc"): #this places orders, I skipped it 
    return api.submit_order(
        symbol=symbol,
        qty=qty,
        side=side,
        type=type,
        time_in_force=time_in_force
    )
""" 

#def get_account(): #depreciated, see updated versio nbelow 
#    return api.get_account()
'''
def get_account():
    """
    Retrieves account information for the authenticated Alpaca user using the Alpaca-py TradingClient.

    Returns:
    -------
    Account
        An object representing the current Alpaca trading account. Includes fields such as:

        - id : str — Unique account identifier
        - status : str — Account status (e.g., "ACTIVE")
        - currency : str — Currency of the account (usually "USD")
        - cash : float — Available cash balance
        - buying_power : float — Buying power available for new positions
        - portfolio_value : float — Total portfolio value including open positions
        - equity : float — Current equity in the account
        - last_equity : float — Previous day’s equity value
        - created_at : datetime — When the account was created
        - pattern_day_trader : bool — Whether the account is flagged as a PDT

    """
    return trading_client.get_account()
'''
"""
i can put get_account in a df:
def get_account_df():
    account = trading_client.get_account()
    data = {
        "id": account.id,
        "status": account.status,
        "currency": account.currency,
        "cash": float(account.cash),
        "buying_power": float(account.buying_power),
        "equity": float(account.equity),
        "portfolio_value": float(account.portfolio_value),
        "pattern_day_trader": account.pattern_day_trader,
        "created_at": account.created_at,
        "retrieved_at": datetime.utcnow()
    }
    return pd.DataFrame([data])

"""

#def list_positions(): #depreciated - won't use becasue it's api account specific not market specific
#    return api.list_positions()

#def list_orders(status="all"): #depreciated - won't use becasue it's api account specific not market specific
#    return api.list_orders(status=status)
'''
from alpaca.data.requests import StockSnapshotRequest

def get_stock_snapshots(symbols):#I don't think I'll use it but it's here 
    """
    Retrieves real-time snapshot data for a list of stock symbols.

    Parameters
    ----------
    symbols : list of str
        List of stock ticker symbols (e.g., ["AAPL", "MSFT", "TSLA"])

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the latest trade, quote, daily and previous day bars per symbol.
    """
    request = StockSnapshotRequest(symbol_or_symbols=symbols)
    snapshots = market_client.get_stock_snapshots(request)

    all_data = []
    for symbol, snapshot in snapshots.items():
        row = {
            "symbol": symbol,
            "retrieved_at": datetime.utcnow(),

            # Last Trade
            "trade_price": getattr(snapshot.latest_trade, "price", None),
            "trade_size": getattr(snapshot.latest_trade, "size", None),
            "trade_timestamp": getattr(snapshot.latest_trade, "timestamp", None),

            # Last Quote
            "ask_price": getattr(snapshot.latest_quote, "ask_price", None),
            "bid_price": getattr(snapshot.latest_quote, "bid_price", None),

            # Daily Bar
            "open": getattr(snapshot.daily_bar, "open", None),
            "high": getattr(snapshot.daily_bar, "high", None),
            "low": getattr(snapshot.daily_bar, "low", None),
            "close": getattr(snapshot.daily_bar, "close", None),
            "volume": getattr(snapshot.daily_bar, "volume", None)
        }
        all_data.append(row)

    return pd.DataFrame(all_data)
'''
##########################
#v2 - only 3 out of 5 functions above 
'''
from my_scrapers.alpaca import get_latest_trade_df, get_last_quote_df, get_barset
from db import get_last_scraped_date, update_last_scraped_date, store_to_db
from ticker_loader import get_tradable_tickers
from datetime import datetime, timedelta
import pandas as pd
#couldu se defualt date instead of this repretiive code

def get_trades_incremental(symbol, last_scraped_date):
    now = datetime.utcnow()
    if last_scraped_date is None:
        last_scraped_date = now - timedelta(hours=1)  # default to 1 hour ago if none

    trade_df = get_latest_trade_df(symbol)
    trade_time = pd.to_datetime(trade_df['t'].iloc[0])

    if trade_time > pd.to_datetime(last_scraped_date):
        return trade_df
    else:
        return pd.DataFrame()

def get_quotes_incremental(symbol, last_scraped_date):
    now = datetime.utcnow()
    if last_scraped_date is None:
        last_scraped_date = now - timedelta(hours=1)

    quote_df = get_last_quote_df(symbol)
    quote_time = pd.to_datetime(quote_df['t'].iloc[0])

    if quote_time > pd.to_datetime(last_scraped_date):
        return quote_df
    else:
        return pd.DataFrame()

def get_bars_incremental(symbol, last_scraped_date):
    now = datetime.utcnow()
    if last_scraped_date is None:
        last_scraped_date = now - timedelta(hours=1)

    bar_df = get_barset(symbol, timeframe="1h", start=last_scraped_date, end=now)

    return bar_df
'''