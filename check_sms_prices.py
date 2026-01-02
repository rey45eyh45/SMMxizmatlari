# -*- coding: utf-8 -*-
"""VAK-SMS API narxlarini tekshirish"""

from sms_api import VakSMS

api = VakSMS()

print("=== VAK-SMS NARXLAR ===")
print(f"API Balans: {api.get_balance()} RUB")
print()

# Asosiy platformalar
platforms = ['tg', 'ig', 'wa', 'go', 'tt', 'fb', 'tw', 'ds', 'vk', 'oi', 'sp', 'ub']
countries = ['ru', 'uz', 'kz', 'id', 'ph', 'in', 'vn']

RUB_TO_SOM = 140

for platform in platforms:
    info = api.SERVICES.get(platform, {})
    name = info.get('name', platform)
    print(f"\n{name}:")
    
    for country in countries:
        price = api.get_price(platform, country)
        if price and price > 0:
            som = int(price * RUB_TO_SOM * 1.2)  # 20% ustama
            country_info = api.COUNTRIES.get(country, {})
            country_name = country_info.get('name', country)
            print(f"  {country_name}: {price} RUB = {som:,} so'm")
