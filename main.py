from fastapi import FastAPI
from db import engine  # assumes you have db.py set up for PostgreSQL connection
import pandas as pd
from my_scrapers.sec import get_sec_filings_df  # your function module
from my_scrapers.yahoo_func import get_yahoo_options_data  # your function module
from my_scrapers.alpaca import (
    get_barset_new,
    get_latest_trade_df,
    get_last_quote_df
)
from ticker_loader import get_tradable_tickers
from dotenv import load_dotenv
load_dotenv()  # <-- loads .env into os.environ immediately -- needed for get tradable tickers?

app = FastAPI()

# simple health check for Kubernetes probes
@app.get("/health")
def health():
    return {"status": "ok"}

# Cache tickers once for reuse
#TICKERS = get_tradable_tickers() #exchange_filter=["NASDAQ", "NYSE"] # ❌ this calls Alpaca immediately, even in the reload watcher - docker won't run
TICKERS: list[str] = []

@app.on_event("startup")
def load_tickers_on_startup():
    import logging
    logging.info("Loading tradable tickers from Alpaca…")
    try:
        globals()["TICKERS"] = get_tradable_tickers()
        logging.info(f"Loaded {len(TICKERS)} tickers.")
    except Exception as e:
        logging.error(f"Failed to load tickers: {e}")
        
@app.get("/scrape-all/{ticker}")
def test_all_scrapers_for_ticker(ticker: str):
    results = {}

    # 1. SEC Filings
    try:
        form_types = [("8-K", "weekly"), ("10-K", "yearly"), ("10-q", "quarterly"), ("4", "monthly")]
        sec_result = []
        for form_type, freq in form_types:
            df = get_sec_filings_df(ticker, form_type=form_type, frequency=freq)
            if not df.empty:
                table = f"sec_{ticker.lower()}_{form_type.lower().replace('-', '')}"
                df.to_sql(table, con=engine, if_exists="append", index=False)
                sec_result.append((form_type, len(df)))
        results["sec"] = sec_result
    except Exception as e:
        results["sec_error"] = str(e)

    # 2. Options Chain
    try:
        calls_df, puts_df = get_yahoo_options_data(ticker)
        if not calls_df.empty:
            calls_df.to_sql(f"{ticker.lower()}_calls", con=engine, if_exists="append", index=False)
        if not puts_df.empty:
            puts_df.to_sql(f"{ticker.lower()}_puts", con=engine, if_exists="append", index=False)
        results["options"] = {
            "calls": len(calls_df),
            "puts": len(puts_df)
        }
    except Exception as e:
        results["options_error"] = str(e)

    # 3. OHLCV Bars
    try:
        bars_df = get_barset_new([ticker])
        if not bars_df.empty:
            bars_df.to_sql(f"{ticker.lower()}_bars", con=engine, if_exists="append", index=False)
            results["bars"] = len(bars_df)
        else:
            results["bars"] = 0
    except Exception as e:
        results["bars_error"] = str(e)

    # 4. Latest Trade
    try:
        trade_df = get_latest_trade_df(ticker)
        if not trade_df.empty:
            trade_df.to_sql(f"{ticker.lower()}_latest_trade", con=engine, if_exists="append", index=False)
            results["latest_trade"] = 1
        else:
            results["latest_trade"] = 0
    except Exception as e:
        results["latest_trade_error"] = str(e)

    # 5. Latest Quote
    try:
        quote_df = get_last_quote_df(ticker)
        if not quote_df.empty:
            quote_df.to_sql(f"{ticker.lower()}_latest_quote", con=engine, if_exists="append", index=False)
            results["latest_quote"] = 1
        else:
            results["latest_quote"] = 0
    except Exception as e:
        results["latest_quote_error"] = str(e)

    return {"ticker": ticker, "results": results}

@app.get("/scrape-sec-all") #this is the title that shows up on web interface
def scrape_all_sec():
    form_types = [
        ("8-k","weekly"),
        ("10-K", "yearly"),
        ("10-q", "quarterly"),
        ("4", "monthly")
    ]

    results = []
    for ticker in TICKERS:
        for form_type, frequency in form_types:
            df = get_sec_filings_df(ticker, form_type=form_type, frequency=frequency)

            if df.empty:
                continue

            #table_name = f"sec_{ticker.lower()}_{form_type.lower().replace('-', '')}"
            table_name = f"sec_{form_type.lower().replace('-', '')}"


            df.to_sql(table_name, con=engine, if_exists="append", index=False)
            results.append({
                "ticker": ticker,
                "form_type": form_type,
                "rows_added": len(df)
            })

    return {"message": "Scraping complete.", "details": results}


@app.get("/scrape-options-all")
def scrape_all_options():
    results = []
    for ticker in TICKERS:
        calls_df, puts_df= get_yahoo_options_data(ticker) 
        # calls_df = pd.DataFrame(chain["calls"])
        # puts_df = pd.DataFrame(chain["puts"])
        if not calls_df.empty:
            calls_df.to_sql("option_calls", con=engine, if_exists="append", index=False) #table name in db is "option_calls" 
        if not puts_df.empty:
            puts_df.to_sql("option_puts", con=engine, if_exists="append", index=False)
        results.append({"ticker": ticker, "calls": len(calls_df), "puts": len(puts_df)}) #this outputs teh result of the retrieval
    return {"message": "Options scraping complete.", "details": results}

