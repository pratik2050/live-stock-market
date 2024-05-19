import pandas as pd
import time
from datetime import datetime
from threading import Thread
import json

import sys
sys.path.append('./my_lib')

from my_lib import auth as auth
from my_lib import web_socket as ws
from my_lib import account_config as account
from my_lib import trade_logic as trade
from my_lib import market_ohlc as ohlc



############################### Setting Up Configuration ################################

global entry_price, position, stop_loss_price, target_price

instrument_key = 'NSE_FO|46930'                  # Set Instrument token key from excel
instrument_name = 'NSE_FO:NIFTY24MAYFUT'     # Set Instrument Name from excel 
interval_histoical = '1minute'
interval_quote = 'I1'

from_date = '2024-03-21'      # Set the date in format of 'yy-mm-dd' when last trade occured
to_date = '2024-03-22'        # Set tomorrow date in format of 'yy-mm-dd'


historical_data = ohlc.fetch_historical_data(instrument_key=instrument_key, interval=interval_histoical, to_date=to_date, from_data=from_date)
historical_data = historical_data['data']['candles']

historical_df = pd.DataFrame(historical_data, columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Extra'])
historical_df = pd.to_datetime(historical_df['Time'])
historical_df[::-1]

json_data = 123
with open('ohlc.json', 'r') as json_file:
    json_data = json.load(json_file)

entry_price = json_data.get('entry_price')
position = json_data.get('position')
stop_loss_price = json_data.get('stop_loss_price')
target_price = json_data.get('target_price')


########################### Start Authentication ###############################
auth.make_auth()
time.sleep(1)


############################### Start Web Socket Feed ####################################
# ws.configure_token()

# ws.run_socket()

# time.sleep(5)

# data_thread = Thread(target=ws.get_live_data)
# data_thread.start()


################################## Trade Execute in Live Market ######################################
while True:
    today_data = ohlc.get_ohlc_quote(instrument_key=instrument_key, interval=interval_quote)

    today_data = today_data[instrument_name]['ohlc']

    today_data = [datetime.now(), today_data.get('open'), today_data.get('high'), today_data.get('low'), today_data.get('close'), "", ""]
    today_df = pd.DataFrame(today_data, columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Extra'])
    today_df = pd.to_datetime(today_df['Time'])

    df = historical_df._append(today_data, ignore_index=True)

    df = trade.calculate_technicals(data=df)

    signals = trade.generate_signals(data=df)

    P_E_SL_T = trade.execute_orders(data=df, signals=signals, position=position, entry_price=entry_price, stop_loss_price=stop_loss_price, target_price=target_price, instrument_key=instrument_name)

    position = P_E_SL_T[0]
    entry_price = P_E_SL_T[1]
    stop_loss_price = P_E_SL_T[2]
    target_price = P_E_SL_T[3]

    json_data = [entry_price, stop_loss_price, target_price, position]

    ohlc.write_json(json_data)

    time.sleep(61)
