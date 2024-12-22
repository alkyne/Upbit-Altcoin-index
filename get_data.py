import requests
import json
import argparse
import sys
from pprint import pprint

from settings import *

def _get_krw_pairs(ticker="all"):
    """Retrieve all KRW trading pairs from Upbit."""
    url = 'https://api.upbit.com/v1/market/all'
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers)
    markets = response.json()
    
    # Build the list of KRW pairs, excluding the specified pairs
    krw_pairs = [
        market['market'] for market in markets
        if market['market'].startswith('KRW-') and market['market'] not in exclude_pairs
    ]
    return krw_pairs

def _chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def _get_volumes(krw_pairs):
    volume_data = {}

    for chunk in _chunks(krw_pairs, 200):
        markets = ','.join(chunk)
        params = {
            'markets': markets
        }
        url = "https://api.upbit.com/v1/ticker"
        response = requests.get(url, params=params)
        data = response.json()
        # print(params)
        for item in data:
            trade_price = item['trade_price']
            ticker = item['market'] # ticker
            volume = item['acc_trade_price_24h']  # 24-hour accumulated trade volume in KRW
            volume_data[ticker] = {'volume': volume, 'trade_price': trade_price}

    # for market, volume in volume_data.items():
        # print(f"{market}: {volume}")

    # pprint(volume_data)
    dict_sorted = dict(sorted(volume_data.items(), key=lambda x: x[1]['volume'], reverse=True))
    sorted_volume_data = dict(list(dict_sorted.items()))

    return sorted_volume_data

def get_tickers(ticker="all"):

    if ticker == "all":
        krw_pairs = _get_krw_pairs()
    else:
        krw_pairs = [ticker.upper()]
    ticker_data = _get_volumes(krw_pairs)
    
    return ticker_data

# for debug
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("ticker", nargs='?', default="all")    
    args = parser.parse_args()

    # Retrieve the ticker argument, defaulting to 'all'
    ticker = args.ticker
    ticker_data = get_tickers(ticker)
    print(f"Ticker: 24-hour trade volume / price")
    for ticker, value in ticker_data.items():
        price = value['trade_price']
        if isinstance(price, float) and price < 100:
            print(f"{ticker}: {value['volume']:,.0f} / {price:,.6f} KRW")
        elif isinstance(price, float) and price < 1000:
        # Print the value with 5 decimal places
            print(f"{ticker}: {value['volume']:,.0f} / {price:,.1f} KRW")
        else:
            print(f"{ticker}: {value['volume']:,.0f} / {price:,.0f} KRW")

    print(f"num_of_data: {len(ticker_data)}")