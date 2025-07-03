'''
get_analysts_info(ticker) – typically changes weekly or biweekly

SEC 8-K reports – moderate frequency (avg ~1/week/ticker depending on news)'''

#call sec filings -- done 
#need to itilize last_scraped_date from somewhere - it's in my schedler - don't know if it needs to be 
#here or not  -- done 
#call tradable_tickers and loop through all tickers - done

from my_scrapers.sec import get_sec_filings_incremental 
from db import get_last_scraped_date, update_last_scraped_date, store_to_db #yep, need to import get_last_date
from utils import get_default_start_date
from ticker_loader import get_tradable_tickers
import yfinance as yf
import pandas as pd

#I rewrote this function in yahoo_func -- take note of how I'm returing a df here, I'm not in yahoo_func
# def get_analyst_info_df(ticker, last_scraped_date=None): #yfinance
#     """
#     Retrieves incremental analyst data from yfinance.
#     Includes recommendation trends + target prices.
#     Filters recommendations if last_scraped_date is provided.
#     """
#     ticker_obj = yf.Ticker(ticker)

#     # Recommendation history
#     recommendations = ticker_obj.recommendations

#     if recommendations is not None:
#         recommendations["symbol"] = ticker
#         if last_scraped_date is not None:
#             recommendations = recommendations[recommendations.index > pd.to_datetime(last_scraped_date)]

#     # Summary info (target prices, recommendation key, etc.)
#     info = ticker_obj.info
#     summary = {
#         "symbol": ticker,
#         "targetMeanPrice": info.get("targetMeanPrice"),
#         "targetLowPrice": info.get("targetLowPrice"),
#         "targetHighPrice": info.get("targetHighPrice"),
#         "recommendationKey": info.get("recommendationKey"),
#         "numberOfAnalystOpinions": info.get("numberOfAnalystOpinions")
#     }
#     summary_df = pd.DataFrame([summary])

#     return recommendations, summary_df


def run_weekly_scraper(ticker, form_type): #do I need to 
#    symbols = get_tradable_tickers()
    frequency = "weekly"
    form_type ="8-k" #8-k is the weekly form type
#    for symbol in symbols: #is a for loop the best way to go about this? I have 11000 stocks 
#        try:
    last_scraped = get_last_scraped_date(ticker, form_type, frequency)
    '''
            if last_scraped is None: ##can delete this becuase get_sec_finsling deal with it 
                print("First time scrape — using default start date")
                last_scraped = get_default_start_date(frequency)
'''
    df = get_sec_filings_incremental(ticker, form_type, frequency, last_scraped)

    if not df.empty:
        store_to_db(df)
        update_last_scraped_date(ticker, form_type, frequency, df["filedAt"].max())
    else:
        print("No new filings to store.")
        #except:
        #   pass #do I need to write anything here 

tickers = get_tradable_tickers()
#form_types =["10-k", "8-k", ] only looking at 8-k in weekly
form_type ="8-k"
for ticker in tickers:
#    for form_type in form_types:
    run_weekly_scraper(ticker, form_type)

    #TO DO:
        #add a __main__?
######################################################################
#v2

from my_scrapers.sec import get_sec_filings_incremental 
from db import get_last_scraped_date, update_last_scraped_date, store_to_db
from utils import get_default_start_date
from ticker_loader import get_tradable_tickers
import yfinance as yf
import pandas as pd

# def get_analyst_info_df(ticker, last_scraped_date=None):
#     ticker_obj = yf.Ticker(ticker)
    
#     # Recommendation history
#     recommendations = ticker_obj.recommendations
#     if recommendations is not None:
#         recommendations["symbol"] = ticker
#         if last_scraped_date is not None:
#             recommendations = recommendations[recommendations.index > pd.to_datetime(last_scraped_date)]

#     # Summary info
#     info = ticker_obj.info
#     summary = {
#         "symbol": ticker,
#         "targetMeanPrice": info.get("targetMeanPrice"),
#         "targetLowPrice": info.get("targetLowPrice"),
#         "targetHighPrice": info.get("targetHighPrice"),
#         "recommendationKey": info.get("recommendationKey"),
#         "numberOfAnalystOpinions": info.get("numberOfAnalystOpinions")
#     }
#     summary_df = pd.DataFrame([summary])

