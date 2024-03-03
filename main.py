import pandas as pd
import time

import auth as auth
import AlgoTrade as atr


### Start Authentication ###
auth.make_auth()



position = None
entry_price = None
stop_loss_price = None
target_price = None
pnl = []

### Logic of Order Execution ###

def execute_orders(data, signals):

    # position = None
    # entry_price = None
    # stop_loss_price = None
    # target_price = None
    # pnl = []

    for i in range(len(data)):
        if i >= 2 and signals[i] != '':
            if position is None:
                time = data['Timestamp'][i]
                if signals[i] == 'Buy':
                    position = 'Buy'
                    entry_price = data['Open'][i+1]
                    stop_loss_price = data['EMA50'][i]
                    target_price = data['Open'][i+1] + 2 * (data['Open'][i+1] - stop_loss_price)
                    print(f'bought at {time} price {entry_price}')

                elif signals[i] == 'Sell':
                    position = 'Sell'
                    entry_price = data['Open'][i+1]
                    stop_loss_price = data['EMA50'][i]
                    target_price = data['Open'][i+1] - 2 * (stop_loss_price - data['Open'][i+1])
                    print(f'sold at {time} price {entry_price}')
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


while True:
    time.sleep(1)
    ### Getting OHLC data in 30 minute interval ###
    ticker_key = 'NSE_FO|36611'

    ticker_data = atr.fetch_data(ticker_key=ticker_key)
    candles_data = ticker_data['data']['candles']

    df = pd.DataFrame(candles_data, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'Extra'])
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])


    ### Calculating Technicals ###
    df = atr.calculate_technicals(data=df)

    signals = atr.generate_signals(data=df)

    execute_orders(data=df, signals=signals)
    
    time.sleep(1800)