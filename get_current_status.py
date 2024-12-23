import jwt
import json
import hashlib
import sys
import os
import argparse
import requests
import uuid
from pprint import pprint
from urllib.parse import urlencode, unquote
from get_data import get_tickers

from settings import *

pnl_ticker_list = []
holding_ticker_list = []

def _get_account_balance(print_status=False):
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

    # return res.status_code
    if 400 <= res.status_code < 500:
        assert False, f"{res.status_code} error occurred. | Response: {res.text}"

    return res.json()

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
    res.raise_for_status()  # Raise an exception for HTTP errors
    return res.json()

def print_open_orders():
    print("======== open orders ========")
    open_orders_json = _get_open_orders()
    for order in open_orders_json:
        ticker = order['market']
        if ticker in exclude_pairs:
            continue
        application_name = order['application_name']
        ticker = order['market']
        side = order['side']
        locked = order['locked']
        volume = order['volume']
        remaining_volume = order['remaining_volume']
        print(f"[{side}] {ticker}: Locked: {locked}, Volume: {volume}, Remaining Volume: {remaining_volume} ({application_name})")

def print_account_balance():
    global holding_ticker_list
    account_ticker_list = []
    res = _get_account_balance()
    '''
    [{'avg_buy_price': '132992558.1098141',
    'avg_buy_price_modified': False,
    'balance': '0.00514087',
    'currency': 'BTC',
    'locked': '0',
    'unit_currency': 'KRW'},
    {'avg_buy_price': '0',
    'avg_buy_price_modified': True,
    'balance': '26549.37363765',
    'currency': 'KRW',
    'locked': '0',
    'unit_currency': 'KRW'},
    {'avg_buy_price': '2229',
    'avg_buy_price_modified': False,
    'balance': '11.91475998',
    'currency': 'WAVES',
    'locked': '0'}]
    '''

    # pprint(res)

    for x in res:
        ticker = f"{x['unit_currency']}-{x['currency']}"
        if ticker in exclude_pairs:
            continue
        if float(x['balance']) <= 0 or float(x['avg_buy_price']) <= 0:
            continue
        account_ticker_list.append(ticker)
        # print(ticker)

    print("======== Holding alt list ========")
    print(account_ticker_list)
    print(f"num of alt: {len(account_ticker_list)}\n")
    holding_ticker_list = account_ticker_list

def print_pnl(ticker="all"):
    global pnl_ticker_list
    accounts = _get_account_balance()
    # pprint(accounts)
    '''
    [{'avg_buy_price': '132992558.1098141',
    'avg_buy_price_modified': False,
    'balance': '0.00514087',
    'currency': 'BTC',
    'locked': '0',
    'unit_currency': 'KRW'},
    {'avg_buy_price': '0',
    'avg_buy_price_modified': True,
    'balance': '26549.37363765',
    'currency': 'KRW',
    'locked': '0',
    'unit_currency': 'KRW'},
    {'avg_buy_price': '2229',
    'avg_buy_price_modified': False,
    'balance': '11.91475998',
    'currency': 'WAVES',
    'locked': '0'}]
    '''

    # Filter out only currencies that have a non-zero avg_buy_price and non-zero balance (i.e., actual positions)
    # Also skip pure KRW (fiat) since that is just cash holding, not a traded asset

    if ticker != "all":
        traded_positions = [
            acc for acc in accounts 
            if f"{acc['unit_currency']}-{acc['currency']}" == ticker.upper()
        ]
    else:
        traded_positions = [
            acc for acc in accounts
            # if acc['currency'] != 'KRW'
            if f"{acc['unit_currency']}-{acc['currency']}" not in exclude_pairs
            and float(acc['balance']) > 0
            and float(acc['avg_buy_price']) > 0
        ]

    if not traded_positions:
        print("No traded positions found.")
        return

    ticker_data = get_tickers(ticker)

    results = []
    total_pnl_krw = 0.0
    total_invest_krw = 0.0
    current_value_culmulative = 0

    for acc in traded_positions:
        currency = acc['currency']
        market = f"KRW-{currency}"

        if market in exclude_pairs:
            continue

        avg_buy_price = float(acc['avg_buy_price'])
        balance = float(acc['balance'])

        current_price = ticker_data[market]['trade_price']
        invest_amount = avg_buy_price * balance
        current_value = current_price * balance
        current_value_culmulative += current_value
        pnl = current_value - invest_amount
        pnl_percent = (pnl / invest_amount) * 100 if invest_amount != 0 else 0

        total_pnl_krw += pnl
        total_invest_krw += invest_amount

        results.append({
            'market': market,
            'pnl': pnl,
            'pnl_percent': pnl_percent,
            'current_value': current_value
        })

    # Sort results by PnL% descending
    results.sort(key=lambda x: x['pnl_percent'], reverse=True)
    
    num_positive_pnl = 0
    num_negative_pnl = 0

    # Print after sorting
    for res in results:
        pnl = res['pnl']
        pnl_percent = res['pnl_percent']
        market = res['market']
        current_value = floor(res['current_value'])
        sign_krw = "+" if pnl >= 0 else "-"
        sign_pct = "+" if pnl_percent >= 0 else "-"
        print(f"{market}: {sign_krw}{abs(pnl):,.0f} KRW {sign_pct}{abs(pnl_percent):.2f}% / {current_value:,} KRW")
        pnl_ticker_list.append(market)

        # Count positive/negative PnL
        if pnl >= 0:
            num_positive_pnl += 1
        else:
            num_negative_pnl += 1

    # Print total PnL summary
    if total_invest_krw > 0:
        total_pnl_percent = (total_pnl_krw / total_invest_krw) * 100
    else:
        total_pnl_percent = 0.0

    sign_krw = "+" if total_pnl_krw >= 0 else "-"
    sign_pct = "+" if total_pnl_percent >= 0 else "-"

    print()
    print(f"+: {num_positive_pnl}, -: {num_negative_pnl}")
    print(f"Total: {current_value_culmulative:,.0f} KRW / PnL: {sign_krw}{abs(total_pnl_krw):,.0f} KRW {sign_pct}{abs(total_pnl_percent):.2f}%")

    # Print number of alts (positions)
    print(f"num of alts: {len(results)}\n")

if __name__ == "__main__":

    print(f"Usage: python3 {os.path.basename(__file__)} {{pnl}} {{ticker}}")

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    # Define the 'pnl' command
    pnl_parser = subparsers.add_parser("pnl")
    pnl_parser.add_argument("ticker", nargs='?', default="all")

    # Parse the arguments
    args = parser.parse_args()

    # Execute the appropriate command
    if args.command == "pnl":
        print_pnl(ticker=args.ticker)

    print_account_balance() # Holding alt list
    print_open_orders() # open orders

    # c = list(set(holding_ticker_list) - set(pnl_ticker_list))
    # print (c)