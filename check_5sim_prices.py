# -*- coding: utf-8 -*-
"""5SIM Telegram narxlarini olish"""
import requests

api_key = 'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3OTg1NjYwOTMsImlhdCI6MTc2NzAzMDA5MywicmF5IjoiNTBmMTY4YWM5NmY5OTFkYzBmYjAyZjgyNmMxNWE4NjEiLCJzdWIiOjM2OTYxMzB9.Ed33xDN9dR_MNnUWocJl3Dy_iHhk1q12frMZatddIZnV6cUUl1Qc_K_wLzTS3lhs060jFiexShCQjhB5IldJOIOVvtas-lm2Lb5NTmHZOqLmegaDxDSSrU6GSwdNmX9jVHPPyCpiQo7ETV-au5YJNlHpUOXapkTGdRfKQjVhB8dmS1z0OyvWEVuk9NASCJbTEKeRd0X1IGem745nGVHH12QcrMrgZSh5vdrf1nL8AJmkHNhStw7VUKdr4s2j13LK6-HBrBUJRbHbquAAG8jM3AlOo0j-sov-5xW0jprO1XQG8wBa_j6SJs57IKurM9MLLFQfAe1wU1yb5x2jS8A-0w'
headers = {'Authorization': f'Bearer {api_key}'}

countries = ['russia', 'uzbekistan', 'indonesia', 'vietnam', 'philippines', 'india', 'bangladesh', 'ukraine', 'kazakhstan', 'tajikistan', 'kyrgyzstan', 'georgia', 'poland', 'germany', 'england', 'usa', 'colombia']

print('=== 5SIM TELEGRAM NARXLARI ===')
prices = []

for country in countries:
    try:
        r = requests.get(f'https://5sim.net/v1/guest/prices?product=telegram&country={country}', headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data and country in data:
                country_data = data[country]
                if country_data and 'telegram' in country_data:
                    tg = country_data['telegram']
                    if tg:
                        for op, info in tg.items():
                            if info:
                                cost = info.get('cost', 0)
                                count = info.get('count', 0)
                                if count > 0 and cost > 0:
                                    som = int(cost * 140 * 1.2)
                                    prices.append((country, cost, som, count, op))
                                    break
    except Exception as e:
        print(f'{country}: Xato - {e}')

prices.sort(key=lambda x: x[1])
print(f'\nJami {len(prices)} ta davlat\n')
print('ENG ARZON:')
print('-' * 50)
for country, cost, som, count, op in prices:
    print(f'{country}: {cost} RUB = {som:,} som ({count} ta)')
