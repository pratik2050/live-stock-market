# Market RTD Information
## About
This application authenticates with the indian stock market(BSE/NSE) to get the index of each one in real time and writes those in an excel file with real time update. The data also contains OHLC information that can be adjusted with intervals as per the users concern.

NOTE: You need to have one account in Upstox of your own to use this. This application is version specific you need Python 3.10.11 to execute

## Getting Started
### Setup
``` git clone https://github.com/pratik2050/live-stock-market ```

``` cd live-stock market ```

``` python -m venv venv ```

Change the Interpreter in VS Code ``` ctrl + shift + p ``` and select one under /Scripts/Activate (Recomended).

``` pip install -r requirements.txt ```

Create `credentials.json` and copy the following json and replace the credentails with your own

```
{
    "api_key": "your api key",
    "secret_key" : "your secret key",
    "r_url" : "your redirect url",
    "totp_key" : "your TOTP KEY",
    "mobile_no" : "mobile number",
    "pin" : "your account pin"
}

```

### Use Case
You can set the name of the instrument with whome you want to trade. Set the instrument key at line no 68 on `my_lib/web_socket_data.py` 

Run the main.py to see the trade action in live






