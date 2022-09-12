from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, TrailingStopOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest
from dateutil.tz import tzlocal
from datetime import datetime, timezone, timedelta
import dateutil.relativedelta
import config
import logging

# trading setup
SYMBOL = 'SPY'
PAPER = True  # paper trading
TIME_BUFFER = 900  # time buffer to trade after market is open and before market is close, in seconds
trading_client = TradingClient(config.APCA_API_KEY_ID, config.APCA_API_SECRET_KEY, paper=PAPER)
data_client = StockHistoricalDataClient(config.APCA_API_KEY_ID, config.APCA_API_SECRET_KEY)

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)


def is_market_open():
    """
    :return: market open status
    timestamp=datetime.datetime(2022, 9, 11, 5, 54, 47, 291764, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=72000))) is_open=False next_open=datetime.datetime(2022, 9, 12, 9, 30, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=72000))) next_close=datetime.datetime(2022, 9, 12, 16, 0, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=72000)))
    """
    return trading_client.get_clock()


def get_account():
    """
    :return: account info
    """
    return trading_client.get_account()


def list_positions():
    """
    :return: all open positions
    """
    try:
        positions = trading_client.get_all_positions()
        return [position for position in positions if positions]
    except Exception as _e:
        logging.error(_e)
        return None


def buy_close(_symbol):
    """
    :return: the BUY order at the end of a trading day
    """
    try:
        return trading_client.submit_order(
            order_data=TrailingStopOrderRequest(
                symbol=_symbol,
                qty=1,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY,
                trail_percent=2,
                extended_hours=False
            )
        )
    except Exception as _e:
        logging.error(_e)
        return None


def sell_open(_symbol):
    """
    :return: SELL/CLOSE all positions/orders at the beginning of the trading day
    """
    try:
        return trading_client.close_all_positions(cancel_orders=True)
    except Exception as _e:
        logging.error(_e)
        return None


def get_symbol_last_price(_symbol):
    """
    :return: the last 15-minute delayed price for SYMBOL
    """
    try:
        latest_quote = data_client.get_stock_latest_quote(StockLatestQuoteRequest(symbol_or_symbols=[_symbol]))
        return latest_quote[_symbol].ask_price
    except Exception as _e:
        logging.error(_e)
        return None


def main():
    logging.info(get_account().status)
    open_at = is_market_open().next_open.astimezone(tzlocal())
    close_at = is_market_open().next_close.astimezone(tzlocal())
    time_now = datetime.now(tzlocal())

    # if market not open, exit
    if not is_market_open().is_open:
        remaining_time = dateutil.relativedelta.relativedelta(time_now, open_at)
        logging.info(f"Market not open! {remaining_time}")
        exit()
    else:
        if list_positions():
            logging.info(list_positions())
        else:
            logging.info("No opened positions!")

        # validate if SELL is happening near market open time and if BUY is happening near market close time
        if get_symbol_last_price(SYMBOL):
            # if it's close to market close time, then BUY (only if we don't have any opened positions)
            if round((close_at-time_now).total_seconds()) < TIME_BUFFER and not list_positions():
                logging.info(buy_close(SYMBOL))
            # if it's right after the market open time, then SELL (if we have open positions)
            if round((time_now-open_at).total_seconds()) < TIME_BUFFER and list_positions():
                logging.info(sell_open(SYMBOL))
        else:
            logging.warning(f"Cannot get the last 15-minute delayed price for {SYMBOL}!")


if __name__ == "__main__":
    main()
