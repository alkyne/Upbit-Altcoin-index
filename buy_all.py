from get_data import get_tickers
from check_settings import print_settings

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
import sys

with open('settings.json', 'r') as file:
    settings = json.load(file)
num_of_alts = settings['num_of_alts']
input_krw = settings['input_krw'] * (1 - 0.0005)
krw_per_ticker = floor(input_krw / num_of_alts)

access_key = os.environ['UPBIT_OPEN_API_ACCESS_KEY']
secret_key = os.environ['UPBIT_OPEN_API_SECRET_KEY']
# server_url = os.environ['UPBIT_OPEN_API_SERVER_URL']
server_url = "https://api.upbit.com"

if __name__ == '__main__':
    print("==== settings ====")
    print_settings()
    ans = input("\ncontinue? (y/n)")

    if ans != 'y':
        print('bye')
        sys.exit(0)

    error_list = []
    ok_list = []

    ticker_data = get_tickers()

    for i, (ticker, value) in enumerate(ticker_data.items()):
        if i >= num_of_alts:  # Stop after 'num_of_alts' iterations
            break
        
        params = {
            'market': ticker,
            'side': 'bid', # buy
            'ord_type': 'limit',
            'price': value['trade_price'], # current price
            'volume': krw_per_ticker/value['trade_price']
        }
        # pprint(params)
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
        headers = {'Authorization': authorization}

        # real buy order here !!
        res = requests.post(server_url + '/v1/orders', json=params, headers=headers)
        # pprint(res.json())
        code = res.status_code
        if code != 201:
            # print(f"Error({code}): {ticker}\n")
            error_list.append(ticker)
        else:
            # print(f"OK({code}): {ticker}\n")
            ok_list.append(ticker)

    with open('alt_list.txt', 'w') as file:
        for ticker in ok_list:
            file.write(ticker + '\n')

    print(f"error list: {error_list}")