import pandas as pd
import talib
import requests

### Configure access_token ###
def configure_token():
    global access_token
    filename =f"accessToken.txt"
    with open(filename,"r") as file:
        access_token = file.read()


### Function to fetch historical data ###
def fetch_data(ticker_key):
    url = "https://api.upstox.com/v2/historical-candle/{instrument_key}/{interval}/{to_date}/{from_date}"

    instrument_key = ticker_key  ### NSE_FO|36611 -> BANKNIFTY24MARFUT
    interval = '30minute'
    to_date = '2024-03-07'
    from_date = '2024-01-01'

    url = url.format(instrument_key=instrument_key, interval=interval, to_date=to_date, from_date=from_date)
    
    headers = {
        'Accept': 'application/json'
    }

    response = requests.request("GET", url, headers=headers)

    return response.json()


### Function to calculate technicals from data received ###
def calculate_ema50(data):
    data['EMA50'] = data['Close'].ewm(span=50, adjust=False).mean()
    
    # Calculate Supertrend (12,3)
    supertrend = talib.SMA(data['Close'], timeperiod=12) + 3 * talib.STDDEV(data['Close'], timeperiod=12)
    data['Supertrend_Up'] = supertrend
    
    # Calculate RSI
    data['RSI'] = talib.RSI(data['Close'], timeperiod=14)
    
    return data


### Function to generate signals ###
def is_crossover_green(df, i):
    if (df['Close'][i] > df['EMA50'][i] and df['Open'][i] < df['EMA50'][i]):
        return True
    else:
        return False
    
def is_crossover_red(df, i):
    if (df['Close'][i] < df['EMA50'][i] and df['Open'][i] > df['EMA50'][i]):
        return True
    else:
        return False
    
def is_crossover_high_low(df, i):
    if (df['High'][i] > df['EMA50'][i] and df['Low'][i] < df['EMA50'][i]):
        return True
    else:
        return False
    
def is_closed_or_open_above(df, i):
    if(df['Open'][i] > df['EMA50'][i] and df['Close'][i] > df['EMA50'][i]):
        return True
    else:
        return False

def is_closed_or_open_below(df, i):
    if(df['Open'][i] < df['EMA50'][i] and df['Close'][i] < df['EMA50'][i]):
        return True
    else:
        return False


def generate_signals(data):
    signals = []
    for i in range(len(data)):
        if i >= 2:
            # Condition for buy signal
            if (is_crossover_green(data, i-2) and is_closed_or_open_above(data, i-1) and (is_crossover_high_low(data, i) == False)):
                signals.append('Buy')
                time = data['Timestamp'][i]
            # Condition for sell signal
            elif (is_crossover_red(data, i-2) and is_closed_or_open_below(data, i-1) and (is_crossover_high_low(data, i) == False)):
                signals.append('Sell')
                time = data['Timestamp'][i]
            else:
                signals.append('')
        else:
            signals.append('')
    return signals


### Function to Get Postion of account ###
def get_position():
    url = 'https://api.upstox.com/v2/portfolio/short-term-positions'
    headers = {
        'Accept': 'application/json',
        'Authorization': access_token
    }

    response = requests.request("GET", url, headers=headers)

    return response.json()


### Function to Place Order ###
def place_order(instrument_key, order_type, transaction_type, stop_loss):
    url = 'https://api.upstox.com/v2/order/place'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': access_token,
    }

    data = {
        'quantity': 75,
        'product': 'I',
        'validity': 'DAY',
        'price': 0.0,
        'tag': 'string',
        'instrument_token': instrument_key,
        'order_type': order_type,
        'transaction_type': transaction_type,
        'disclosed_quantity': 0,
        'trigger_price': stop_loss,
        'is_amo': False,
    }

    response = requests.request("POST", url, headers=headers, json=data)

    return response.json()



### Function to Logic of Execute Orders and P&L ###
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
                    stop_loss_price = data['EMA50'][i] # entry_price - 40
                    target_price = entry_price + 2 * (entry_price - stop_loss_price) # entry_price + 80

                elif signals[i] == 'Sell':
                    position = 'Sell'
                    entry_price = data['Open'][i+1]
                    stop_loss_price = data['EMA50'][i] # entry_price + 40
                    target_price = entry_price - 2 * (stop_loss_price - entry_price) # entry_price- 80
            else:
                time = data['Timestamp'][i]
                if position == 'Buy':
                    if data['Low'][i] <= stop_loss_price:
                        print(f' Date {time} Sell at StopLoss {stop_loss_price} bought at {entry_price} net {-abs(stop_loss_price - entry_price)}')
                        pnl.append(-abs(entry_price - stop_loss_price))
                        position = None
                    elif data['High'][i] >= target_price:
                        print(f' Date {time} Sell at target {target_price} bought at {entry_price} net {abs(target_price - entry_price)}')
                        pnl.append(abs(target_price - entry_price))
                        position = None

                elif position == 'Sell':
                    if data['High'][i] >= stop_loss_price:
                        print(f' Date {time} Buy at stoploss {stop_loss_price} Sold at {entry_price} net {-abs(entry_price - stop_loss_price)}')
                        pnl.append(-abs(entry_price - stop_loss_price))
                        position = None
                    elif data['Low'][i] <= target_price:
                        print(f' Date {time} Buy at target {target_price} Sold at {entry_price} net {abs(target_price - entry_price)}')
                        pnl.append(abs(entry_price - target_price))
                        position = None

    return pnl



def back_test():
    data = fetch_data(ticker_key='NSE_FO|36612')
    data = data['data']['candles']
    data = data[::-1]

    df = pd.DataFrame(data, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Vol', 'Extra'])
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])

    df = calculate_ema50(df)

    signals = generate_signals(df)

    res = execute_orders(data=df, signals=signals)
    print(sum(res))

back_test()