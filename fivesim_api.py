# -*- coding: utf-8 -*-
"""
5SIM.NET API integratsiyasi
Virtual telefon raqamlar - Telegram, Instagram, WhatsApp va boshqalar uchun
https://5sim.net
"""

import requests

class FiveSIM:
    """5SIM.NET API class"""
    
    BASE_URL = "https://5sim.net/v1"
    
    # Platformalar ro'yxati (5SIM kodlari)
    SERVICES = {
        "telegram": {"name": "📱 Telegram", "code": "telegram"},
        "instagram": {"name": "📷 Instagram", "code": "instagram"},
        "whatsapp": {"name": "💬 WhatsApp", "code": "whatsapp"},
        "google": {"name": "🔍 Google/Gmail", "code": "google"},
        "tiktok": {"name": "🎵 TikTok", "code": "tiktok"},
        "facebook": {"name": "📘 Facebook", "code": "facebook"},
        "twitter": {"name": "🐦 Twitter/X", "code": "twitter"},
        "discord": {"name": "🎮 Discord", "code": "discord"},
        "amazon": {"name": "📦 Amazon", "code": "amazon"},
        "microsoft": {"name": "🪟 Microsoft", "code": "microsoft"},
        "openai": {"name": "🤖 OpenAI/ChatGPT", "code": "openai"},
        "uber": {"name": "🚗 Uber", "code": "uber"},
        "spotify": {"name": "🎧 Spotify", "code": "spotify"},
    }
    
    # Davlatlar ro'yxati (5SIM kodlari)
    COUNTRIES = {
        "russia": {"name": "🇷🇺 Rossiya", "code": "russia"},
        "ukraine": {"name": "🇺🇦 Ukraina", "code": "ukraine"},
        "kazakhstan": {"name": "🇰🇿 Qozog'iston", "code": "kazakhstan"},
        "uzbekistan": {"name": "🇺🇿 O'zbekiston", "code": "uzbekistan"},
        "indonesia": {"name": "🇮🇩 Indoneziya", "code": "indonesia"},
        "philippines": {"name": "🇵🇭 Filippin", "code": "philippines"},
        "india": {"name": "🇮🇳 Hindiston", "code": "india"},
        "vietnam": {"name": "🇻🇳 Vetnam", "code": "vietnam"},
        "bangladesh": {"name": "🇧🇩 Bangladesh", "code": "bangladesh"},
        "colombia": {"name": "🇨🇴 Kolumbiya", "code": "colombia"},
        "england": {"name": "🇬🇧 Angliya", "code": "england"},
        "usa": {"name": "🇺🇸 AQSh", "code": "usa"},
    }
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json"
        }
    
    def _request(self, endpoint, method="GET", params=None):
        """API so'rov"""
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers, params=params, timeout=30)
            else:
                response = requests.post(url, headers=self.headers, json=params, timeout=30)
            
            if response.status_code == 200:
                try:
                    return response.json()
                except:
                    return {"error": response.text}
            else:
                return {"error": response.text, "status_code": response.status_code}
        except Exception as e:
            return {"error": str(e)}
    
    def get_balance(self):
        """Balansni olish (USD)"""
        result = self._request("user/profile")
        if "error" not in result:
            return result.get("balance", 0)
        return 0
    
    def get_prices(self, country, service):
        """Narxni olish"""
        result = self._request(f"guest/prices?country={country}&product={service}")
        if "error" not in result and country in result:
            service_data = result[country].get(service, {})
            # Eng arzon operatorni topish
            min_price = float('inf')
            for operator, data in service_data.items():
                if isinstance(data, dict) and "cost" in data:
                    if data["cost"] < min_price and data.get("count", 0) > 0:
                        min_price = data["cost"]
            return min_price if min_price != float('inf') else 0
        return 0
    
    def buy_number(self, country, service, operator="any"):
        """Raqam sotib olish"""
        result = self._request(f"user/buy/activation/{country}/{operator}/{service}")
        return result
    
    def check_order(self, order_id):
        """Buyurtma holatini tekshirish"""
        result = self._request(f"user/check/{order_id}")
        return result
    
    def get_sms(self, order_id):
        """SMS kodini olish (check_order alias)"""
        return self.check_order(order_id)
    
    def cancel_order(self, order_id):
        """Raqamni bekor qilish"""
        result = self._request(f"user/cancel/{order_id}")
        return result
    
    def cancel_number(self, order_id):
        """cancel_order alias"""
        return self.cancel_order(order_id)
    
    def finish_order(self, order_id):
        """Raqamni yakunlash"""
        result = self._request(f"user/finish/{order_id}")
        return result
    
    def finish_number(self, order_id):
        """finish_order alias"""
        return self.finish_order(order_id)
