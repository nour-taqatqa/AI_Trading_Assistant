# ticker_loader.py
# import os -- commented out and imported as part of hte function for easier implemetnation outside moduel
# from dotenv import load_dotenv
# from alpaca.trading.client import TradingClient
# from alpaca.trading.requests import GetAssetsRequest
# from alpaca.trading.enums import AssetStatus

# load_dotenv()


# trading_client = TradingClient(
#     os.getenv("ALPACA_API_KEY"),
#     os.getenv("ALPACA_SECRET_KEY"),
#     paper=True  # Set to False if you're using live trading
# )

def get_tradable_tickers(exchange_filter=["NASDAQ"]): #the filter can be ["NASDAQ", "NYSE"] #3000 trades
    import os
    from dotenv import load_dotenv
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import GetAssetsRequest
    from alpaca.trading.enums import AssetStatus
    load_dotenv()


    trading_client = TradingClient(
        os.getenv("ALPACA_API_KEY"),
        os.getenv("ALPACA_SECRET_KEY"),
        paper=True  # Set to False if you're using live trading
    )
    request = GetAssetsRequest(status=AssetStatus.ACTIVE)
    assets = trading_client.get_all_assets(request)

    tickers = [
        asset.symbol for asset in assets
        if asset.tradable and (exchange_filter is None or asset.exchange in exchange_filter)
    ]
    return tickers

if __name__ == "__main__": #-- it works 
   tickers= get_tradable_tickers()#exchange_filter=["NYSE", "NASDAQ"])
   #print(tickers[:10])  # print first 10 to verify it's working
