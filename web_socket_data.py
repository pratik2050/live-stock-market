# Import necessary modules
import pandas as pd
import xlwings as xw
import asyncio
import json
import ssl
import upstox_client
import websockets
from google.protobuf.json_format import MessageToDict
from threading import Thread
import MarketDataFeed_pb2 as pb
import time
import requests


### Creating XLSX Records ###

headers = ['Instrument', 'LTP', 'High', 'Low']
workbook = xw.Book('TickData.xlsx')
worksheet = workbook.sheets[0]

ohlc_time = time.time()
ohlc_data = ''
high_price = ''
low_price = ''
open_price = ''
close_price = ''

filename =f"accessToken.txt"
with open(filename,"r") as file:
    access_token = file.read()

def get_market_data_feed_authorize(api_version, configuration):
    """Get authorization for market data feed."""
    api_instance = upstox_client.WebsocketApi(
        upstox_client.ApiClient(configuration))
    api_response = api_instance.get_market_data_feed_authorize(api_version)
    return api_response


def decode_protobuf(buffer):
    """Decode protobuf message."""
    feed_response = pb.FeedResponse()
    feed_response.ParseFromString(buffer)
    return feed_response


async def fetch_market_data():
    global data_dict, decoded_data
    """Fetch market data using WebSocket and print it."""

    # Create default SSL context
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    # Configure OAuth2 access token for authorization
    configuration = upstox_client.Configuration()

    api_version = '2.0'
    configuration.access_token = access_token

    # Get market data feed authorization
    response = get_market_data_feed_authorize(
        api_version, configuration)

    # Connect to the WebSocket with SSL context
    async with websockets.connect(response.data.authorized_redirect_uri, ssl=ssl_context) as websocket:
        print('Connection established')

        await asyncio.sleep(1)  # Wait for 1 second

        # Data to be sent over the WebSocket
        data = {
            "guid": "someguid",
            "method": "sub",
            "data": {
                "mode": "full",
                "instrumentKeys": [ "NSE_INDEX|Nifty Bank" ]
            }
        }

        # Convert data to binary and send over WebSocket
        binary_data = json.dumps(data).encode('utf-8')
        await websocket.send(binary_data)

        # Continuously receive and decode data from WebSocket
        while True:
            message = await websocket.recv()
            decoded_data = decode_protobuf(message)

            # Convert the decoded data to a dictionary
            # data_dict = MessageToDict(decoded_data)
            data_dict = pd.DataFrame(columns=headers)

            # Print the dictionary representation
            # print(json.dumps(data_dict))


# Execute the function to fetch market data
# asyncio.run(fetch_market_data())
def run_websocket():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(fetch_market_data())

# Start the WebSocket connection in a separate thread
websocket_thread = Thread(target=run_websocket)
websocket_thread.start()

time.sleep(5)

while True:
    time.sleep(1)

    data = (MessageToDict(decoded_data))

    for instrument, values in data.get('feeds', {}).items():
        # Extract values for each instrument
        ltp = values.get('ff', {}).get('indexFF', {}).get('ltpc', {}).get('ltp', '')
        
        if time.time() - ohlc_time >= 15:
            ohlc_data = values.get('ff', {}).get('indexFF', {}).get('marketOHLC', {}).get('ohlc', [])
            open_price = ohlc_data[0].get('open', '') if ohlc_data else ''
            high_price = ohlc_data[0].get('high', '') if ohlc_data else ''
            low_price = ohlc_data[0].get('low', '') if ohlc_data else ''
            close_price = ohlc_data[0].get('close', '') if ohlc_data else ''

            ohlc_time = time.time()
                

        # Append data to the DataFrame
        data_dict = data_dict._append({
            'Instrument': instrument,
            'LTP': ltp,
            'Open': open_price,
            'High': high_price,
            'Low': low_price,
            'Close': close_price
        }, ignore_index=True)

        # Update the Excel file with the DataFrame
        worksheet.range('A1').value = data_dict
    