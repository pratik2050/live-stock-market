import requests


####################################### Configure access_token ##########################################
def configure_token():
    global access_token
    filename =f"accessToken.txt"
    with open(filename,"r") as file:
        access_token = file.read()



########################################### Function to Get Postion of account #################################################
def get_position():
    configure_token()
    url = 'https://api.upstox.com/v2/portfolio/short-term-positions'
    headers = {
        'Accept': 'application/json',
        'Authorization': access_token
    }

    response = requests.request("GET", url, headers=headers)

    return response.json()



################################################ Function to Place Order #####################################################
def place_order(instrument_key, order_type, transaction_type, stop_loss):
    configure_token()
    url = 'https://api.upstox.com/v2/order/place'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': access_token,
    }

    data = {
        'quantity': 75,
        'product': 'D',
        'validity': 'DAY',
        'price': 0.0,
        'tag': 'string',
        'instrument_token': instrument_key,
        'order_type': order_type,
        'transaction_type': transaction_type,
        'disclosed_quantity': 0,
        'trigger_price': stop_loss,
        'is_amo': False,
    }

    response = requests.request("POST", url, headers=headers, json=data)

    return response.json()



# def back_test():
#     data = fetch_data(ticker_key='NSE_FO|36611')
#     data = data['data']['candles']

#     df = pd.DataFrame(data, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Vol', 'Extra'])
#     df['Timestamp'] = pd.to_datetime(df['Timestamp'])

#     df = calculate_technicals(df)

#     signals = generate_signals(df)

#     res = execute_orders(data=df, signals=signals)
#     print(sum(res))