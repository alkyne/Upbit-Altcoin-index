import jwt
import hashlib
import os
import requests
import uuid
import time
import json
from pprint import pprint
from urllib.parse import urlencode, unquote
from get_data import get_tickers
from concurrent.futures import ThreadPoolExecutor, as_completed
from cancel_open_orders import cancel_orders_in_markets
import sys

from settings import *

########### get account balance ###########
def get_account_balance(print_status=False):
    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
    }

    jwt_token = jwt.encode(payload, secret_key)
    authorization = 'Bearer {}'.format(jwt_token)
    headers = {
        'Authorization': authorization,
    }

    res = requests.get(server_url + '/v1/accounts', headers=headers)
    res.raise_for_status()

    return res.json()

############# SELL #########
def _place_limit_sell_order(ticker, volume, price):

    # print(f"sell order is called: {ticker}, {volume}, {price}")
    query = {
        'market': ticker,
        'side': 'ask',            # 'ask' for sell orders
        'volume': volume,         # Quantity to sell
        'price': price,           # Price per unit
        'ord_type': 'limit',      # Limit order
    }
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, secret_key, algorithm='HS256')
    headers = {
        'Authorization': f'Bearer {jwt_token}',
    }

    res = requests.post(f"{server_url}/v1/orders", params=query, headers=headers)
    code = res.status_code
    print(f"Placing ask order for {ticker}: {volume} at {price}...")
    # return 1, 2
    return code, res.text

def place_limit_sell_orders():
    account_balances = get_account_balance()
    balance_dict = {f"{item['unit_currency']}-{item['currency']}": item for item in account_balances}
    # print(f"balance_dict: {balance_dict}")
    # input()
    # {'KRW-BTC': {'currency': 'BTC', 'balance': '0.00514087', 'locked': '0', 'avg_buy_price': '132992558.1098141', 'avg_buy_price_modified': False, 'unit_currency': 'KRW'}, 'KRW-KRW': {'currency': 'KRW', 'balance': '461.37533087', 'locked': '0', 'avg_buy_price': '0', 'avg_buy_price_modified': True, 'unit_currency': 'KRW'}, 'KRW-WAVES': {'currency': 'WAVES', 'balance': '11.91475998', 'locked': '0', 'avg_buy_price': '2229', 'avg_buy_price_modified': False, 'unit_currency': 'KRW'}}

    ticker_list = list(balance_dict.keys())

    error_list = []
    ok_list = []

    # Run the sell orders concurrently
    chunk_size = 8
    i = 0
    while i < len(ticker_list):

        ticker_list_batch = ticker_list[i:i+chunk_size] # slice key(tickers)

        ticker_data = get_tickers() # to get trade_price
        batch = {key: ticker_data[key]['trade_price'] for key in ticker_list_batch if key in ticker_data}
        # print (f"batch {i}:")
        # print (batch)
        # {'KRW-AGLD': 2731.0, 'KRW-UXLINK': 2130.0, 'KRW-DOGE': 483.4, 'KRW-CTC': 2060.0, 'KRW-HIVE': 526.6, 'KRW-STRAX': 120.2, 'KRW-ONDO': 2549.0, 'KRW-DRIFT': 1689.0}

        with ThreadPoolExecutor(max_workers=chunk_size) as executor:
            future_to_ticker = {
                executor.submit(
                    _place_limit_sell_order, 
                    ticker, 
                    balance_dict[ticker]['balance'],
                    trade_price, # current price
                ): ticker
                for ticker, trade_price in batch.items()
            }

            # print (future_to_ticker)
            # input()
            # {<Future at 0x1037baab0 state=finished raised TypeError>: 'KRW-AGLD'}
            # {<Future at 0x105022630 state=running>: 'KRW-ATH'}
            
            for future in as_completed(future_to_ticker):
                ticker = future_to_ticker[future]

                try:
                    code, text = future.result()
                    if code != 201:
                        error_list.append(ticker)
                        print (f"{ticker} error: {text}")
                    else:
                        ok_list.append(ticker)
                except Exception as e:
                    error_list.append(ticker)
                    # Print exception if you'd like more info
                    print(f"Exception for {ticker}: {e}")

        i += chunk_size
        if i < len(ticker_list):
            # Sleep for 1 second after every 8 completed tasks
            time.sleep(1)
            print()

    print("Completed concurrent sell orders.")
    print("Success:", ok_list)
    print("Errors:", error_list)

if __name__ == '__main__':
    ans = input("\nSell all? (y/n)")

    if ans != 'y':
        print('bye')
        sys.exit(0)
    cancel_orders_in_markets(_side="ask") # unlock all assets first
    place_limit_sell_orders()