# Market RTD Information
## About
This application authenticates with the indian stock market(BSE/NSE) to get the index of each one in real time and writes those in an excel file with real time update. The data also contains OHLC information that can be adjusted with intervals as per the users concern.

NOTE: You need to have one account in Upstox of your own to use this

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

### Getting Live Feed
First Run `auth.py` to get `accessToken.txt` file.

Live Feed can be activated by running `web_socket_data.py`.

To get life feed of desired instrument change the instrument key at line 98 in `web_socket_data.py`

By Default the OHLC Data will update with interval of 15 seconds and Live tick of ltp will be in real time. 

OHLC Interval can be adjusted at line no 139.






