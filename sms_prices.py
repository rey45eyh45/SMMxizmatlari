# -*- coding: utf-8 -*-
"""
VIRTUAL RAQAM NARXLARI - Barcha API lardan
VAK-SMS, 5SIM, SMSPVA
"""

# Valyuta kurslari
USD_RATE = 12900  # 1 USD = 12900 so'm
RUB_RATE = 140    # 1 RUB = 140 so'm
MARKUP = 1.20     # 20% ustama

# ==================== TELEGRAM NARXLARI ====================
TELEGRAM_SMS_PRICES = {
    # SMSPVA.COM - Haqiqiy narxlar (ENG ARZON!)
    "smspva_vn": {
        "api": "smspva",
        "country": "VN",
        "country_name": "Vetnam",
        "flag": "VN",
        "price_usd": 0.09,
        "price_som": 1393,
        "service": "opt1"
    },
    "smspva_uz": {
        "api": "smspva",
        "country": "UZ", 
        "country_name": "O'zbekiston",
        "flag": "UZ",
        "price_usd": 0.10,
        "price_som": 1548,
        "service": "opt1"
    },
    "smspva_ru": {
        "api": "smspva",
        "country": "RU",
        "country_name": "Rossiya",
        "flag": "RU",
        "price_usd": 0.15,
        "price_som": 2322,
        "service": "opt1"
    },
    "smspva_id": {
        "api": "smspva",
        "country": "ID",
        "country_name": "Indoneziya",
        "flag": "ID",
        "price_usd": 0.20,
        "price_som": 3096,
        "service": "opt1"
    },
    "smspva_co": {
        "api": "smspva",
        "country": "CO",
        "country_name": "Kolumbiya",
        "flag": "CO",
        "price_usd": 0.22,
        "price_som": 3405,
        "service": "opt1"
    },
    "smspva_bd": {
        "api": "smspva",
        "country": "BD", 
        "country_name": "Bangladesh",
        "flag": "BD",
        "price_usd": 0.30,
        "price_som": 4644,
        "service": "opt1"
    },
    "smspva_gb": {
        "api": "smspva",
        "country": "UK",
        "country_name": "Angliya",
        "flag": "GB",
        "price_usd": 0.54,
        "price_som": 8359,
        "service": "opt1"
    },
    "smspva_ph": {
        "api": "smspva",
        "country": "PH",
        "country_name": "Filippin",
        "flag": "PH",
        "price_usd": 0.55,
        "price_som": 8514,
        "service": "opt1"
    },
    "smspva_pt": {
        "api": "smspva",
        "country": "PT",
        "country_name": "Portugaliya",
        "flag": "PT",
        "price_usd": 0.82,
        "price_som": 12693,
        "service": "opt1"
    },
    
    # VAK-SMS.COM - Haqiqiy narxlar
    "vaksms_id": {
        "api": "vaksms",
        "country": "id",
        "country_name": "Indoneziya",
        "flag": "ID",
        "price_rub": 12,
        "price_som": 2016,
        "service": "tg"
    },
    "vaksms_ph": {
        "api": "vaksms",
        "country": "ph",
        "country_name": "Filippin", 
        "flag": "PH",
        "price_rub": 16,
        "price_som": 2688,
        "service": "tg"
    },
    "vaksms_vn": {
        "api": "vaksms",
        "country": "vn",
        "country_name": "Vetnam",
        "flag": "VN",
        "price_rub": 23,
        "price_som": 3864,
        "service": "tg"
    },
    "vaksms_uz": {
        "api": "vaksms",
        "country": "uz",
        "country_name": "O'zbekiston",
        "flag": "UZ",
        "price_rub": 64,
        "price_som": 10752,
        "service": "tg"
    },
    "vaksms_ru": {
        "api": "vaksms",
        "country": "ru",
        "country_name": "Rossiya",
        "flag": "RU",
        "price_rub": 100,
        "price_som": 16800,
        "service": "tg"
    },
    
    # 5SIM.NET - Zaxira variant
    "fivesim_id": {
        "api": "fivesim",
        "country": "indonesia",
        "country_name": "Indoneziya",
        "flag": "ID",
        "price_rub": 50,
        "price_som": 8400,
        "service": "telegram"
    },
    "fivesim_ph": {
        "api": "fivesim",
        "country": "philippines",
        "country_name": "Filippin",
        "flag": "PH",
        "price_rub": 93.33,
        "price_som": 15679,
        "service": "telegram"
    },
    "fivesim_gb": {
        "api": "fivesim",
        "country": "england",
        "country_name": "Angliya",
        "flag": "GB",
        "price_rub": 110,
        "price_som": 18480,
        "service": "telegram"
    },
    "fivesim_uz": {
        "api": "fivesim",
        "country": "uzbekistan",
        "country_name": "O'zbekiston",
        "flag": "UZ",
        "price_rub": 120,
        "price_som": 20160,
        "service": "telegram"
    },
    "fivesim_de": {
        "api": "fivesim",
        "country": "germany",
        "country_name": "Germaniya",
        "flag": "DE",
        "price_rub": 340,
        "price_som": 57120,
        "service": "telegram"
    },
}

