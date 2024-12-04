from get_data import get_tickers

import json
import requests
import jwt
import hashlib
import os
import requests
import uuid
from pprint import pprint
from urllib.parse import urlencode, unquote
from math import floor

with open('settings.json', 'r') as file:
        settings = json.load(file)
num_of_alts = settings['num_of_alts']
input_krw = settings['input_krw'] * (1 - 0.0005)
amount_krw = floor(input_krw / num_of_alts)

access_key = os.environ['UPBIT_OPEN_API_ACCESS_KEY']
secret_key = os.environ['UPBIT_OPEN_API_SECRET_KEY']
# server_url = os.environ['UPBIT_OPEN_API_SERVER_URL']
server_url = "https://api.upbit.com"

ticker_data = get_tickers()

for ticker, value in ticker_data.items():
    params = {
    'market': ticker,
    'side': 'bid', # buy
    'ord_type': 'limit',
    'price': value['trade_price'], # current price
    'volume': amount_krw/value['trade_price']
    }
    pprint(params)
    # continue
    query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, secret_key)
    authorization = 'Bearer {}'.format(jwt_token)
    headers = {
    'Authorization': authorization,
    }

    res = requests.post(server_url + '/v1/orders', json=params, headers=headers)
    # pprint(res.json())
    code = res.status_code
    if code != 201:
        print(f"Error({code}): {ticker}\n")
    else:
         print(f"OK({code}): {ticker}\n")


with open('alt_list.txt', 'w') as file:
    for key in ticker_data.keys():
        file.write(key + '\n')