import jwt
import hashlib
import os
import requests
import uuid
import json
from pprint import pprint
from urllib.parse import urlencode, unquote
from get_data import get_tickers
import sys
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
    if 400 <= res.status_code < 500:
        assert False, f"{res.status_code} error occurred. | Response: {res.text}"
    res.raise_for_status()  # Raise an exception for HTTP errors
    return res.json()

# Main logic to cancel open orders in specified markets
def cancel_orders_in_markets():
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
            order_uuid = order['uuid']
            market = order['market']
            side = order['side']
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

    if print_status == True:
        for x in res.json():
            if f"{x['unit_currency']}-{x['currency']}" in alt_list:
                pprint(x)

    return res.json()

############# SELL #########
# Function to place a limit sell order
def _place_limit_sell_order(market, volume, price):
    query = {
        'market': market,
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

    jwt_token = jwt.encode(payload, secret_key)
    headers = {
        'Authorization': f'Bearer {jwt_token}',
    }

    res = requests.post(f"{server_url}/v1/orders", params=query, headers=headers)
    # res.raise_for_status()
    return res.json()

# Main function to place limit sell orders
def place_limit_sell_orders():
    # try:
        account_balances = get_account_balance()
        # Create a mapping from currency code to balance info
        balance_dict = {f"{item['unit_currency']}-{item['currency']}": item for item in account_balances}

        ticker_data = get_tickers()
        for ticker in alt_list:
            if ticker in exclude_pairs:
                continue
            if ticker in balance_dict:
                balance_info = balance_dict[ticker]
                # currency = balance_info['currency']
                available_balance = balance_info['balance']

                # Skip if balance is zero
                if float(available_balance) <= 0:
                    # print(f"No available balance to sell for {ticker}.")
                    continue

                # Get the price for the current market
                # price = prices.get(market)
                price = ticker_data[ticker]['trade_price']
                if not price:
                    print(f"No price specified for {ticker}. Skipping..")
                    continue

                # DEBUG
                # print(f"{ticker}: {price}") 

                # Place the limit sell order
                order_result = _place_limit_sell_order(
                    market=ticker,
                    volume=available_balance,
                    price=price
                )
                print(f"Placed limit sell order for [{ticker}]: {order_result}")
                # pprint(order_result)
            # else:
                # print(f"{ticker} not found in account balances.")
    # except requests.exceptions.HTTPError as err:
    #     error_msg = err.response.json()
    #     print(f"HTTP error occurred: {error_msg}")
    # except Exception as e:
    #     print(f"place_limit_sell_orders: An error occurred: {e}")

if __name__ == '__main__':
    # cancel_orders_in_markets() # unlock all assets first
    ans = input("\nSell all? (y/n)")

    if ans != 'y':
        print('bye')
        sys.exit(0)
        
    place_limit_sell_orders()
    get_account_balance(print_status=True)