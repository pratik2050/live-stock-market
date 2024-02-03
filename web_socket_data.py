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
from time import sleep
import datetime


### Creating XLSX Records ###

headers = ['Instrument', 'LTP', 'Volume', 'High', 'Low']
workbook = xw.Book('TickData.xlsx')
worksheet = workbook.sheets[0]

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
                "instrumentKeys": [ "NSE_EQ|INE742F01042",
    "NSE_EQ|INE029A01011",
    "NSE_EQ|INE752E01010",
    "NSE_EQ|INE158A01026",
    # "NSE_EQ|INE361B01024",
    # "NSE_EQ|INE002A01018",
    # "NSE_EQ|INE009A01021",
    # "NSE_EQ|INE213A01029",
    # "NSE_EQ|INE214T01019",
    # "NSE_EQ|INE090A01021",
    # "NSE_EQ|INE669C01036",
    # "NSE_EQ|INE467B01029",
    # "NSE_EQ|INE081A01020",
    # "NSE_EQ|INE522F01014",
    # "NSE_EQ|INE733E01010",
    # "NSE_EQ|INE918I01026",
    # "NSE_EQ|INE192A01025",
    # "NSE_EQ|INE123W01016",
    # "NSE_EQ|INE423A01024",
    # "NSE_EQ|INE075A01022",
    # "NSE_EQ|INE481G01011",
    # "NSE_EQ|INE019A01038",
    # "NSE_EQ|INE155A01022",
    # "NSE_EQ|INE917I01010",
    # "NSE_EQ|INE047A01021",
    # "NSE_EQ|INE437A01024",
    # "NSE_EQ|INE239A01024",
    # "NSE_EQ|INE296A01024",
    # "NSE_EQ|INE038A01020",
    # "NSE_EQ|INE101A01026",
    # "NSE_EQ|INE059A01026",
    # "NSE_EQ|INE089A01023",
    # "NSE_EQ|INE860A01027",
    # "NSE_EQ|INE628A01036",
    # "NSE_EQ|INE021A01026",
    # "NSE_EQ|INE044A01036",
    # "NSE_EQ|INE154A01025",
    # "NSE_EQ|INE040A01034",
    # "NSE_EQ|INE216A01030",
    # "NSE_EQ|INE095A01012",
    # "NSE_EQ|INE237A01028",
    # "NSE_EQ|INE280A01028",
    # "NSE_EQ|INE397D01024",
    # "NSE_EQ|INE018A01030",
    # "NSE_EQ|INE062A01020",
    # "NSE_EQ|INE030A01027",
    # "NSE_EQ|INE238A01034",
    "NSE_EQ|INE795G01014",
    "NSE_EQ|INE585B01010",
    "NSE_EQ|INE066A01021"]
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

sleep(5)

while True:
    sleep(1)

    data = (MessageToDict(decoded_data))

    for instrument, values in data.get('feeds', {}).items():
        # Extract values for each instrument
        ltp = values.get('ff', {}).get('marketFF', {}).get('ltpc', {}).get('ltp', '')
                
        ohlc_data = values.get('ff', {}).get('marketFF', {}).get('marketOHLC', {}).get('ohlc', [])
        volume = ohlc_data[0].get('volume', '') if ohlc_data else ''
                
        high_price = ohlc_data[0].get('high', '') if ohlc_data else ''
        low_price = ohlc_data[0].get('low', '') if ohlc_data else ''
                

        # Append data to the DataFrame
        data_dict = data_dict._append({
            'Instrument': instrument,
            'LTP': ltp,
            'Volume': volume,
            'High': high_price,
            'Low': low_price
        }, ignore_index=True)

        # Update the Excel file with the DataFrame
        worksheet.range('A1').value = data_dict
    