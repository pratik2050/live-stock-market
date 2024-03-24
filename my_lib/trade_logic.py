# import pandas as pd
# import talib
import account_config



################################ Function to calculate technicals from data received #################################
def calculate_technicals(data):
    data['EMA50'] = data['Close'].ewm(span=50, adjust=False).mean()
    
    # # Calculate Supertrend (12,3)
    # supertrend = talib.SMA(data['Close'], timeperiod=6) + 1.5 * talib.STDDEV(data['Close'], timeperiod=6)
    # data['Supertrend_Up'] = supertrend
    
    # # Calculate RSI
    # data['RSI'] = talib.RSI(data['Close'], timeperiod=14)
    
    return data



#################################### Function to generate signals #########################################
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
        if data['Volume'] is None:
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



##################################### Function to Logic of Execute Orders and P&L #######################################
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

                    account_config.place_order(instrument_key=instrument_key, order_type='SL-M', transaction_type='BUY', stop_loss=stop_loss_price)

                    signals[i] = ''
                    break

                elif signals[i] == 'Sell':
                    position = 'Sell'
                    entry_price = data['Open'][i+1]
                    stop_loss_price = data['EMA50'][i]
                    target_price = entry_price - 2 * (stop_loss_price - entry_price)

                    account_config.place_order(instrument_key=instrument_key, order_type='SL-M', transaction_type='SELL', stop_loss=stop_loss_price)
    
                    signals[i] = ''
                    break

            else:
                if position == 'Buy' and time:
                    if data['Low'][i] <= stop_loss_price:
                        print(f' Date {time} Sell at StopLoss {stop_loss_price} bought at {entry_price} net {-abs(stop_loss_price - entry_price)}')
                        position = None
                        break
                    elif data['High'][i] >= target_price:
                        print(f' Date {time} Sell at target {target_price} bought at {entry_price} net {abs(target_price - entry_price)}')

                        position = None

                        account_config.place_order(instrument_key=instrument_key, order_type='MARKET', transaction_type='SELL', stop_loss=0)
                        break
                elif position == 'Sell' and time:
                    if data['High'][i] >= stop_loss_price:
                        print(f' Date {time} Buy at stoploss {stop_loss_price} Sold at {entry_price} net {-abs(entry_price - stop_loss_price)}')
                        position = None
                        break
                    elif data['Low'][i] <= target_price:
                        print(f' Date {time} Buy at target {target_price} Sold at {entry_price} net {abs(target_price - entry_price)}')

                        position = None

                        account_config.place_order(instrument_key=instrument_key, order_type='MARKET', transaction_type='BUY', stop_loss=0)
                        break

    return [position, entry_price, stop_loss_price, target_price]
