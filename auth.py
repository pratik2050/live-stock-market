import requests as rq
from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import urllib.parse as urlparse
from pyotp import TOTP
import json


#### Login Credentials ####

json_data = 123
with open('credentials.json', 'r') as json_file:
    json_data = json.load(json_file)

api_key = json_data.get('api_key')
secret_key = json_data.get('secret_key')
r_url = json_data.get('r_url')
totp_key = json_data.get('totp_key') 
mobile_no = json_data.get('mobile_no')
pin = json_data.get('pin')

auth_url = f'https://api-v2.upstox.com/login/authorization/dialog?response_type=code&client_id={api_key}&redirect_uri={r_url}'

#https://api-v2.upstox.com/login/authorization/dialog?response_type=code&client_id=cddff55d-5354-47d0-86e1-29a4f89c24ab&redirect_uri=https://127.0.0.1:5000/

sleep(1)

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
# options.add_argument('--headless')
driver = webdriver.Chrome(options=options)
driver.get(auth_url)
wait = WebDriverWait(driver,3)
wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="text"]'))).send_keys(mobile_no)
wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="getOtp"]'))).click()

totp = TOTP(totp_key).now()
sleep(2)

wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="otpNum"]'))).send_keys(totp)
wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="continueBtn"]'))).click()

sleep(2)

wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="pinCode"]'))).send_keys(pin)
wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="pinContinueBtn"]'))).click()

sleep(2)

token_url = driver.current_url
parsed = urlparse.urlparse(token_url)
driver.close()

code = urlparse.parse_qs(parsed.query)['code'][0]
url = 'https://api-v2.upstox.com/login/authorization/token'
headers = {
    'accept': 'application/json',
    'Api-Version': '2.0',
    'Content-Type': 'application/x-www-form-urlencoded'}

data = {
    'code': code,
    'client_id': api_key,
    'client_secret': secret_key,
    'redirect_uri': r_url,
    'grant_type': 'authorization_code'}

response = rq.post(url, headers=headers, data=data)
jsr = response.json()

with open('accessToken.txt','w') as file:
    file.write(jsr['access_token'])