@app.get("/scrape-bars-all")
def scrape_all_bars():
    results = []
    for ticker in TICKERS:
        df = get_barset_new([ticker])
        if not df.empty:
            df.to_sql("price_bars", con=engine, if_exists="append", index=False)
            df.reset_index(inplace=True)  # timestamp is likely the index in your DataFrame -- added this, not sure
            results.append({"ticker": ticker, "rows_added": len(df)})
    return {"message": "OHLCV scraping complete.", "details": results}

@app.get("/scrape-trades-all")
def scrape_all_trades():
    results = []
    for ticker in TICKERS:
        df = get_latest_trade_df(ticker)
        if not df.empty:
            df.to_sql("latest_trades", con=engine, if_exists="append", index=False)
            results.append({"ticker": ticker, "rows_added": len(df)})
    return {"message": "Trade scraping complete.", "details": results}

@app.get("/scrape-quotes-all")
def scrape_all_quotes():
    results = []
    for ticker in TICKERS:
        df = get_last_quote_df(ticker)
        if not df.empty:
            df.to_sql("latest_quotes", con=engine, if_exists="append", index=False)
            results.append({"ticker": ticker, "rows_added": len(df)})
    return {"message": "Quote scraping complete.", "details": results}

"""
@app.get("/sec/{ticker}")
def scrape_sec(ticker: str, form_type: str = "10-K", frequency: str = "yearly"):
    df = get_sec_filings_df(ticker, form_type=form_type, frequency=frequency)
    if df.empty:
        return {"message": f"No filings found for {ticker}"}

    table_name = f"sec_{ticker.lower()}_{form_type.lower()}"
    df.to_sql(table_name, con=engine, if_exists="replace", index=False)
    return {"message": f"Saved {len(df)} filings to table '{table_name}'"}

@app.get("/options/{ticker}")
def scrape_options(ticker: str):
    chain = get_yahoo_options_data(ticker)
    calls_df = pd.DataFrame(chain.get("calls", []))
    puts_df = pd.DataFrame(chain.get("puts", []))
    calls_df.to_sql(f"{ticker.lower()}_calls", con=engine, if_exists="replace", index=False)
    puts_df.to_sql(f"{ticker.lower()}_puts", con=engine, if_exists="replace", index=False)
    return {"calls": len(calls_df), "puts": len(puts_df)}

@app.get("/bars/{ticker}")
def scrape_ohlcv(ticker: str):
    df = get_barset_new([ticker])
    df.to_sql(f"{ticker.lower()}_bars", con=engine, if_exists="replace", index=False)
    return {"message": f"Saved {len(df)} OHLCV rows for {ticker}"}

@app.get("/latest_trade/{ticker}")
def scrape_latest_trade(ticker: str):
    df = get_latest_trade_df(ticker)
    df.to_sql(f"{ticker.lower()}_latest_trade", con=engine, if_exists="replace", index=False)
    return df.to_dict(orient="records")[0]

@app.get("/quote/{ticker}")
def scrape_latest_quote(ticker: str):
    df = get_last_quote_df(ticker)
    df.to_sql(f"{ticker.lower()}_latest_quote", con=engine, if_exists="replace", index=False)
    return df.to_dict(orient="records")[0]
'''
'''
from fastapi import FastAPI
from scheduler import schedule_scraping_jobs

app = FastAPI()

@app.on_event("startup")
def startup_event():
    schedule_scraping_jobs()

"""
"""
we’re referring to the moment the FastAPI server is launched, not when someone visits it in a browser.

when the server spins up, it'll kick off your scraping scheduler immediately — even if no one visits the API.
"""

#do I need the following:
"""
from fastapi import FastAPI, BackgroundTasks
from scheduler import schedule_scraping_jobs
from scraper import yahoo, alpaca, sec

app = FastAPI()

# Initialize scheduled scraping jobs
schedule_scraping_jobs()

@app.get("/")
def root():
    return {"message": "Financial Data Scraper API is running."}

@app.get("/scrape/ticker/{ticker}")
def scrape_single_ticker(ticker: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(yahoo.scrape_all_yahoo, ticker)
    background_tasks.add_task(alpaca.scrape_all_alpaca, ticker)
    background_tasks.add_task(sec.scrape_all_sec, ticker)
    return {"message": f"Scraping initiated for {ticker}"}

@app.get("/scrape/all")
def scrape_all(background_tasks: BackgroundTasks):
    # This could also be paginated or triggered in batches.
    tickers = yahoo.get_all_tickers()
    for ticker in tickers:
        background_tasks.add_task(yahoo.scrape_all_yahoo, ticker)
        background_tasks.add_task(alpaca.scrape_all_alpaca, ticker)
        background_tasks.add_task(sec.scrape_all_sec, ticker)
    return {"message": "Scraping initiated for all tickers."}

"""
