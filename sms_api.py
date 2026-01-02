# -*- coding: utf-8 -*-
"""
VAK-SMS.COM API integratsiyasi
Virtual telefon raqamlar - Telegram, Instagram, WhatsApp va boshqalar uchun
https://vak-sms.com
Arzon narxlar - 5SIM dan 10-50 marta arzon!
+ CACHE TIZIMI - tezlik oshirildi!
"""

import requests
from config import SMS_API_KEY

# Cache import
try:
    from cache import sms_cache, balance_cache
except ImportError:
    sms_cache = None
    balance_cache = None

class VakSMS:
    """VAK-SMS.COM API class"""
    
    BASE_URL = "https://vak-sms.com/api"
    
    # Platformalar ro'yxati (VAK-SMS kodlari)
    SERVICES = {
        "tg": {"name": "📱 Telegram", "code": "tg"},
        "ig": {"name": "📷 Instagram", "code": "ig"},
        "wa": {"name": "💬 WhatsApp", "code": "wa"},
        "go": {"name": "🔍 Google/Gmail", "code": "go"},
        "ya": {"name": "🔴 Yandex", "code": "ya"},
        "tt": {"name": "🎵 TikTok", "code": "tt"},
        "fb": {"name": "📘 Facebook", "code": "fb"},
        "tw": {"name": "🐦 Twitter/X", "code": "tw"},
        "vk": {"name": "💙 VKontakte", "code": "vk"},
        "ok": {"name": "🟠 OK.ru", "code": "ok"},
        "vi": {"name": "💜 Viber", "code": "vi"},
        "we": {"name": "🟢 WeChat", "code": "we"},
        "ds": {"name": "🎮 Discord", "code": "ds"},
        "am": {"name": "📦 Amazon", "code": "am"},
        "mi": {"name": "🪟 Microsoft", "code": "mi"},
        "oi": {"name": "🤖 OpenAI/ChatGPT", "code": "oi"},
        "ub": {"name": "🚗 Uber", "code": "ub"},
        "ol": {"name": "📝 OLX", "code": "ol"},
        "sp": {"name": "🎧 Spotify", "code": "sp"},
        "ot": {"name": "🔢 Boshqa", "code": "ot"},
    }
    
    # Davlatlar ro'yxati (VAK-SMS kodlari)
    COUNTRIES = {
        "ru": {"name": "🇷🇺 Rossiya", "code": "ru"},
        "ua": {"name": "🇺🇦 Ukraina", "code": "ua"},
        "kz": {"name": "🇰🇿 Qozog'iston", "code": "kz"},
        "uz": {"name": "🇺🇿 O'zbekiston", "code": "uz"},
        "tj": {"name": "🇹🇯 Tojikiston", "code": "tj"},
        "kg": {"name": "🇰🇬 Qirg'iziston", "code": "kg"},
        "id": {"name": "🇮🇩 Indoneziya", "code": "id"},
        "ph": {"name": "🇵🇭 Filippin", "code": "ph"},
        "my": {"name": "🇲🇾 Malayziya", "code": "my"},
        "vn": {"name": "🇻🇳 Vetnam", "code": "vn"},
        "th": {"name": "🇹🇭 Tailand", "code": "th"},
        "bd": {"name": "🇧🇩 Bangladesh", "code": "bd"},
        "in": {"name": "🇮🇳 Hindiston", "code": "in"},
        "pk": {"name": "🇵🇰 Pokiston", "code": "pk"},
        "ge": {"name": "🇬🇪 Gruziya", "code": "ge"},
        "az": {"name": "🇦🇿 Ozarbayjon", "code": "az"},
        "pl": {"name": "🇵🇱 Polsha", "code": "pl"},
        "de": {"name": "🇩🇪 Germaniya", "code": "de"},
        "gb": {"name": "🇬🇧 Angliya", "code": "gb"},
        "us": {"name": "🇺🇸 AQSh", "code": "us"},
    }
    
    def __init__(self, api_key=None):
        self.api_key = api_key or SMS_API_KEY
    
    def _request(self, endpoint, params=None):
        """API so'rov"""
        url = f"{self.BASE_URL}/{endpoint}"
        
        if params is None:
            params = {}
        params["apiKey"] = self.api_key
        
        try:
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                try:
                    return response.json()
                except:
                    return {"error": response.text}
            else:
                return {"error": response.text, "status_code": response.status_code}
        except Exception as e:
            return {"error": str(e)}
    
    def get_balance(self, use_cache=True):
        """Balansni olish (RUB - rubl) - CACHED 1 daqiqa"""
        cache_key = "sms_balance"
        
        # Cache dan olish
        if use_cache and balance_cache:
            cached_data = balance_cache.get(cache_key)
            if cached_data is not None:
                return cached_data
        
        result = self._request("getBalance/")
        balance = 0.0
        
        if isinstance(result, dict) and "balance" in result:
            balance = float(result["balance"])
        
        # Cache ga saqlash (1 daqiqa)
        if balance_cache:
            balance_cache.set(cache_key, balance, ttl=60)
        
        return balance
    
    def get_count_number(self, service, country="ru", use_cache=True):
        """Mavjud raqamlar sonini olish - CACHED 5 daqiqa"""
        cache_key = f"sms_count:{service}:{country}"
        
        # Cache dan olish
        if use_cache and sms_cache:
            cached_data = sms_cache.get(cache_key)
            if cached_data is not None:
                return cached_data
        
        result = self._request("getCountNumber/", {
            "service": service,
            "country": country,
            "price": "true"
        })
        
        if isinstance(result, dict) and "error" not in result:
            # Cache ga saqlash (5 daqiqa)
            if sms_cache:
                sms_cache.set(cache_key, result, ttl=300)
            return result
        return None
    
    def buy_number(self, country, service, operator=None):
        """Raqam sotib olish
        
        Args:
            country: Mamlakat kodi (ru, uz, kz, ...)
            service: Servis kodi (tg, ig, wa, ...)
            operator: Operator nomi (ixtiyoriy)
        
        Returns:
            dict: {"tel": "79991112233", "idNum": "abc123..."}
        """
        params = {
            "service": service,
            "country": country
        }
        
        if operator:
            params["operator"] = operator
        
        result = self._request("getNumber/", params)
        
        if isinstance(result, dict):
            if "tel" in result and "idNum" in result:
                # Muvaffaqiyatli
                return {
                    "success": True,
                    "phone": str(result["tel"]),
                    "order_id": result["idNum"],
                    "country": country,
                    "service": service
                }
            elif "error" in result:
                error = result["error"]
                return {"success": False, "error": self._translate_error(error)}
        
        return {"success": False, "error": "Noma'lum xatolik"}
    
    def check_order(self, order_id):
        """SMS kodni tekshirish (check_sms bilan bir xil)
        
        Args:
            order_id: Buyurtma ID (idNum)
        
        Returns:
            dict: {"smsCode": "12345"} yoki {"smsCode": null}
        """
        result = self._request("getSmsCode/", {"idNum": order_id})
        
        if isinstance(result, dict):
            if "smsCode" in result:
                code = result["smsCode"]
                if code is not None:
                    return {
                        "success": True,
                        "status": "received",
                        "sms_code": str(code),
                        "order_id": order_id
                    }
                else:
                    return {
                        "success": True,
                        "status": "waiting",
                        "sms_code": None,
                        "order_id": order_id
                    }
            elif "error" in result:
                return {"success": False, "error": self._translate_error(result["error"])}
        
        return {"success": False, "error": "Noma'lum xatolik"}
    
    def set_status(self, order_id, status):
        """Buyurtma statusini o'zgartirish
        
        Args:
            order_id: Buyurtma ID
            status: 
                - "send" - yana SMS kutish
                - "end" - bekor qilish
                - "bad" - raqam ishlatilgan/bloklangan
        """
        result = self._request("setStatus/", {
            "idNum": order_id,
            "status": status
        })
        
        if isinstance(result, dict):
            if result.get("status") == "update":
                return {"success": True, "status": "updated"}
            elif result.get("status") == "smsReceived":
                return {"success": False, "error": "SMS allaqachon qabul qilingan, bekor qilib bo'lmaydi"}
            elif result.get("status") == "waitSMS":
                return {"success": False, "error": "SMS kutilmoqda, bekor qilib bo'lmaydi"}
            elif "error" in result:
                return {"success": False, "error": self._translate_error(result["error"])}
        
        return {"success": False, "error": "Noma'lum xatolik"}
    
    def cancel_order(self, order_id):
        """Buyurtmani bekor qilish"""
        return self.set_status(order_id, "end")
    
    def finish_order(self, order_id):
        """Buyurtmani yakunlash (VAK-SMS da kerak emas, lekin bot uchun)"""
        # VAK-SMS da finish_order yo'q, faqat cancel bor
        return {"success": True, "message": "Buyurtma yakunlandi"}
    
    def request_another_sms(self, order_id):
        """Yana bir SMS so'rash (bepul)"""
        return self.set_status(order_id, "send")
    
    def report_bad_number(self, order_id):
        """Raqam ishlamayotganini xabar qilish"""
        return self.set_status(order_id, "bad")
    
    def get_countries_list(self):
        """Barcha mamlakatlar ro'yxatini olish"""
        try:
            response = requests.get(f"{self.BASE_URL}/getCountryList/", timeout=30)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return []
    
    def get_price(self, service, country="ru"):
        """Servis narxini olish"""
        result = self.get_count_number(service, country)
        if result and "price" in result:
            return float(result["price"])
        return None
    
    def get_cheapest_prices(self, service, limit=10):
        """Eng arzon davlatlarni olish
        
        Args:
            service: Servis kodi (tg, ig, wa, ...)
            limit: Nechta davlat qaytarish
        
        Returns:
            list: [{"country": "ru", "cost": 10.5, "count": 1000}, ...]
        """
        results = []
        
        for country_code in self.COUNTRIES.keys():
            try:
                data = self.get_count_number(service, country_code)
                if data and service in data:
                    count = int(data.get(service, 0))
                    price = float(data.get("price", 0))
                    
                    if count > 0 and price > 0:
                        # VAK-SMS narxi RUB da, USD ga o'tkazamiz (1 RUB ~ 0.011 USD)
                        price_usd = price * 0.011
                        results.append({
                            "country": country_code,
                            "cost": price_usd,
                            "cost_rub": price,
                            "count": count
                        })
            except:
                continue
        
        # Eng arzoni bo'yicha saralash
        results.sort(key=lambda x: x["cost"])
        
        return results[:limit]
    
    def get_all_prices(self, service):
        """Barcha davlatlar narxlarini olish"""
        return self.get_cheapest_prices(service, 50)
    
    def _translate_error(self, error):
        """Xato xabarlarini tarjima qilish"""
        translations = {
            "noNumber": "Raqam mavjud emas, boshqa mamlakat tanlang",
            "noMoney": "Balansda mablag' yetarli emas",
            "noService": "Bu servis qo'llab-quvvatlanmaydi",
            "noCountry": "Bu mamlakat mavjud emas",
            "noOperator": "Operator topilmadi",
            "badStatus": "Noto'g'ri status",
            "idNumNotFound": "Buyurtma topilmadi",
            "badService": "Noto'g'ri servis kodi",
            "badData": "Noto'g'ri ma'lumotlar",
            "apiKeyNotFound": "API kalit noto'g'ri",
        }
        
        if error in translations:
            return translations[error]
        
        return error
    
    def get_country_name(self, country_code):
        """Davlat kodidan nom olish"""
        if country_code in self.COUNTRIES:
            return self.COUNTRIES[country_code]["name"]
        return country_code.upper()
    
    def get_service_name(self, service_key):
        """Xizmat kalitidan nom olish"""
        if service_key in self.SERVICES:
            return self.SERVICES[service_key]["name"]
        return service_key.upper()


# Global instance
sms_api = VakSMS()


# Test funksiyasi
if __name__ == "__main__":
    api = VakSMS()
    
    print("=" * 50)
    print("VAK-SMS.COM API Test")
    print("=" * 50)
    
    # Balans tekshirish
    balance = api.get_balance()
    print(f"\n💰 Balans: {balance} RUB")
    
    # Narxlarni tekshirish
    print("\n💵 Narxlar (Rossiya raqamlari):")
    for code, info in list(api.SERVICES.items())[:10]:
        result = api.get_count_number(info["code"], "ru")
        if result:
            count = result.get(info["code"], 0)
            price = result.get("price", "?")
            print(f"  {info['name']}: {price} RUB ({count} ta mavjud)")
    
    print("\n" + "=" * 50)
