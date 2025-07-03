'''(useful during trading hours, e.g., 9:30 AM – 4:00 PM EST)

api.get_bars("AAPL", TimeFrame.Hour, ...) – loop over 8000 stocks if needed #alpaca 

get_last_trade(symbol) # alpaca 

get_last_quote(symbol)''' #alpaca

from my_scrapers.alpaca import get_latest_trade_df, get_last_quote_df, get_barset
from ticker_loader import get_tradable_tickers  # optional if you fetch tickers here
from datetime import datetime
import pandas as pd

def run_hourly():
    symbols = get_tradable_tickers()  #this looks similar to what I'm using in main, is there an overlap?

    all_trades = []
    all_quotes = []
    all_bars = []

    for symbol in symbols: #is a for loop the best way to go about this? I have 11000 stocks 
        try:
            trade_df = get_latest_trade_df(symbol)
            quote_df = get_last_quote_df(symbol)
            bar_df = get_barset(symbol, timeframe="1h", limit=1)

            all_trades.append(trade_df)
            all_quotes.append(quote_df)
            all_bars.append(bar_df)

        except Exception as e:
            print(f"[ERROR] Failed for {symbol}: {e}")

    # Combine and export or store to DB
    trades_df = pd.concat(all_trades, ignore_index=True)
    quotes_df = pd.concat(all_quotes, ignore_index=True)
    bars_df = pd.concat(all_bars, ignore_index=True)

    print("Trades:\n", trades_df)
    print("Quotes:\n", quotes_df)
    print("Bars:\n", bars_df)

    # TODO: store to SQL with to_sql() - get last scraped data, udpate last scraped data, store to db
    # 
    #do I need to return anything?

################################################
#v2: april 28th 

from my_scrapers.alpaca import get_trades_incremental, get_quotes_incremental, get_bars_incremental #get_latest_trade_df, get_last_quote_df, get_barset
from db import get_last_scraped_date, update_last_scraped_date, store_to_db
from ticker_loader import get_tradable_tickers
from datetime import datetime, timedelta
import pandas as pd

def run_hourly_scraper():
    symbols = get_tradable_tickers()
    frequency = "hourly"

    all_trades = []
    all_quotes = []
    all_bars = []

    for symbol in symbols:
        try:
            # Get last scrape dates per type
            last_trade_scrape = get_last_scraped_date(symbol, "trade", frequency)
            last_quote_scrape = get_last_scraped_date(symbol, "quote", frequency)
            last_bar_scrape = get_last_scraped_date(symbol, "bar", frequency)

            # Fetch incremental updates
            trade_df = get_trades_incremental(symbol, last_trade_scrape)
            quote_df = get_quotes_incremental(symbol, last_quote_scrape)
            bar_df = get_bars_incremental(symbol, last_bar_scrape)

            # Store to lists
            if not trade_df.empty:
                all_trades.append(trade_df)
                update_last_scraped_date(symbol, "trade", frequency, trade_df['t'].max())

            if not quote_df.empty:
                all_quotes.append(quote_df)
                update_last_scraped_date(symbol, "quote", frequency, quote_df['t'].max())

            if not bar_df.empty:
                all_bars.append(bar_df)
                update_last_scraped_date(symbol, "bar", frequency, bar_df.index.max())

        except Exception as e:
            print(f"[ERROR] Failed for {symbol}: {e}")

    # Store to DB
    if all_trades:
        trades_df = pd.concat(all_trades, ignore_index=True)
        store_to_db(trades_df)

    if all_quotes:
        quotes_df = pd.concat(all_quotes, ignore_index=True)
        store_to_db(quotes_df)

    if all_bars:
        bars_df = pd.concat(all_bars, ignore_index=True)
        store_to_db(bars_df)

if __name__ == "__main__":
    run_hourly_scraper()
