# -*- coding: utf-8 -*-
"""5SIM API kalitlarini tekshirish"""
import requests

# 1-chi API key (JWT token) - .env dagi
api_key_jwt = 'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3OTg1NjYwOTMsImlhdCI6MTc2NzAzMDA5MywicmF5IjoiNTBmMTY4YWM5NmY5OTFkYzBmYjAyZjgyNmMxNWE4NjEiLCJzdWIiOjM2OTYxMzB9.Ed33xDN9dR_MNnUWocJl3Dy_iHhk1q12frMZatddIZnV6cUUl1Qc_K_wLzTS3lhs060jFiexShCQjhB5IldJOIOVvtas-lm2Lb5NTmHZOqLmegaDxDSSrU6GSwdNmX9jVHPPyCpiQo7ETV-au5YJNlHpUOXapkTGdRfKQjVhB8dmS1z0OyvWEVuk9NASCJbTEKeRd0X1IGem745nGVHH12QcrMrgZSh5vdrf1nL8AJmkHNhStw7VUKdr4s2j13LK6-HBrBUJRbHbquAAG8jM3AlOo0j-sov-5xW0jprO1XQG8wBa_j6SJs57IKurM9MLLFQfAe1wU1yb5x2jS8A-0w'

# 2-chi API key (oddiy) - foydalanuvchi berdi
api_key_simple = '4101642ed86b4d45903f36e758f218bd'

print('=== JWT TOKEN (uzun) ===')
try:
    headers = {'Authorization': f'Bearer {api_key_jwt}'}
    r = requests.get('https://5sim.net/v1/user/profile', headers=headers, timeout=10)
    print(f'Status: {r.status_code}')
    if r.status_code == 200:
        data = r.json()
        print(f'Email: {data.get("email", "?")}')
        print(f'Balans: {data.get("balance", 0)} RUB')
        print('>>> JWT TOKEN ISHLAYDI!')
    else:
        print(f'Xato: {r.text[:100]}')
except Exception as e:
    print(f'Xato: {e}')

print()
print('=== SIMPLE KEY (qisqa) ===')
try:
    headers2 = {'Authorization': f'Bearer {api_key_simple}'}
    r2 = requests.get('https://5sim.net/v1/user/profile', headers=headers2, timeout=10)
    print(f'Status: {r2.status_code}')
    if r2.status_code == 200:
        data2 = r2.json()
        print(f'Email: {data2.get("email", "?")}')
        print(f'Balans: {data2.get("balance", 0)} RUB')
        print('>>> SIMPLE KEY ISHLAYDI!')
    else:
        print(f'Xato: {r2.text[:100]}')
except Exception as e:
    print(f'Xato: {e}')
