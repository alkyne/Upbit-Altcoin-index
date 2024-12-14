import sys, os
from math import floor
import uuid
import jwt
import hashlib
import requests
from urllib.parse import urlencode, unquote
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from get_data import get_tickers
from check_settings import print_settings

with open('settings.json', 'r') as file:
    settings = json.load(file)
num_of_alts = settings['num_of_alts']
input_krw = settings['input_krw'] * (1 - 0.0005)
krw_per_ticker = floor(input_krw / num_of_alts)

access_key = os.environ['UPBIT_OPEN_API_ACCESS_KEY']
secret_key = os.environ['UPBIT_OPEN_API_SECRET_KEY']
# server_url = os.environ['UPBIT_OPEN_API_SERVER_URL']
server_url = "https://api.upbit.com"

def process_order(ticker, value, access_key, secret_key, server_url, krw_per_ticker):
    if value['trade_price'] <= 0:
        return ticker, 500
    params = {
        'market': ticker,
        'side': 'bid', # buy
        'ord_type': 'limit',
        'price': value['trade_price'], # current price
        'volume': krw_per_ticker/value['trade_price']
    }
    
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
    authorization = f'Bearer {jwt_token}'
    headers = {'Authorization': authorization}

    # Perform the real buy order
    res = requests.post(server_url + '/v1/orders', json=params, headers=headers)
    code = res.status_code
    return ticker, code

if __name__ == '__main__':
    print("==== settings ====")
    print_settings()
    ans = input("\ncontinue? (y/n)")

    if ans != 'y':
        print('bye')
        sys.exit(0)

    error_list = []
    ok_list = []


    # Extract only the first 'num_of_alts' items
    ticker_data = get_tickers()
    items = list(ticker_data.items())[:num_of_alts]

    # Run the orders concurrently
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_ticker = {
            executor.submit(
                process_order, 
                ticker, 
                value, 
                access_key, 
                secret_key, 
                server_url, 
                krw_per_ticker
            ): ticker
            for ticker, value in items
        }

        count = 0
        for future in as_completed(future_to_ticker):
            ticker = future_to_ticker[future]
            try:
                ticker_result, code = future.result()
                if code != 201:
                    error_list.append(ticker_result)
                else:
                    ok_list.append(ticker_result)
            except Exception as e:
                error_list.append(ticker)
                # Print exception if you'd like more info
                print(f"Exception for {ticker}: {e}")

            count += 1
            if count % 8 == 0:
                # Sleep for 1 second after every 8 completed tasks
                time.sleep(1)

    # Write successful tickers to file
    with open('alt_list.txt', 'w') as file:
        for ticker in ok_list:
            file.write(ticker + '\n')

    print(f"error list: {error_list}")