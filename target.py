import pandas as pd
import talib
import requests


### Function to fetch historical data ###

def fetch_data():
    url = "https://api.upstox.com/v2/historical-candle/{instrument_key}/{interval}/{to_date}/{from_date}"

    instrument_key = 'NSE_FO|52220'  ### NSE_FO|36611 -> BANKNIFTY24APRFUT
    interval = '30minute'
    to_date = '2024-02-29'
    from_date = '2024-01-01'

    url = url.format(instrument_key=instrument_key, interval=interval, to_date=to_date, from_date=from_date)
    
    headers = {
        'Accept': 'application/json'
    }

    response = requests.request("GET", url, headers=headers)

    return response.json()


### Function to calculate technicals from data received ###

def calculate_technicals(data):
    data['EMA50'] = data['Close'].ewm(span=50, adjust=False).mean()
    
    # Calculate Supertrend (12,3)
    supertrend = talib.SMA(data['Close'], timeperiod=12) + 3 * talib.STDDEV(data['Close'], timeperiod=12)
    data['Supertrend_Up'] = supertrend
    
    # Calculate RSI
    data['RSI'] = talib.RSI(data['Close'], timeperiod=14)
    
    return data


### Function to generate signals ###

def generate_signals(data):
    signals = []
    for i in range(len(data)):
        if i >= 2:
            # Condition for buy signal
            if data['Close'][i-2] > data['EMA50'][i-2] and data['Close'][i-1] > data['EMA50'][i-1] and data['Supertrend_Up'][i-1] > data['Close'][i-1] and data['RSI'][i-1] < 50:
                signals.append('Buy')
            # Condition for sell signal
            elif data['Close'][i-2] < data['EMA50'][i-2] and data['Close'][i-1] < data['EMA50'][i-1] and data['Close'][i-1] < data['Supertrend_Up'][i-1] and data['RSI'][i-1] > 50:
                signals.append('Sell')
            else:
                signals.append('')
        else:
            signals.append('')
    return signals


### Function to Execute orders and P&L ###

def execute_orders(data, signals):

    position = None
    entry_price = None
    stop_loss_price = None
    target_price = None
    pnl = []

    for i in range(len(data)):
        if i >= 2 and signals[i] != '':
            if position is None:
                if signals[i] == 'Buy':
                    position = 'Buy'
                    entry_price = data['Open'][i+1]
                    stop_loss_price = data['EMA50'][i]
                    target_price = data['Open'][i+1] + 2 * (data['Open'][i+1] - stop_loss_price)

                elif signals[i] == 'Sell':
                    position = 'Sell'
                    entry_price = data['Open'][i+1]
                    stop_loss_price = data['EMA50'][i]
                    target_price = data['Open'][i+1] - 2 * (stop_loss_price - data['Open'][i+1])
            else:
                time = data['Timestamp'][i]
                if position == 'Buy':
                    if data['Low'][i] <= stop_loss_price:
                        print(f' Date {time} Sell at StopLoss {stop_loss_price} bought at {entry_price} net {stop_loss_price - entry_price}')
                        pnl.append(stop_loss_price - entry_price)
                        position = None
                    elif data['High'][i] >= target_price:
                        print(f' Date {time} Sell at target {target_price} bought at {entry_price} net {target_price - entry_price}')
                        pnl.append(target_price - entry_price)
                        position = None

                elif position == 'Sell':
                    if data['High'][i] >= stop_loss_price:
                        print(f' Date {time} Buy at stoploss {stop_loss_price} Sold at {entry_price} net {stop_loss_price - entry_price}')
                        pnl.append(stop_loss_price - entry_price)
                        position = None
                    elif data['Low'][i] <= target_price:
                        print(f' Date {time} Buy at target {target_price} Sold at {entry_price} net {target_price - entry_price}')
                        pnl.append(target_price - entry_price)
                        position = None

    return pnl


### Main Function ###

if __name__ == "__main__":
    response_data = fetch_data()
    candles_data = response_data['data']['candles']

    df = pd.DataFrame(candles_data, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'Extra'])
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])

    df = calculate_technicals(df)

    signals = generate_signals(df)

    pnl = execute_orders(data=df, signals=signals)