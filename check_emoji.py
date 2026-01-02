# -*- coding: utf-8 -*-
from services_config import TELEGRAM_SERVICES

print("Emojilar tekshiruvi:")
print("=" * 50)
for k, v in list(TELEGRAM_SERVICES.items())[:10]:
    print(f"{k}: {v['emoji']} {v['name']}")
