import json

with open('settings.json', 'r') as file:
        settings = json.load(file)

num_of_alts = settings['num_of_alts']
input_krw = settings['input_krw']

print(f"num_of_alts: {num_of_alts}")
print(f"input_krw: {input_krw}")
price = input_krw / num_of_alts
print(f"price: {price}")