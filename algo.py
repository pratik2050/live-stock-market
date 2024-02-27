import yfinance as yf
import pandas as pd
import numpy as np
import talib

# Function to fetch historical OHLC data for the specified ticker symbol
def fetch_historical_data(ticker_symbol, start_date, end_date):
    data = yf.download(ticker_symbol, start=start_date, end=end_date)
    return data

# Function to calculate EMA50, Supertrend (12,3), and RSI
def calculate_technical_indicators(data):
    # Calculate EMA50
    data['EMA50'] = data['Close'].ewm(span=50, adjust=False).mean()
    
    # Calculate Supertrend (12,3)
    supertrend = talib.SMA(data['Close'], timeperiod=12) + 3 * talib.STDDEV(data['Close'], timeperiod=12)
    data['Supertrend_Up'] = supertrend
    
    # Calculate RSI
    data['RSI'] = talib.RSI(data['Close'], timeperiod=14)
    
    return data

# Function to generate buy or sell signals based on the specified conditions
def generate_signals(data):
    signals = []
    for i in range(len(data)):
        if i >= 2:
            # Condition for buy signal
            if data['Close'][i-2] > data['EMA50'][i-2] and data['Close'][i-1] > data['EMA50'][i-1] and \
               data['Supertrend_Up'][i-1] > data['Close'][i-1] and data['RSI'][i-1] < 50:
                signals.append('Buy')
            # Condition for sell signal
            elif data['Close'][i-2] < data['EMA50'][i-2] and data['Close'][i-1] < data['EMA50'][i-1] and \
                 data['Close'][i-1] < data['Supertrend_Up'][i-1] and data['RSI'][i-1] > 50:
                signals.append('Sell')
            else:
                signals.append('')
        else:
            signals.append('')
    return signals

# Function to execute buy or sell orders based on the generated signals
def execute_orders(data, signals):
    stop_loss = data['EMA50']
    orders = []
    for i in range(len(data)):
        if i >= 2 and signals[i] != '':
            if signals[i] == 'Buy':
                # Calculate stop-loss and target
                stop_loss_price = data['EMA50'][i]
                target_price = data['Open'][i+1] + 2 * (data['Open'][i+1] - stop_loss_price)
                orders.append(('Buy', data['Open'][i+1], stop_loss_price, target_price))
            elif signals[i] == 'Sell':
                # Calculate stop-loss and target
                stop_loss_price = data['EMA50'][i]
                target_price = data['Open'][i+1] - 2 * (stop_loss_price - data['Open'][i+1])

                temp = stop_loss_price
                stop_loss_price = target_price
                target_price = temp

                orders.append(('Sell', data['Open'][i+1], stop_loss_price, target_price))
        else:
            orders.append(('Hold', None, None, None))
    return orders

# Main function to execute the algorithm
def execute_algorithm(ticker_symbol, start_date, end_date):
    # Fetch historical data
    data = fetch_historical_data(ticker_symbol, start_date, end_date)
    
    # Calculate technical indicators
    data = calculate_technical_indicators(data)
    
    # Generate signals
    signals = generate_signals(data)
    
    # Execute orders
    orders = execute_orders(data, signals)
    
    return orders

# Example usage
ticker_symbol = '^NSEBANK'
start_date = '2024-01-01'
end_date = '2024-02-27'

orders = execute_algorithm(ticker_symbol, start_date, end_date)
for i, order in enumerate(orders):
    print(f"Day {i+1}: {order[0]} at {order[1]} (Stop-loss: {order[2]}, Target: {order[3]})")
