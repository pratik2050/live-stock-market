import pandas as pd

import market_ohlc as ohlc
import trade_logic as trade



####################################### Configure access_token ##########################################
def configure_token():
    global access_token
    filename =f"accessToken.txt"
    with open(filename,"r") as file:
        access_token = file.read()



######################################### Back Test with data Data ################################################
instrument_key = 'NSE_FO|36611'
interval = '30minute'
to_date = '2024-03-03'
from_date = '2024-01-01'


def test():
    data = ohlc.fetch_historical_data(instrument_key=instrument_key, interval=interval, to_date=to_date, from_data=from_date)
    data = data['data']['candles']

    df = pd.DataFrame(data, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Vol', 'Extra'])

    df = trade.calculate_technicals(df)

    signals = trade.generate_signals(df)
    
    entry_price = None
    position = None
    stop_loss_price = None
    target_price = None
    prev_time = 0

    res = trade.execute_orders(data=df, signals=signals, position=position, entry_price=entry_price, stop_loss_price=stop_loss_price, target_price=target_price, prev_time=prev_time)
  
    position = res[0]
    entry_price = res[1]
    stop_loss_price = res[2]
    target_price = res[3]
    prev_time = res[4]


if __name__ == '__main__':
    configure_token()

    test()