#     return recommendations, summary_df

def run_sec_scraper(ticker, form_type="8-k"):
    frequency = "weekly"
    last_scraped = get_last_scraped_date(ticker, form_type, frequency)
    df = get_sec_filings_incremental(ticker, form_type, frequency, last_scraped)

    if not df.empty:
        store_to_db(df)
        update_last_scraped_date(ticker, form_type, frequency, df["filedAt"].max())
    else:
        print(f"No new SEC filings to store for {ticker}.")

def run_analyst_scraper(ticker):
    frequency = "weekly"
    try:
        last_scraped = get_last_scraped_date(ticker, "analyst_info", frequency)
        recommendations_df, summary_df = get_analyst_info_df(ticker, last_scraped)

        if recommendations_df is not None and not recommendations_df.empty:
            store_to_db(recommendations_df)
            update_last_scraped_date(ticker, "analyst_info", frequency, recommendations_df.index.max())

        if not summary_df.empty:
            store_to_db(summary_df)

    except Exception as e:
        print(f"[Analyst Info Error] {ticker}: {e}")

if __name__ == "__main__":
    tickers = get_tradable_tickers()
    
    # Run SEC scraper
    for ticker in tickers:
        run_sec_scraper(ticker, form_type="8-k")

    # Run Analyst Info scraper
    for ticker in tickers:
        run_analyst_scraper(ticker)
################################################
#v3  
#correct db function fomrats should be included here 

"""
get_last_scraped_date(ticker, source="8-k", frequency="weekly")
update_last_scraped_date(ticker, date_str, source="8-k", frequency="weekly")
"""
from my_scrapers.sec import get_sec_filings_incremental
from my_scrapers.yahoo_func import get_yfinance_analyst_insights
from db import get_last_scraped_date, update_last_scraped_date, store_to_db
from utils import get_default_start_date
from ticker_loader import get_tradable_tickers
import yfinance as yf
import pandas as pd
from datetime import date

def run_weekly_scraper(ticker: str):
    frequency = "weekly"
    today = date.today().isoformat()

    ### ---------------- SEC FILINGS ---------------- ###
    try:
        last_sec_scraped = get_last_scraped_date(ticker, source="8-k", frequency=frequency)
        sec_df = get_sec_filings_incremental(ticker, form_type="8-k", frequency=frequency, last_scraped_date=last_sec_scraped)

        if not sec_df.empty:
            store_to_db(sec_df, table_name="sec_filings")
            update_last_scraped_date(ticker, sec_df["filedAt"].max(), source="8-k", frequency=frequency)
            print(f"✅ {ticker}: Stored {len(sec_df)} 8-K SEC filings.")
        else:
            print(f"⏭️ {ticker}: No new 8-K filings.")
    except Exception as e:
        print(f"[SEC Error] {ticker}: {e}")

    ### ---------------- ANALYST INSIGHTS ---------------- ###
    try:
        last_analyst_scraped = get_last_scraped_date(ticker, source="analyst_info", frequency=frequency)

        # Only scrape again if not scraped today
        if last_analyst_scraped != today:
            insights = get_yfinance_analyst_insights(ticker) 

            # Handle recommendations (as DataFrame) and target price (scalar)
            recs = insights["recommendations"] #I don't know if this is correct 
            target = insights["target_mean_price"]

            if recs is not None and not recs.empty:
                recs["ticker"] = ticker
                store_to_db(recs, table_name="analyst_recommendations")
                update_last_scraped_date(ticker, today, source="analyst_info", frequency=frequency)
                print(f"📈 {ticker}: Stored {len(recs)} analyst recommendations.")
            else:
                print(f"⏭️ {ticker}: No new analyst recommendations.")

            if target is not None:
                summary_df = pd.DataFrame([{
                    "ticker": ticker,
                    "target_mean_price": target,
                    "scraped_date": today
                }])
                store_to_db(summary_df, table_name="analyst_summary")
                print(f"📊 {ticker}: Stored target mean price.")

        else:
            print(f"⏭️ {ticker}: Analyst info already scraped today.")
    except Exception as e:
        print(f"[Analyst Info Error] {ticker}: {e}")

    print("-" * 80)


if __name__ == "__main__":
    tickers = get_tradable_tickers()

    for ticker in tickers:
        run_weekly_scraper(ticker)