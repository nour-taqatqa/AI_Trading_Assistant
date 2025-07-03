# my_scrapers/sec.py

import os
import requests
from dotenv import load_dotenv
import pandas as pd
from datetime import date
from utils import get_date_ranges


load_dotenv()
SEC_API_KEY = os.getenv("SEC_API_KEY")

BASE_URL = os.getenv("SEC_API_URL")
headers = {"Authorization": SEC_API_KEY}

# Mapping of how many periods and expected size per frequency
SCRAPE_PLAN = {
    "yearly": {"num_periods": 10, "size": 10},
    "quarterly": {"num_periods": 20, "size": 20},
    "monthly": {"num_periods": 36, "size": 36},
    "weekly": {"num_periods": 52, "size": 52}
}
def get_sec_filings_df(ticker: str, form_type="8-K", frequency="weekly") -> pd.DataFrame:
    size = SCRAPE_PLAN.get(frequency, {}).get("size", 10)  # fallback to 10 if frequency not found

    query = {
        "query": {
            "query_string": {
                "query": f'formType:"{form_type}" AND ticker:"{ticker.upper()}"'
            }
        },
        "from": "0",
        "size": str(size),
        "sort": [{"filedAt": {"order": "desc"}}]
    }

    response = requests.post(BASE_URL, json=query, headers=headers)
    data = response.json()

    filings = data.get("filings", [])
    if not filings:
        print(f"No filings found for {ticker} ({form_type}, {frequency}).")
        return pd.DataFrame()

    df = pd.DataFrame(filings)

    cols_to_show = ["ticker", "formType", "companyName", "filedAt", "description", "id", "linkToFilingDetails"]
    return df[cols_to_show] if all(col in df.columns for col in cols_to_show) else df


'''
def get_company_filings(ticker, form_type=None): #will define the weekly, yearly, etc here and just call them in the weekly scraper 
    query = {
        "query": {
            "query_string": {
                "query": f"ticker:{ticker}" + (f" AND formType:{form_type}" if form_type else "")
            }
        },
        "from": "0",
        "size": "10",
        "sort": [{"filedAt": {"order": "desc"}}]
    }
    response = requests.post(f"{BASE_URL}/filings", json=query, headers={"Authorization": SEC_API_KEY})
    return response.json()
'''
'''
def get_filings_since(ticker, last_scraped_date, form_type=None, frequency='weekly', size=52): #what should I put sizer to be 
    today = date.today().isoformat()

    query_conditions = [f'ticker:"{ticker.upper()}"']
    if form_type:
        query_conditions.append(f'formType:"{form_type}"')

    query_string = " AND ".join(query_conditions)

    query = {
        "query": {
            "bool": {
                "must": [
                    {"query_string": {"query": query_string}},
                    {"range": {"filedAt": {"gte": last_scraped_date, "lte": today}}}
                ]
            }
        },
        "from": "0",
        "size": str(size),
        "sort": [{"filedAt": {"order": "desc"}}]
    }

    headers = {"Authorization": SEC_API_KEY}
    response = requests.post(BASE_URL, json=query, headers=headers)

    if response.ok:
        filings = [hit["_source"] for hit in response.json().get("hits", {}).get("hits", [])]
        return pd.DataFrame(filings)
    else:
        raise Exception("Failed to retrieve new SEC filings.")
'''
#previously final version
'''
def get_sec_filings_incremental(ticker, form_type=None, frequency=None, last_scraped_date=None): #takes care of 8-k and 10k, 10-Q, earnings filings and form 4 are left 
    """
    supposed to take care of only retrieving since last date info have been retrieved 
    supposed to work for first time retrieval (retireve up to 10 years back - sets defualt date to 10 years ago)
    and also work with dates in the furutre without scraping redundant info 
    - this function is used in yearly, quarterly, weekly, 
    """
    today = date.today().isoformat()
    size = SCRAPE_PLAN[frequency]["size"]

    all_filings = []

    # 🟢 First-time scrape: use multiple historical periods
    if last_scraped_date is None:
        num_periods = SCRAPE_PLAN[frequency]["num_periods"]
        date_ranges = get_date_ranges(frequency, num_periods)
    # 🔁 Subsequent scrape: use last_scraped_date to today
    else:
        date_ranges = [(last_scraped_date, today)]

    for start_date, end_date in date_ranges:
        query_conditions = [f'ticker:"{ticker.upper()}"']
        if form_type:
            query_conditions.append(f'formType:"{form_type}"')

        query_string = " AND ".join(query_conditions)

        query = {
            "query": {
                "bool": {
                    "must": [
                        {"query_string": {"query": query_string}},
                        {"range": {"filedAt": {"gte": start_date, "lte": end_date}}}
                    ]
                }
            },
            "from": "0",
            "size": str(size),
            "sort": [{"filedAt": {"order": "desc"}}]
        }

        headers = {"Authorization": SEC_API_KEY}
        response = requests.post(BASE_URL, json=query, headers=headers)

        if response.ok:
            filings = [hit["_source"] for hit in response.json().get("hits", {}).get("hits", [])]
            all_filings.extend(filings)
        else:
            print(f"Failed to retrieve filings for {ticker} from {start_date} to {end_date}")

    if not all_filings:
        return pd.DataFrame()

    df = pd.DataFrame(all_filings)
    return df[['ticker', 'companyName', 'formType', 'filedAt', 'documentFormatFiles']].sort_values(by='filedAt', ascending=False)

#def get_10k_filings(ticker):
#    return get_company_filings(ticker, form_type="10-K")

#def get_8k_filings(ticker): - the function above takes care of 10-k and of 8-k filings 
#    return get_company_filings(ticker, form_type="8-K")

def get_insider_transactions(ticker): #won't use 
    url = f"{BASE_URL}/insider-trading?appkey={SEC_API_KEY}&ticker={ticker}"
    response = requests.get(url)
    return response.json()

#have these functions run for any single ticker 
#store into a df 
'''