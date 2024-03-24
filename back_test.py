import pandas as pd

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
instrument_key = 'NSE_FO|36612'
interval = '30minute'
to_date = '2024-03-03'
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


if __name__ == '__main__':
    test()