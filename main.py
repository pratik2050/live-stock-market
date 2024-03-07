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


########################### Start Authentication ###############################
# auth.make_auth()


############################### Start Web Socket Feed ####################################
# ws.configure_token()

# ws.run_socket()

# time.sleep(5)

# data_thread = Thread(target=ws.get_live_data)
# data_thread.start()


################################ Get OHLC Interval Quote ###################################





################################## Trade Execute in Live Market ######################################


while True:
    time.sleep(60)

    ohlc_quote = account.get_quote(instrument_key='NSE_FO|36612', interval='I1')
    candles_data = ohlc_quote.get('data', {}).get('NSE_FO|36612', {}).get('ohlc', {})

    candles_data = ['NSE_FO|36612', time.time(), candles_data.get('open'), candles_data.get('high'), candles_data.get('low'), candles_data.get('close')]

    df = pd.DataFrame(candles_data, columns=['Instrument', 'Timestamp', 'Open', 'High', 'Low', 'Close'])
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])

    df = trade.calculate_technicals(data=df)

    signals = trade.generate_signals(data=df)

    P_E_SL_T = trade.execute_orders(data=df, signals=signals)


