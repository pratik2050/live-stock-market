# Import necessary modules
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


### Creating XLSX Records ###

headers = ['Time', 'Instrument', 'Open', 'High', 'Low', 'Close']

workbookBNF = xw.Book('BankNifty.xlsx')
worksheetBNF = workbookBNF.sheets[0]

workbookNifty = xw.Book('Nifty.xlsx')
worksheetNifty = workbookNifty.sheets[0]

ohlc_time = time.time()
Bohlc_data = ''
Bhigh_price = ''
Blow_price = ''
Bopen_price = ''
Bclose_price = ''

Nohlc_data = ''
Nhigh_price = ''
Nlow_price = ''
Nopen_price = ''
Nclose_price = ''

currRow = 2

worksheetBNF.range('A1').value = ['LTP']
worksheetBNF.range('B1').value = ['Time', 'Instrument', 'Open', 'High', 'Low', 'Close']

worksheetNifty.range('A1').value = ['LTP']
worksheetNifty.range('B1').value = ['Time', 'Instrument', 'Open', 'High', 'Low', 'Close']


### Web Socket Configuration ###

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
                "instrumentKeys": [ "NSE_INDEX|Nifty Bank", "NSE_INDEX|Nifty 50" ]  # Add intruments as per your need
            }
        }

        # Convert data to binary and send over WebSocket
        binary_data = json.dumps(data).encode('utf-8')
        await websocket.send(binary_data)

        # Continuously receive and decode data from WebSocket
        while True:
            message = await websocket.recv()
            decoded_data = decode_protobuf(message)

def run_websocket():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(fetch_market_data())

# Start the WebSocket connection in a separate thread
websocket_thread = Thread(target=run_websocket)
websocket_thread.start()


time.sleep(5)


### Getting Continuous Data with 1 Second Interval ###

while True:
    time.sleep(1)

    data = (MessageToDict(decoded_data))

    feed = data.get('feeds', {})

    bankFeed = feed.get('NSE_INDEX|Nifty Bank', {})
    niftyFeed = feed.get('NSE_INDEX|Nifty 50', {})

    worksheetBNF.range('A2').value = bankFeed.get('ff', {}).get('indexFF', {}).get('ltpc', {}).get('ltp', '')
    worksheetNifty.range('A2').value = niftyFeed.get('ff', {}).get('indexFF', {}).get('ltpc', {}).get('ltp', '')

    if time.time() - ohlc_time >= 15:       # 15 means 15 seconds, adjust as per your need
        Bohlc_data = bankFeed.get('ff', {}).get('indexFF', {}).get('marketOHLC', {}).get('ohlc', [])
        Bopen_price = Bohlc_data[0].get('open', '') if Bohlc_data else ''
        Bhigh_price = Bohlc_data[0].get('high', '') if Bohlc_data else ''
        Blow_price = Bohlc_data[0].get('low', '') if Bohlc_data else ''
        Bclose_price = Bohlc_data[0].get('close', '') if Bohlc_data else ''

        worksheetBNF.range('B' + str(currRow)).value = [time.time(), 'Bank Nifty', Bopen_price, Bhigh_price, Blow_price, Bclose_price]

        Nohlc_data = niftyFeed.get('ff', {}).get('indexFF', {}).get('marketOHLC', {}).get('ohlc', [])
        Nopen_price = Nohlc_data[0].get('open', '') if Nohlc_data else ''
        Nhigh_price = Nohlc_data[0].get('high', '') if Nohlc_data else ''
        Nlow_price = Nohlc_data[0].get('low', '') if Nohlc_data else ''
        Nclose_price = Nohlc_data[0].get('close', '') if Nohlc_data else ''

        worksheetNifty.range('B' + str(currRow)).value = [time.time(), 'Nifty 50', Nopen_price, Nhigh_price, Nlow_price, Nclose_price]

        ohlc_time = time.time()
        currRow += 1
