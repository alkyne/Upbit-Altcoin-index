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

with open('settings.json', 'r') as file:
    settings = json.load(file)
exclude_pairs = settings['exclude_pairs']

access_key = os.environ['UPBIT_OPEN_API_ACCESS_KEY']
secret_key = os.environ['UPBIT_OPEN_API_SECRET_KEY']
server_url = "https://api.upbit.com"

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
    if 400 <= res.status_code < 500:
        assert False, f"{res.status_code} error occurred. | Response: {res.text}"
    res.raise_for_status()  # Raise an exception for HTTP errors
    return res.json()

def cancel_orders_in_markets(_side="all"):
    try:
        open_orders = _get_open_orders()
        if not open_orders:
            print("No open orders to cancel.")
            return

        # Filter orders to only include those in specified markets
        orders_to_cancel = [order for order in open_orders if order['market'] in alt_list]

        if not orders_to_cancel:
            # print("No open orders found in the specified markets.")
            return  

        for order in orders_to_cancel:
            side = order['side'] # bid or ask

            if _side == "all":
                pass
            elif _side != side:
                continue
            order_uuid = order['uuid']
            market = order['market']
            volume = order['remaining_volume']
            price = order['price']
            cancel_result = _cancel_order(order_uuid)
            print(f"Cancelled order {order_uuid} in market {market}: side={side}, volume={volume}, price={price}")
        print("All specified orders have been cancelled.")
    except requests.exceptions.HTTPError as err:
        error_msg = err.response.json()
        print(f"HTTP error occurred: {error_msg}")
    except Exception as e:
        print(f"cancel_orders_in_markets: An error occurred: {e}")

if __name__ == "__main__":

    print(f"Usage: python3 {os.path.basename(__file__)} {{all|bid|ask}}")
    
    side = "all"

    if "bid" in sys.argv:
        side = "bid"
    elif "ask" in sys.argv:
        side = "ask"

    cancel_orders_in_markets(_side=side)
