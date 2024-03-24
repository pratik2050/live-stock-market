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
def fetch_historical_data(instrument_key, interval, to_date, from_data):
    url = "https://api.upstox.com/v2/historical-candle/{instrument_key}/{interval}/{to_date}/{from_date}"

    instrument_key = instrument_key  ### NSE_FO|36611 -> BANKNIFTY24MARFUT
    interval = interval
    to_date = to_date
    from_date = from_data

    url = url.format(instrument_key=instrument_key, interval=interval, to_date=to_date, from_date=from_date)
    
    headers = {
        'Accept': 'application/json'
    }

    response = requests.request("GET", url, headers=headers)

    return response.json()



##################################### Wite to Json ###################################
def write_json(data):
    data = {
        "entry_price": data[0],
        "stop_loss_price": data[1],
        "target_price": data[2],
        "position": data[3]
    }

    output_file_path = 'ohlc.json'
    with open(output_file_path, 'w') as f:
        json.dump(data, f, indent=4)



################################### Function to fetch OHLC Data ################################
def get_ohlc_quote(instrument_key, interval):
    configure_token()
    print(access_token)

    url = 'https://api.upstox.com/v2/market-quote/ohlc'
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + access_token
    }

    data = {
        "instrument_key": instrument_key,
        "interval": interval
    }

    response = requests.request("GET", url, headers=headers, params=data)
    response = response.json()

    return response.get('data', {})
