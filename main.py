import pandas as pd
import time
from threading import Thread

import sys
sys.path.append('./my_lib')

from my_lib import auth as auth
from my_lib import web_socket_data as ws
from my_lib import AlgoTrade as atr


########################### Start Authentication ###############################
auth.make_auth()


############################### Starting Web Socket Feed ####################################
ws.configure_token()

ws.run_socket()

time.sleep(5)

data_thread = Thread(target=ws.get_live_data)
data_thread.start()


################################## Trade Logic ######################################

position = None
entry_price = None
stop_loss_price = None
target_price = None


def execute_orders(data, signals):

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
                        position = None
                    elif data['High'][i] >= target_price:
                        print(f' Date {time} Sell at target {target_price} bought at {entry_price} net {target_price - entry_price}')
                        position = None

                elif position == 'Sell':
                    if data['High'][i] >= stop_loss_price:
                        print(f' Date {time} Buy at stoploss {stop_loss_price} Sold at {entry_price} net {stop_loss_price - entry_price}')
                        position = None
                    elif data['Low'][i] <= target_price:
                        print(f' Date {time} Buy at target {target_price} Sold at {entry_price} net {target_price - entry_price}')
                        position = None

    return


while True:
    time.sleep(20)

    candles_data = ws.candles

    df = pd.DataFrame(candles_data, columns=['Timestamp', 'Open', 'High', 'Low', 'Close'])
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])

    df = atr.calculate_technicals(df)

    signals = atr.generate_signals(df)

    execute_orders(data=df, signals=signals)

