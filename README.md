# alpaca_buy_close_sell_open
Alpaca broker (paper trading) buy close/sell open strategy - https://finance.yahoo.com/news/buy-close-sell-open-114705554.html

The code should BUY when close to the market closing time and SELL right after the market opening time.

Can be setup as a cron job or as an AWS Lambda scheduled.

Create config.py and fill the API keys from https://app.alpaca.markets/ (https://alpaca.markets/learn/connect-to-alpaca-api/)
```angular2html
# API config
APCA_API_BASE_URL = 'https://paper-api.alpaca.markets'
APCA_API_KEY_ID = '...'
APCA_API_SECRET_KEY = '...'
```
