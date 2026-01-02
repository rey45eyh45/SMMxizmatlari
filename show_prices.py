# -*- coding: utf-8 -*-
from services_config import TELEGRAM_SERVICES

USD_RATE = 12900
MARKUP = 1.15

print("TELEGRAM XIZMATLARI NARXLARI (1000 ta uchun)")
print("=" * 70)

for key, val in TELEGRAM_SERVICES.items():
    peakerr = val.get('peakerr')
    smmmain = val.get('smmmain')
    
    p_price = peakerr['price_usd'] if peakerr else 999
    s_price = smmmain['price_usd'] if smmmain else 999
    best = min(p_price, s_price)
    som = int(best * USD_RATE * MARKUP)
    
    panel = "P" if p_price <= s_price else "S"
    print(f"{val['emoji']} {val['name']}: ${best:.4f} = {som:,} so'm [{panel}]")

print("=" * 70)
print(f"Jami: {len(TELEGRAM_SERVICES)} ta xizmat")
