"""
(about every 3 months, matching earnings cycles)

get_income_statement(ticker, yearly=False)- changed it - yfinance 

get_balance_sheet(ticker, yearly=False)- changed it - yfinance 

get_cash_flow(ticker, yearly=False) - changed it - yfinance 

get_earnings_history(ticker)-----skipped 

SEC Form 10-Q #and other earnings-related filings - done 
"""

from my_scrapers.sec import get_sec_filings_incremental
from db import get_last_scraped_date, update_last_scraped_date, store_to_db
from utils import get_default_start_date # I don't use this anywhere 
from ticker_loader import get_tradable_tickers

def run_scraper(ticker, form_type, frequency):
    last_scraped = get_last_scraped_date(ticker, form_type, frequency)
    #get a last scraped date for the cash flow, earnings etc 
    df = get_sec_filings_incremental(ticker, form_type, frequency, last_scraped)

    if not df.empty:
        store_to_db(df)
        update_last_scraped_date(ticker, form_type, frequency, df["filedAt"].max())
    else:
        print(f"No new filings to store for {ticker} - {form_type}.")
    import yfinance as yf

    ticker = yf.Ticker("AAPL")

    # Quarterly income statement
    income_q = ticker.quarterly_financials
    print("Quarterly Income Statement:\n", income_q)

    # Quarterly balance sheet
    balance_q = ticker.quarterly_balance_sheet
    print("Quarterly Balance Sheet:\n", balance_q)

    # Quarterly cash flow
    cashflow_q = ticker.quarterly_cashflow
    print("Quarterly Cash Flow:\n", cashflow_q)


def run_quarterly_scraper():
    tickers = get_tradable_tickers()
    form_type= '10-Q'
    frequency = "quarterly"

    for ticker in tickers:
        run_scraper(ticker, form_type, frequency)

if __name__ == "__main__":
    # Example of running monthly or quarterly scraper
    run_quarterly_scraper()