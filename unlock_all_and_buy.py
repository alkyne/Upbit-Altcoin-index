import jwt
import hashlib
import os
import requests
import json
import uuid
import sys

from math import floor
from pprint import pprint
from urllib.parse import urlencode, unquote
from get_data import get_tickers

from settings import *

# Function to get all open orders
def _get_open_orders():
    query = {
        'state': 'wait',  # 'wait' indicates orders waiting to be executed
    }
    query_string = urlencode(query)
    m = hashlib.sha512()
    m.update(query_string.encode())
    query_hash = m.hexdigest()

    # Create JWT payload
    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    # Generate JWT token
    jwt_token = jwt.encode(payload, secret_key, algorithm='HS256')
    headers = {
        'Authorization': f'Bearer {jwt_token}',
    }

    # Send GET request to retrieve open orders
    res = requests.get(f"{server_url}/v1/orders", params=query, headers=headers)
    # return res.status_code
    if 400 <= res.status_code < 500:
        assert False, f"{res.status_code} error occurred. | Response: {res.text}"
    res.raise_for_status()  # Raise an exception for HTTP errors
    return res.json()

# Function to cancel an order by UUID
def _cancel_order(order_uuid):
    query = {
        'uuid': order_uuid,
    }
    query_string = urlencode(query)
    m = hashlib.sha512()
    m.update(query_string.encode())
    query_hash = m.hexdigest()

    # Create JWT payload
    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    # Generate JWT token
    jwt_token = jwt.encode(payload, secret_key, algorithm='HS256')
    headers = {
        'Authorization': f'Bearer {jwt_token}',
    }

    # Send DELETE request to cancel the order
    res = requests.delete(f"{server_url}/v1/order", params=query, headers=headers)
    res.raise_for_status()  # Raise an exception for HTTP errors
    return res.status_code

# Main logic to cancel open orders in specified markets
def cancel_orders_in_markets():
    cancel_ticker_list = []

    try:
        open_orders = _get_open_orders()
        if not open_orders:
            print("No open orders to cancel.")
            return []

        # Filter orders to only include those in specified markets
        orders_to_cancel = [order for order in open_orders if order['market'] not in exclude_pairs]

        if not orders_to_cancel:
            print("No open orders to cancel.")
            return []
        
        for order in orders_to_cancel:
            side = order['side'] # bid or ask
            # bid only
            if side == 'ask':
                continue
            order_uuid = order['uuid']
            market = order['market'] # ticker
            volume = order['remaining_volume']
            price = order['price']
            cancel_status_code = _cancel_order(order_uuid)
            if cancel_status_code == 200:
                print(f"{market}: side={side}, volume={volume}, price={price}")
                cancel_ticker_list += market
            else:
                print(f"Order Cancel Error({cancel_status_code}): {market}\n")
        print("All specified orders have been cancelled.")
    except requests.exceptions.HTTPError as err:
        error_msg = err.response.json()
        print(f"HTTP error occurred: {error_msg}")
    except Exception as e:
        print(f"cancel_orders_in_markets: An error occurred: {e}")

    return cancel_ticker_list

def buy_crypto(cancel_ticker_list):

    error_list = []
    ok_list = []

    ticker_data = get_tickers()

    # for ticker, value in enumerate(ticker_data.items()):
    for ticker in cancel_ticker_list:
        value = ticker_data[ticker]
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

    print()
    print(f"ok list: {ok_list}")
    print(f"error list: {error_list}")

if __name__ == '__main__':
    cancel_ticker_list = cancel_orders_in_markets() # unlock all assets first
    print (f"cancel list: {cancel_ticker_list}")
    print ("====== cancel end ======\n")

    if len(cancel_ticker_list) == 0:
        print("nothing to cancel")
        sys.exit(0)
    
    print("====== Re-order start ======\n")
    buy_crypto(cancel_ticker_list)