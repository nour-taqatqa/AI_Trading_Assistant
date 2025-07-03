#Optional: custom_get_data(..., interval="1mo") for macro views #not a function in any of the 3 scrapers
'''
SEC Form 4 filings (insider trades) – high activity in some months #sec 

Batch get_options_chain(ticker) – useful for long-dated options #yahoo_fin
'''

#form_type= '4'

#df = get_sec_filings_incremental(ticker, form_type, frequency, last_scraped)

from db import get_last_scraped_date, update_last_scraped_date, store_to_db
from utils import get_default_start_date
from ticker_loader import get_tradable_tickers
from my_scrapers.yahoo_func import get_yahoo_options_data
from my_scrapers.sec import get_sec_filings_incremental
from datetime import date
import pandas as pd


#v2
'''
def run_scraper(ticker, form_type, frequency):
    last_scraped = get_last_scraped_date(ticker, form_type, frequency)
    df = get_sec_filings_incremental(ticker, form_type, frequency, last_scraped)

    if not df.empty:
        store_to_db(df)
        update_last_scraped_date(ticker, form_type, frequency, df["filedAt"].max())
    else:
        print(f"No new filings to store for {ticker} - {form_type}.")


def run_monthly_scraper():
    tickers = get_tradable_tickers()
    form_types = ["4"]  # Form 4 is insider trading, generally collected monthly
    frequency = "monthly"

    for ticker in tickers:
        for form_type in form_types:
            run_scraper(ticker, form_type, frequency)


if __name__ == "__main__": ## should I include this in other scripts?
    # Example of running monthly or quarterly scraper

    run_monthly_scraper()

#v3
def run_scraper(ticker, form_type, frequency): #I could put this function in util and use it in all scrapers
    last_scraped = get_last_scraped_date(ticker, source=form_type, frequency=frequency)
    df = get_sec_filings_incremental(
        ticker=ticker,
        form_type=form_type,
        frequency=frequency,
        last_scraped_date=last_scraped
    )

    if not df.empty:
        store_to_db(df, table_name="sec_filings")
        update_last_scraped_date(ticker, df["filedAt"].max(), source=form_type, frequency=frequency)
        print(f"✅ {ticker}: Stored {len(df)} {form_type} filings.")
    else:
        print(f"⏭️ {ticker}: No new {form_type} filings.")


def run_monthly_scraper():
    tickers = get_tradable_tickers()
    form_types = ["4"]  # Form 4 = Insider trading
    frequency = "monthly"
    today = date.today().isoformat()

    for ticker in tickers:
        for form_type in form_types:
            run_scraper(ticker, form_type, frequency)

        ### 📊 Yahoo Options Data
        try:
            last_option_scraped = get_last_scraped_date(ticker, source="options_data", frequency=frequency)
            if last_option_scraped != today:
                options_data = get_yahoo_options_data(ticker)
                calls_df = pd.DataFrame(options_data.get("calls", []))
                puts_df = pd.DataFrame(options_data.get("puts", []))

                for df, label in [(calls_df, "calls"), (puts_df, "puts")]:
                    if not df.empty:
                        df["ticker"] = ticker
                        df["scraped_date"] = today
                        df["option_type"] = label
                        store_to_db(df, table_name="options_data")
                        print(f"📈 {ticker}: Stored {len(df)} {label} options.")

                update_last_scraped_date(ticker, today, source="options_data", frequency=frequency)
            else:
                print(f"⏭️ {ticker}: Options data already scraped today.")
        except Exception as e:
            print(f"[Options Data Error] {ticker}: {e}")

        print("-" * 80)


if __name__ == "__main__":
    run_monthly_scraper()
'''
#v4
def run():
    tickers = get_tradable_tickers()
    frequency = "monthly"
    today = date.today().isoformat()

    for ticker in tickers:
        try:
            ### ---------------- SEC FORM 4 ---------------- ###
            last_sec_scrape = get_last_scraped_date(ticker, source="4", frequency=frequency)

            sec_df = get_sec_filings_incremental(
                ticker=ticker,
                form_type="4",
                frequency=frequency,
                last_scraped_date=last_sec_scrape
            )

            if not sec_df.empty:
                store_to_db(sec_df, table_name="sec_filings")
                latest_date = sec_df['filedAt'].max()
                update_last_scraped_date(ticker, latest_date, source="4", frequency=frequency)
                print(f"📄 {ticker}: {len(sec_df)} Form 4 filings stored.")
            else:
                print(f"📄 {ticker}: No new Form 4 filings.")

            ### ---------------- OPTIONS DATA ---------------- ###
            last_options_scrape = get_last_scraped_date(ticker, source="options_data", frequency=frequency)

            if last_options_scrape != today: #this s
                options_data = get_yahoo_options_data(ticker)
                calls_df = pd.DataFrame(options_data.get("calls", []))
                puts_df = pd.DataFrame(options_data.get("puts", []))

                for df, label in [(calls_df, "calls"), (puts_df, "puts")]:
                    if not df.empty:
                        df["ticker"] = ticker
                        df["scraped_date"] = today
                        df["option_type"] = label
                        store_to_db(df, table_name="options_data")
                        print(f"📈 {ticker}: {len(df)} {label} options stored.")

                update_last_scraped_date(ticker, today, source="options_data", frequency=frequency)
            else:
                print(f"⏭️ {ticker}: Options data already scraped today.")

            print("-" * 80)

        except Exception as e:
            print(f"❌ {ticker}: Error during monthly scraping: {e}")


if __name__ == "__main__":
    run()
