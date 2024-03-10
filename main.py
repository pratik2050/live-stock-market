import pandas as pd
import time
from threading import Thread

import sys
sys.path.append('./my_lib')

from my_lib import auth as auth
from my_lib import web_socket as ws
from my_lib import account_config as account
from my_lib import trade_logic as trade
from my_lib import market_ohlc as ohlc



############################### Setting Up Configuration ################################
instrument_key = 'NSE_FO|36611'
interval = '1minute'



########################### Start Authentication ###############################
auth.make_auth()

time.sleep(1)

############################### Start Web Socket Feed ####################################
# ws.configure_token()

# ws.run_socket()

# time.sleep(5)

# data_thread = Thread(target=ws.get_live_data)
# data_thread.start()



################################ Get OHLC Interval Quote ###################################
ohlc.configure_token()

def get_ohlc_1min():
    global ohlc_data
    ohlc_data = ohlc.get_ohlc_quote(instrument_key=instrument_key, interval=interval)

    return ohlc_data



################################## Trade Execute in Live Market ######################################
entry_price = None
position = None
stop_loss_price = None
target_price = None
prev_time = 0

while True:
    time.sleep(60)

    ohlc_data = ohlc_data.get('ohlc', {})


    candles_data = [instrument_key, time.time(), ohlc_data.get('open'), ohlc_data.get('high'), ohlc_data.get('low'), ohlc_data.get('close')]

    df = pd.DataFrame(candles_data, columns=[instrument_key, 'Timestamp', 'Open', 'High', 'Low', 'Close'])

    df = trade.calculate_technicals(data=df)

    signals = trade.generate_signals(data=df)

    P_E_SL_T = trade.execute_orders(data=df, signals=signals, position=position, entry_price=entry_price, stop_loss_price=stop_loss_price, target_price=target_price, prev_time=prev_time)

    position = P_E_SL_T[0]
    entry_price = P_E_SL_T[1]
    stop_loss_price = P_E_SL_T[2]
    target_price = P_E_SL_T[3]
    prev_time = P_E_SL_T[4]
