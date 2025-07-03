'''
#functions 

'''
#TO DO:
# - update the db functions 
# the correct fomrat :
#get_last_scraped_date(ticker: str, source: str, frequency: str = None)
#update_last_scraped_date(ticker: str, date_str: str, source: str, frequency: str = None)
#store_to_db(summary_df, table_name="analyst_summary")



'''
def get_last_scraped_date(ticker: str, source: str, frequency: str = None):
    # Example: Use a table or config with columns: ticker, source, frequency, last_date
    # Construct key based on optional frequency
    query_key = f"{source}_{frequency}" if frequency else source
    
    # Fetch from DB based on ticker and query_key
    # Example (pseudo-SQL):
    # SELECT last_scraped FROM scrape_log WHERE ticker=? AND key=?
    ...
def update_last_scraped_date(ticker: str, date_str: str, source: str, frequency: str = None):
    query_key = f"{source}_{frequency}" if frequency else source

    # Example (pseudo-SQL):
    # INSERT INTO scrape_log (ticker, key, last_scraped) VALUES (?, ?, ?)
    # ON CONFLICT(ticker, key) DO UPDATE SET last_scraped=?
    ...

'''
#db function formats 
# get_last_scraped_date(ticker: str, source: str)
#update_last_scraped_date(ticker: str, date_str: str, source: str)
#store_do_db: store_to_db(payload, table_name="fundamentals")

from my_scrapers.yahoo_func import (
    get_yahoo_price,
    get_yfinance_fundamentals,
)
#from yahoo_fin import stock_info #don't need because I'm importing from yahoo_func
#from my_scrapers import sec
from ticker_loader import get_tradable_tickers
from my_scrapers.sec import get_sec_filings_incremental 
from db import get_last_scraped_date, update_last_scraped_date, store_to_db #yep, need to import get_last_date
from utils import get_default_start_date
from ticker_loader import get_tradable_tickers
from datetime import date

def run():
    tickers = get_tradable_tickers()  # optional filter + limit
    for ticker in tickers:
        try:
            fundamentals = get_yfinance_fundamentals(ticker)
            price = get_yahoo_price(ticker)

            today = date.today().isoformat()

            ### ---------------- FUNDAMENTALS ---------------- ###
            last_fundamental_scrape = get_last_scraped_date(ticker, source="fundamentals") #no need to update func to this: get_last_scraped_date(ticker: str, source: str, frequency: str = None)

            if last_fundamental_scrape != today:
                fundamentals = get_yfinance_fundamentals(ticker)
                price = get_yahoo_price.get_live_price(ticker)

                # Add ticker and scrape date for traceability
                payload = {
                    "ticker": ticker,
                    "scraped_date": today,
                    "price": price,
                    "income_statement": fundamentals["income_statement"].to_dict(),
                    "balance_sheet": fundamentals["balance_sheet"].to_dict(),
                    "cash_flow": fundamentals["cash_flow"].to_dict(),
                }

                store_to_db(payload, table_name="fundamentals") 
                update_last_scraped_date(ticker, today, source="fundamentals")
                print(f"✅ {ticker}: Stored fundamentals and price.") #don I need to print?
            else:
                print(f"⏭️ {ticker}: Fundamentals already scraped today.")

            ### ---------------- SEC FILINGS ---------------- ###
            last_sec_scrape = get_last_scraped_date(ticker, source="sec", frequency="yearly") #updated to update_last_scraped_date(ticker: str, date_str: str, source: str, frequency: str = yearly)

            sec_df = get_sec_filings_incremental(
                ticker=ticker,
                form_type=None,
                frequency="yearly",
                last_scraped_date=last_sec_scrape
            )

            if not sec_df.empty:
                store_to_db(sec_df, table_name="sec_filings")
                latest_date = sec_df['filedAt'].max()
                update_last_scraped_date(ticker, latest_date, source="sec",frequency="yearly")
                print(f"📄 {ticker}: {len(sec_df)} SEC filings stored.")
            else:
                print(f"📄 {ticker}: No new SEC filings.")

            print("-" * 80)

        except Exception as e:
            print(f"❌ {ticker}: Error during scraping: {e}")



'''
        except Exception as e:
            print(f"Error processing {ticker}: {e}")

            income = stock_info.get_income_statement(ticker)
            balance = stock_info.get_balance_sheet(ticker)
            cashflow = stock_info.get_cash_flow(ticker)
            price = stock_info.get_live_price(ticker)

            print(f"{ticker} data retrieved: Price = {price}")
            filings = get_sec_filings_incremental(ticker, form_type="10-k", frequency="yearly", last_scraped_date=None) #is this good here? 
            #since last_scraped_data is None, I need to store all the data that gets there 

            #TO DO: add the resutls to the db using store_to_db
            #TO DOL update the laste scraped date with update_last_scraped_date 
            #look at weekly for inspo

        except Exception as e:
            print(f"[ERROR] Failed for {ticker}: {e}")
    
    print("[YEARLY JOB] Completed.")
'''
