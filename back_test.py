import numpy as np
import pandas as pd
import talib

import sys
sys.path.append('./my_lib')

from my_lib import market_ohlc as ohlc
from my_lib import trade_logic as trade


def calculate_technicals(data):
    data['EMA50'] = data['Close'].ewm(span=50, adjust=False).mean()

    return data


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
            if (is_crossover_green(data, i-2) and is_closed_or_open_above(data, i-1) and (is_crossover_green(data, i) == False and is_crossover_red(data, i) == False)):
                signals.append('Buy')
                time = data['Timestamp'][i]
            # Condition for sell signal
            elif (is_crossover_red(data, i-2) and is_closed_or_open_below(data, i-1) and (is_crossover_green(data, i) == False and is_crossover_red(data, i) == False)):
                signals.append('Sell')
                time = data['Timestamp'][i]
            else:
                signals.append('')
        else:
            signals.append('')
    return signals

def calculate_Supertrend(df, atr_period, multiplier):
    high = df['High']
    low = df['Low']
    close = df['Close']
    atr = talib.ATR(high.values, low.values, close.values, timeperiod=atr_period)
    hl2 = (high + low) / 2
    final_upperband = np.zeros(len(close))
    final_lowerband = np.zeros(len(close))
    Supertrend = np.zeros(len(close))

    for i in range(atr_period, len(close)):
        if i == atr_period:
            final_upperband[i] = hl2[i] + (multiplier * atr[i])
            final_lowerband[i] = hl2[i] - (multiplier * atr[i])
        else:
            final_upperband[i] = min(hl2[i] + (multiplier * atr[i]), final_upperband[i-1]) if close[i-1] <= final_upperband[i-1] else hl2[i] + (multiplier * atr[i])
            final_lowerband[i] = max(hl2[i] - (multiplier * atr[i]), final_lowerband[i-1]) if close[i-1] >= final_lowerband[i-1] else hl2[i] - (multiplier * atr[i])

        Supertrend[i] = final_lowerband[i] if close[i] > final_lowerband[i] else final_upperband[i]

    df['Supertrend'] = Supertrend
    return df

def backtest_strategy_with_supertend(data):
    data['EMA50'] = data['Close'].ewm(span=50, adjust=False).mean()
    data['RSI'] = talib.RSI(data['Close'], timeperiod=14)
    data = calculate_Supertrend(data, 12, 3)  # Adjust these parameters as needed

    signals = []
    signals_one = []
    positions = []
    for i in range(len(data)):  # Start at 50 to ensure EMA and other indicators have enough data
        if data['Close'][i] > data['EMA50'][i] and data['RSI'][i] > 50 and data['Close'][i] > data['Supertrend'][i]:
            # Entry for Buy
            if not positions or positions[-1][0] == 'sell':
                stop_loss = data['Supertrend'][i]
                target = data['Close'][i] + (data['Close'][i] - stop_loss)
                positions.append(('buy', data['Timestamp'][i], data['Close'][i], stop_loss, target))
                signals.append((data['Timestamp'][i], 'Buy', 'Entry Price:', data['Close'][i], 'Stop Loss:', stop_loss, 'Target:', target))
                signals_one.append('Buy')

        elif data['Close'][i] < data['EMA50'][i] and data['RSI'][i] < 50 and data['Close'][i] < data['Supertrend'][i]:
            # Entry for Sell
            if not positions or positions[-1][0] == 'buy':
                stop_loss = data['Supertrend'][i]
                target = data['Close'][i] - (stop_loss - data['Close'][i])
                positions.append(('sell', data['Timestamp'][i], data['Close'][i], stop_loss, target))
                signals.append((data['Timestamp'][i], 'Sell', 'Entry Price:', data['Close'][i], 'Stop Loss:', stop_loss, 'Target:', target))
                signals_one.append('Sell')
        else:
            signals_one.append('')

    for signal in signals:
        print(signal)

    print()
    

    return signals_one



################################### Trade Logic ###########################################

def execute_orders(data, signals, position, entry_price, stop_loss_price, target_price, instrument_key):

    for i in range(len(data)):
        if i >= 2 and signals[i] != '':
            time = data['Timestamp'][i]
            if position is None and time:
                if signals[i] == 'Buy':
                    position = 'Buy'
                    entry_price = data['Open'][i+1]
                    stop_loss_price = data['EMA50'][i] 
                    target_price = entry_price + 2 * (entry_price - stop_loss_price)

                elif signals[i] == 'Sell':
                    position = 'Sell'
                    entry_price = data['Open'][i+1]
                    stop_loss_price = data['EMA50'][i]
                    target_price = entry_price - 2 * (stop_loss_price - entry_price)

            else:
                if position == 'Buy' and time:
                    if data['Low'][i] <= stop_loss_price:
                        print(f' Date {time} Sell at StopLoss {stop_loss_price} bought at {entry_price} net {-abs(stop_loss_price - entry_price)}')
                        position = None
                    elif data['High'][i] >= target_price:
                        print(f' Date {time} Sell at target {target_price} bought at {entry_price} net {abs(target_price - entry_price)}')

                        position = None
                elif position == 'Sell' and time:
                    if data['High'][i] >= stop_loss_price:
                        print(f' Date {time} Buy at stoploss {stop_loss_price} Sold at {entry_price} net {-abs(entry_price - stop_loss_price)}')
                        position = None
                        break
                    elif data['Low'][i] <= target_price:
                        print(f' Date {time} Buy at target {target_price} Sold at {entry_price} net {abs(target_price - entry_price)}')

                        position = None


    return [position, entry_price, stop_loss_price, target_price]


######################################### Back Test with Data ################################################
instrument_key = 'NSE_EQ|INE075A01022'
interval = '30minute'
to_date = '2024-05-10'
from_date = '2024-01-01'


def test():
    data = ohlc.fetch_historical_data(instrument_key=instrument_key, interval=interval, to_date=to_date, from_data=from_date)
    data = data['data']['candles']

    df = pd.DataFrame(data, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Vol', 'Extra'])
    df[::-1]

    df = calculate_technicals(df)

    signals = generate_signals(df)
    
    entry_price = None
    position = None
    stop_loss_price = None
    target_price = None

    res = execute_orders(data=df, signals=signals, position=position, entry_price=entry_price, stop_loss_price=stop_loss_price, target_price=target_price, instrument_key=instrument_key)
  
    position = res[0]
    entry_price = res[1]
    stop_loss_price = res[2]
    target_price = res[3]

def test_with_Supertrend():
    data = ohlc.fetch_historical_data(instrument_key=instrument_key, interval=interval, to_date=to_date, from_data=from_date)
    data = data['data']['candles']

    df = pd.DataFrame(data, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Vol', 'Extra'])
    df[::-1]

    signals = backtest_strategy_with_supertend(data=df)

    entry_price = None
    position = None
    stop_loss_price = None
    target_price = None

    res = execute_orders(data=df, signals=signals, position=position, entry_price=entry_price, stop_loss_price=stop_loss_price, target_price=target_price, instrument_key=instrument_key)

    position = res[0]
    entry_price = res[1]
    stop_loss_price = res[2]
    target_price = res[3]

if __name__ == '__main__':
    #test()
    test_with_Supertrend()