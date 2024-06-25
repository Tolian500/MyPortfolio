from datetime import datetime, timedelta
import pandas as pd
import pybit
from pybit.unified_trading import HTTP
import ta


class BybitManager:
    def __init__(self, api_key, api_secret, window):
        self.session = HTTP(testnet=False, api_key=api_key, api_secret=api_secret)
        self.window = window

    def fetch_kline_data(self, symbol, interval, start_time, end_time):
        if interval == 'D':  # 1 day interval
            # Ensure we have enough data by setting the start_time earlier
            start_time = end_time - (self.window + 100) * 24 * 60 * 60 * 1000  # Adjusting start time to get sufficient data
            print(end_time)
        try:
            response = self.session.get_kline(
                category="spot",
                symbol=symbol,
                interval=interval,
                start=start_time,
                end=end_time,
                limit=200  # maximum number of K-lines to fetch
            )

            if response['retCode'] == 0:
                kline_data = response['result']['list']
                print(kline_data)
                return kline_data
            else:
                print(f"Error fetching K-line data: {response['retMsg']}")
                return None
        except pybit.exceptions.FailedRequestError as e:
            print(f"FailedRequestError: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    def calculate_rsi(self, kline_data):
        df = pd.DataFrame(kline_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'other'])
        df['timestamp'] = pd.to_datetime(pd.to_numeric(df['timestamp']), unit='ms')
        df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)

        # Set timestamp as index
        df.set_index('timestamp', inplace=True)

        # Calculate RSI
        df['RSI'] = ta.momentum.RSIIndicator(close=df['close'], window=self.window).rsi()

        return df

    def print_kline_data(self, kline_data, symbol):
        print(f"K-line data for {symbol}:")
        for item in kline_data[:1]:
            timestamp, open_price, high_price, low_price, close_price, volume, turnover = item
            timestamp = int(timestamp)
            dt_object = datetime.fromtimestamp(timestamp / 1000)
            print(f"Timestamp: {timestamp} (time: {dt_object}) , Open: {open_price}, High: {high_price}, Low: {low_price}, Close: {close_price}, Volume: {volume}, Turnover: {turnover}")