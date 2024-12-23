import json
from math import floor
import os

### alt_list.txt ###
# with open('alt_list.txt', 'r') as f:
    # alt_list = [line for line in f.read().split("\n") if line]

### settings.json ###
with open('settings.json', 'r') as file:
    settings = json.load(file)
num_of_alts = settings['num_of_alts']
input_krw = settings['input_krw'] * (1 - 0.0005)
krw_per_ticker = floor(input_krw / num_of_alts)
exclude_pairs = settings['exclude_pairs']

### Upbit API key ###
access_key = os.environ['UPBIT_OPEN_API_ACCESS_KEY']
secret_key = os.environ['UPBIT_OPEN_API_SECRET_KEY']
server_url = "https://api.upbit.com"