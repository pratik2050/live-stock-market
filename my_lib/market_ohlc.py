import requests
import json
import os


################################################ Configure access_token ###########################################
def configure_token():
    current_directory = os.getcwd()
    file_path = os.path.join(current_directory, "accessToken.txt")

    global access_token
    with open(file_path, "r") as file:
        access_token = file.read()


######################################### Function to fetch historical data ######################################
def fetch_historical_data(ticker_key):
    url = "https://api.upstox.com/v2/historical-candle/{instrument_key}/{interval}/{to_date}/{from_date}"

    instrument_key = ticker_key  ### NSE_FO|36611 -> BANKNIFTY24MARFUT
    interval = '30minute'
    to_date = '2024-03-06'
    from_date = '2024-02-01'

    url = url.format(instrument_key=instrument_key, interval=interval, to_date=to_date, from_date=from_date)
    
    headers = {
        'Accept': 'application/json'
    }

    response = requests.request("GET", url, headers=headers)

    return response.json()



##################################### Wite to Json ###################################
def write_json(data, instument_key):
    last_price = data['data'][instument_key]['last_price']
    instrument_token = data['data'][instument_key]['instrument_token']
    ohlc_data = data['data'][instument_key]['ohlc']

    output_data = {
        'last_price': last_price,
        'instrument_token': instrument_token,
        'ohlc': ohlc_data
    }

    output_file_path = 'ohlc.json'
    with open(output_file_path, 'w') as f:
        json.dump(output_data, f, indent=4)



################################### Function to fetch OHLC Data ################################
def get_ohlc_quote(instrument_key, interval):
    configure_token()

    url = 'https://api.upstox.com/v2/market-quote/ohlc'
    headers = {
        'Accept': 'application/json',
        'Authorization': access_token 
    }

    data = {
        "instrument_key": instrument_key,
        "interval": interval
    }

    response = requests.request("GET", url, headers=headers, params=data)
    print (response)
    response = response.json()

    write_json(data=response, instument_key=instrument_key)


get_ohlc_quote(instrument_key='NSE_FO|36612', interval='I1')