'''(runs at market close or shortly after)

custom_get_data(..., interval="1d")

get_day_gainers()

get_day_losers()

get_day_most_active()

get_options_chain(ticker) (daily change in near-term options data)
#yahoo fin data 
# '''
from yahoo_fin import stock_info, news, options #don't need this \
from ticker_loader import get_tradable_tickers
from my_scrapers.sec import get_sec_filings_incremental 
from db import get_last_scraped_date, update_last_scraped_date, store_to_db #yep, need to import get_last_date
from utils import get_default_start_date
from ticker_loader import get_tradable_tickers
import yfinance as yf
from datetime import date
import pandas as pd
'''
def run():
    tickers = get_tradable_tickers()  # optional filter + limit
    for ticker in tickers:
        try:
            # Income Statement
            income_statement = ticker.financials
        except Exception as e:
            print(f"[ERROR] Failed for {ticker}: {e}")
    
    print("[YEARLY JOB] Completed.")
'''

####v2
from my_scrapers.yahoo_func import get_yahoo_historical_data  # make sure it's exposed there


def run():
    tickers = get_tradable_tickers()
    frequency = "daily"
    today = date.today().isoformat()

    for ticker in tickers:
        try:
            ### ---------------- HISTORICAL DATA ---------------- ###
            last_scraped = get_last_scraped_date(ticker, source="historical_prices", frequency=frequency)

            if last_scraped == today:
                print(f"⏭️ {ticker}: Historical data already scraped today.")
                continue

            if last_scraped is None:
                print(f"🆕 First time scraping {ticker} — using default start date")
                last_scraped = get_default_start_date(frequency)

            hist_df = get_yahoo_historical_data(
                ticker_symbol=ticker,
                start_date=last_scraped,
                end_date=today,
                index_as_date=True
            )

            if hist_df is not None and not hist_df.empty:
                hist_df = hist_df.reset_index()
                hist_df["ticker"] = ticker
                hist_df["scraped_date"] = today

                store_to_db(hist_df, table_name="historical_prices")
                update_last_scraped_date(ticker, today, source="historical_prices", frequency=frequency)
                print(f"📈 {ticker}: Stored {len(hist_df)} daily price rows.")
            else:
                print(f"📉 {ticker}: No new historical data.")

        except Exception as e:
            print(f"❌ {ticker}: Error fetching historical data: {e}")

    print("[DAILY JOB] Completed.")

if __name__ == "__main__":
    run()