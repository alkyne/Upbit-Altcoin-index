import requests
import json
from pprint import pprint

def _get_krw_pairs():
    """Retrieve all KRW trading pairs from Upbit."""
    url = 'https://api.upbit.com/v1/market/all'
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers)
    markets = response.json()
    
    # List of pairs to exclude
    exclude_pairs = ['KRW-BTC', 'KRW-ETH', 'KRW-SOL', 'KRW-USDT', 'KRW-USDC', 'KRW-CVC']

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

def _get_volumes(krw_pairs, num_of_alts):
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

    sorted_volume_data = dict(list(dict_sorted.items())[:num_of_alts])

    return sorted_volume_data

def get_tickers():
    with open('settings.json', 'r') as file:
        settings = json.load(file)

    krw_pairs = _get_krw_pairs()
    ticker_data = _get_volumes(krw_pairs, num_of_alts=int(settings['num_of_alts']))
    
    return ticker_data

# for debug
if __name__ == '__main__':
    ticker_data = get_tickers()
    for ticker, value in ticker_data.items():
        print(f"{ticker}: {value['volume']:,.0f} / {value['trade_price']}")

    print(f"num_of_data: {len(ticker_data)}")