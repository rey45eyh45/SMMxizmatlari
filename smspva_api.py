# -*- coding: utf-8 -*-
"""
SMSPVA.COM API integratsiyasi
Virtual telefon raqamlar - Eng arzon narxlar!
https://smspva.com
"""

import requests

# Alias for compatibility
SMSPVAAPI = None  # Will be set below

class SMSPVA:
    """SMSPVA.COM API class"""
    
    BASE_URL = "https://smspva.com/priemnik.php"
    
    # Platformalar ro'yxati (SMSPVA kodlari)
    SERVICES = {
        "opt1": {"name": "Telegram", "code": "opt1"},
        "opt2": {"name": "WhatsApp", "code": "opt2"},
        "opt3": {"name": "Instagram", "code": "opt3"},
        "opt4": {"name": "Facebook", "code": "opt4"},
        "opt5": {"name": "Google/Gmail", "code": "opt5"},
        "opt16": {"name": "Twitter/X", "code": "opt16"},
        "opt23": {"name": "TikTok", "code": "opt23"},
        "opt14": {"name": "Discord", "code": "opt14"},
        "opt33": {"name": "Amazon", "code": "opt33"},
        "opt15": {"name": "Microsoft", "code": "opt15"},
        "opt51": {"name": "OpenAI/ChatGPT", "code": "opt51"},
        "opt19": {"name": "Uber", "code": "opt19"},
        "opt25": {"name": "Spotify", "code": "opt25"},
    }
    
    # Davlatlar ro'yxati (SMSPVA country ID)
    COUNTRIES = {
        "RU": {"name": "Rossiya", "code": "RU", "id": "RU"},
        "UA": {"name": "Ukraina", "code": "UA", "id": "UA"},
        "KZ": {"name": "Qozog'iston", "code": "KZ", "id": "KZ"},
        "UZ": {"name": "O'zbekiston", "code": "UZ", "id": "UZ"},
        "ID": {"name": "Indoneziya", "code": "ID", "id": "ID"},
        "PH": {"name": "Filippin", "code": "PH", "id": "PH"},
        "IN": {"name": "Hindiston", "code": "IN", "id": "IN"},
        "VN": {"name": "Vetnam", "code": "VN", "id": "VN"},
        "BD": {"name": "Bangladesh", "code": "BD", "id": "BD"},
        "CO": {"name": "Kolumbiya", "code": "CO", "id": "CO"},
        "UK": {"name": "Angliya", "code": "UK", "id": "UK"},
        "US": {"name": "AQSh", "code": "US", "id": "US"},
        "PT": {"name": "Portugaliya", "code": "PT", "id": "PT"},
        "GB": {"name": "Buyuk Britaniya", "code": "GB", "id": "UK"},
    }
    
    def __init__(self, api_key):
        self.api_key = api_key
    
    def _request(self, params):
        """API so'rov"""
        params["apikey"] = self.api_key
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            
            if response.status_code == 200:
                try:
                    return response.json()
                except:
                    return {"response": response.text}
            else:
                return {"error": response.text, "status_code": response.status_code}
        except Exception as e:
            return {"error": str(e)}
    
    def get_balance(self):
        """Balansni olish (USD)"""
        result = self._request({"metod": "get_balance"})
        if "error" not in result:
            return float(result.get("balance", 0))
        return 0
    
    def get_price(self, service, country):
        """Narxni olish (USD)"""
        result = self._request({
            "metod": "get_service_price",
            "service": service,
            "country": country
        })
        if "error" not in result and "price" in result:
            return float(result.get("price", 0))
        return 0
    
    def get_number(self, service, country):
        """Raqam sotib olish"""
        result = self._request({
            "metod": "get_number",
            "service": service,
            "country": country
        })
        return result
    
    def get_sms(self, order_id):
        """SMS kodini olish"""
        result = self._request({
            "metod": "get_sms",
            "id": order_id
        })
        return result
    
    def cancel_number(self, order_id):
        """Raqamni bekor qilish"""
        result = self._request({
            "metod": "denial",
            "id": order_id
        })
        return result
    
    def finish_number(self, order_id):
        """Raqamni yakunlash"""
        result = self._request({
            "metod": "end_num",
            "id": order_id
        })
        return result


# Alias for compatibility
SMSPVAAPI = SMSPVA