# ==================== INSTAGRAM NARXLARI ====================
INSTAGRAM_SMS_PRICES = {
    "smspva_ru": {
        "api": "smspva",
        "country": "RU",
        "country_name": "Rossiya",
        "flag": "RU",
        "price_usd": 0.01,
        "price_som": 155,
        "service": "opt3"
    },
    "vaksms_ru": {
        "api": "vaksms",
        "country": "ru",
        "country_name": "Rossiya",
        "flag": "RU",
        "price_rub": 1,
        "price_som": 168,
        "service": "ig"
    },
}

# ==================== WHATSAPP NARXLARI ====================
WHATSAPP_SMS_PRICES = {
    "vaksms_uz": {
        "api": "vaksms",
        "country": "uz",
        "country_name": "O'zbekiston",
        "flag": "UZ",
        "price_rub": 19,
        "price_som": 3192,
        "service": "wa"
    },
    "vaksms_id": {
        "api": "vaksms",
        "country": "id",
        "country_name": "Indoneziya",
        "flag": "ID",
        "price_rub": 20,
        "price_som": 3360,
        "service": "wa"
    },
}

# ==================== BARCHA XIZMATLAR NARXLARI ====================
ALL_SMS_SERVICES = {
    "telegram": {
        "name": "Telegram",
        "icon": "tg",
        "prices": TELEGRAM_SMS_PRICES
    },
    "instagram": {
        "name": "Instagram", 
        "icon": "ig",
        "prices": INSTAGRAM_SMS_PRICES
    },
    "whatsapp": {
        "name": "WhatsApp",
        "icon": "wa",
        "prices": WHATSAPP_SMS_PRICES
    },
}


def get_cheapest_telegram():
    """Eng arzon Telegram raqam"""
    prices = list(TELEGRAM_SMS_PRICES.values())
    return min(prices, key=lambda x: x["price_som"])


def get_all_telegram_prices():
    """Barcha Telegram narxlari (arzondan qimmatga)"""
    prices = list(TELEGRAM_SMS_PRICES.values())
    return sorted(prices, key=lambda x: x["price_som"])


def get_cheapest_by_country(service="telegram"):
    """Har bir davlat uchun eng arzon variant"""
    if service == "telegram":
        prices = TELEGRAM_SMS_PRICES
    elif service == "instagram":
        prices = INSTAGRAM_SMS_PRICES
    else:
        prices = WHATSAPP_SMS_PRICES
    
    # Davlatlar bo'yicha guruhlash
    countries = {}
    for key, val in prices.items():
        country = val["flag"]
        if country not in countries:
            countries[country] = val
        elif val["price_som"] < countries[country]["price_som"]:
            countries[country] = val
    
    return sorted(countries.values(), key=lambda x: x["price_som"])


# Test
if __name__ == "__main__":
    print("=== TELEGRAM ENG ARZON NARXLAR ===")
    for p in get_all_telegram_prices():
        api = p["api"].upper()
        country = p["country_name"]
        som = p["price_som"]
        print(f"{api}: {country} = {som:,} so'm")
    
    print("\n=== DAVLATLAR BO'YICHA ENG ARZON ===")
    for p in get_cheapest_by_country("telegram"):
        api = p["api"].upper()
        country = p["country_name"]
        flag = p["flag"]
        som = p["price_som"]
        print(f"{flag} {country}: {som:,} so'm ({api})")
    
    print("\n=== ENG ARZON ===")
    cheapest = get_cheapest_telegram()
    print(f"{cheapest['api'].upper()}: {cheapest['country_name']} = {cheapest['price_som']:,} so'm")
