
def get_yfinance_analyst_insights(ticker_symbol: str):
    """Returns recommendations and target price as two DataFrames."""
    import yfinance as yf
    import pandas as pd

    ticker = yf.Ticker(ticker_symbol)

    recs_df = ticker.recommendations
    target_price = ticker.info.get("targetMeanPrice")

    # Wrap scalar in DataFrame
    target_df = pd.DataFrame([{
        "ticker": ticker_symbol,
        "target_mean_price": target_price
    }])

    return recs_df, target_df

recs_df, target_df = get_yfinance_analyst_insights("MSFT")
print("Target Mean Price:", target_df["target_mean_price"].iloc[0])
print("Recommendations (last 5):")
print(recs_df.tail())