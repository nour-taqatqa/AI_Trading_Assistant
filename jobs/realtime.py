(only if you want to trigger scraping upon new events)

#SEC API POST request for latest 8-K, Form 4 (set size: 1) – polling every 5–10 minutes during trading hours is reasonable - won't do it 

get_last_trade(symbol), get_last_quote(symbol) – if building a live dashboard

WebSocket for live trades (if latency matters) #might skip this 
    
#    On-Demand / Manual -- don't know where to put this
(for user interaction or periodic review)

submit_order(...) #didn't write - puts orders 

get_account() #alpaca - wrote - gets yoru alpaca account info

list_positions() #alpaca - won't use 

list_orders(...) #alpaca - won't use 

