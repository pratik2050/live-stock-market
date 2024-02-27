import pandas as pd
import numpy as np
import yfinance as yf
import talib

def calculate_ema(df, window):
    ema = df['Close'].ewm(span=window, min_periods=window).mean()
    return ema

def calculate_supertrend(df, window):
    df['ATR'] = df['High'] - df['Low']
    df['Basic Upper Band'] = (df['High'] + df['Low']) / 2 + (window * df['ATR'].rolling(window).mean())
    df['Basic Lower Band'] = (df['High'] + df['Low']) / 2 - (window * df['ATR'].rolling(window).mean())
    df['Final Upper Band'] = np.where(df['Basic Upper Band'] < df['Final Upper Band'].shift(1), df['Basic Upper Band'], df['Final Upper Band'].shift(1))
    df['Final Lower Band'] = np.where(df['Basic Lower Band'] > df['Final Lower Band'].shift(1), df['Basic Lower Band'], df['Final Lower Band'].shift(1))
    df['Supertrend'] = np.where(df['Close'] <= df['Final Upper Band'], df['Final Upper Band'], df['Final Lower Band'])
    return df['Supertrend']


def backtest_strategy(data):
    data['EMA_50'] = calculate_ema(data, 50)
    data['Supertrend'] = calculate_supertrend(data, 10)
    data['RSI'] = talib.RSI(data['Close'], timeperiod=14)
    data['Buy Signal'] = (data['Close'] > data['EMA_50']) & (data['Close'] > data['Supertrend']) & (data['RSI'] < 50)
    data['Sell Signal'] = (data['Close'] < data['EMA_50']) & (data['Close'] < data['Supertrend']) & (data['RSI'] > 50)

    position = None
    entry_price = None
    stop_loss = None
    target = None
    pnl = []

    for index, row in data.iterrows():
        if position is None:
            if row['Buy Signal']:
                position = 'buy'
                entry_price = row['Open']
                stop_loss = row['EMA_50']
                target = entry_price + 2 * (entry_price - stop_loss)
            elif row['Sell Signal']:
                position = 'sell'
                entry_price = row['Open']
                stop_loss = row['EMA_50']
                target = entry_price - 2 * (stop_loss - entry_price)
        else:
            if position == 'buy':
                if row['Low'] <= stop_loss:
                    pnl.append(stop_loss - entry_price)
                    position = None
                elif row['High'] >= target:
                    pnl.append(target - entry_price)
                    position = None
            elif position == 'sell':
                if row['High'] >= stop_loss:
                    pnl.append(entry_price - stop_loss)
                    position = None
                elif row['Low'] <= target:
                    pnl.append(entry_price - target)
                    position = None

    return sum(pnl)

# Example usage:
ticker = 'BTC-USD'
start_date = '2020-01-01'
end_date = '2023-01-01'
data = yf.download(ticker, start=start_date, end=end_date, interval='1d')
pnl = backtest_strategy(data)
print("Total P&L:", pnl)