import json

def print_settings():
    with open('settings.json', 'r') as file:
        settings = json.load(file)

        num_of_alts = settings['num_of_alts']
        input_krw = settings['input_krw']
        exclude_pairs = settings['exclude_pairs']

        print(f"num_of_alts: {num_of_alts}")
        print(f"input_krw: {input_krw}")
        krw_per_ticker = input_krw / num_of_alts
        print(f"KRW per a ticker: {krw_per_ticker}")
        print(f"exclude_pairs: {exclude_pairs}")

if __name__ == '__main__':
     print_settings()