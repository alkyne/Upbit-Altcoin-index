import jwt
import json
import hashlib
import sys
import os
import requests
import uuid
from pprint import pprint
from urllib.parse import urlencode, unquote

access_key = os.environ['UPBIT_OPEN_API_ACCESS_KEY']
secret_key = os.environ['UPBIT_OPEN_API_SECRET_KEY']
server_url = "https://api.upbit.com"

with open('settings.json', 'r') as file:
    settings = json.load(file)
exclude_pairs = settings['exclude_pairs']

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
    # return res.raise_for_status()

    # if print_status == True:
    #     for x in res.json():
    #         if f"{x['unit_currency']}-{x['currency']}" in alt_list:
    #             pprint(x)

    return res.json()

# Function to get all open orders
def get_open_orders():
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
    res.raise_for_status()  # Raise an exception for HTTP errors
    return res.json()

if __name__ == "__main__":
    # print (f"python3 {os.path.basename(__file__)} {{locked}}")
    # res_json = get_account_balance()

    # if "locked" in sys.argv:
    #     for x in res_json:
    #         if float(x['locked']) > 0:
    #             print (f"{x['unit_currency']}-{x['currency']}")
    #             pprint(x)
    #             print()
    # else:        
    #     pprint(res_json)

    print("======== open orders ========")
    open_orders_json = get_open_orders()
    for order in open_orders_json:
        # if order['application_name'] == 'ios':
        if "api" not in order['application_name']:
            continue
        ticker = order['market']
        side = order['side']
        locked = order['locked']
        volume = order['volume']
        remaining_volume = order['remaining_volume']
        print(f"[{side}] {ticker}: Locked: {locked}, Volume: {volume}, Remaining Volume: {remaining_volume}")
