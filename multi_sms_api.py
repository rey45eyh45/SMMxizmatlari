# -*- coding: utf-8 -*-
"""
MULTI SMS API - Barcha SMS API larni birlashtirgan modul
VAK-SMS, 5SIM, SMSPVA - Eng arzon narxni avtomatik tanlaydi
"""

from config import SMS_API_KEY, FIVESIM_API_KEY, SMSPVA_API_KEY

# API importlar
try:
    from sms_api import VakSMS
except ImportError:
    VakSMS = None

try:
    from fivesim_api import FiveSIM
except ImportError:
    FiveSIM = None

try:
    from smspva_api import SMSPVA
except ImportError:
    SMSPVA = None


# Valyuta kurslari
USD_RATE = 12900  # 1 USD = 12900 so'm
RUB_RATE = 140    # 1 RUB = 140 so'm


class MultiSMSAPI:
    """Barcha SMS API larni birlashtirgan klass"""
    
    # Platformalar - barcha API larda bir xil nom
    SERVICES = {
        "telegram": {
            "name": "📱 Telegram",
            "vaksms": "tg",
            "fivesim": "telegram", 
            "smspva": "opt1"
        },
        "instagram": {
            "name": "📷 Instagram",
            "vaksms": "ig",
            "fivesim": "instagram",
            "smspva": "opt3"
        },
        "whatsapp": {
            "name": "💬 WhatsApp",
            "vaksms": "wa",
            "fivesim": "whatsapp",
            "smspva": "opt2"
        },
        "google": {
            "name": "🔍 Google/Gmail",
            "vaksms": "go",
            "fivesim": "google",
            "smspva": "opt5"
        },
        "tiktok": {
            "name": "🎵 TikTok",
            "vaksms": "tt",
            "fivesim": "tiktok",
            "smspva": "opt23"
        },
        "facebook": {
            "name": "📘 Facebook",
            "vaksms": "fb",
            "fivesim": "facebook",
            "smspva": "opt4"
        },
        "twitter": {
            "name": "🐦 Twitter/X",
            "vaksms": "tw",
            "fivesim": "twitter",
            "smspva": "opt16"
        },
        "discord": {
            "name": "🎮 Discord",
            "vaksms": "ds",
            "fivesim": "discord",
            "smspva": "opt14"
        },
    }
    
    # Davlatlar
    COUNTRIES = {
        "russia": {
            "name": "🇷🇺 Rossiya",
            "vaksms": "ru",
            "fivesim": "russia",
            "smspva": "RU"
        },
        "uzbekistan": {
            "name": "🇺🇿 O'zbekiston",
            "vaksms": "uz",
            "fivesim": "uzbekistan",
            "smspva": "UZ"
        },
        "kazakhstan": {
            "name": "🇰🇿 Qozog'iston",
            "vaksms": "kz",
            "fivesim": "kazakhstan",
            "smspva": "KZ"
        },
        "indonesia": {
            "name": "🇮🇩 Indoneziya",
            "vaksms": "id",
            "fivesim": "indonesia",
            "smspva": "ID"
        },
        "philippines": {
            "name": "🇵🇭 Filippin",
            "vaksms": "ph",
            "fivesim": "philippines",
            "smspva": "PH"
        },
        "vietnam": {
            "name": "🇻🇳 Vetnam",
            "vaksms": "vn",
            "fivesim": "vietnam",
            "smspva": "VN"
        },
        "bangladesh": {
            "name": "🇧🇩 Bangladesh",
            "vaksms": "bd",
            "fivesim": "bangladesh",
            "smspva": "BD"
        },
        "colombia": {
            "name": "🇨🇴 Kolumbiya",
            "vaksms": None,
            "fivesim": "colombia",
            "smspva": "CO"
        },
        "india": {
            "name": "🇮🇳 Hindiston",
            "vaksms": "in",
            "fivesim": "india",
            "smspva": "IN"
        },
    }
    
    def __init__(self):
        # API lar
        self.vaksms = VakSMS() if VakSMS and SMS_API_KEY else None
        self.fivesim = FiveSIM(FIVESIM_API_KEY) if FiveSIM and FIVESIM_API_KEY else None
        self.smspva = SMSPVA(SMSPVA_API_KEY) if SMSPVA and SMSPVA_API_KEY else None
        
        # Aktiv API lar
        self.active_apis = []
        if self.vaksms:
            self.active_apis.append("vaksms")
        if self.fivesim:
            self.active_apis.append("fivesim")
        if self.smspva:
            self.active_apis.append("smspva")
    
    def get_all_balances(self):
        """Barcha API balanslarini olish"""
        balances = {}
        
        if self.vaksms:
            try:
                balances["vaksms"] = {"balance": self.vaksms.get_balance(), "currency": "RUB"}
            except:
                balances["vaksms"] = {"balance": 0, "currency": "RUB"}
        
        if self.fivesim:
            try:
                balances["fivesim"] = {"balance": self.fivesim.get_balance(), "currency": "USD"}
            except:
                balances["fivesim"] = {"balance": 0, "currency": "USD"}
        
        if self.smspva:
            try:
                balances["smspva"] = {"balance": self.smspva.get_balance(), "currency": "USD"}
            except:
                balances["smspva"] = {"balance": 0, "currency": "USD"}
        
        return balances
    
    def get_best_price(self, service, country):
        """Eng arzon narxni topish - barcha API lardan"""
        prices = []
        
        service_codes = self.SERVICES.get(service, {})
        country_codes = self.COUNTRIES.get(country, {})
        
        # VAK-SMS
        if self.vaksms and service_codes.get("vaksms") and country_codes.get("vaksms"):
            try:
                price_rub = self.vaksms.get_price(
                    service_codes["vaksms"],
                    country_codes["vaksms"]
                )
                if price_rub and price_rub > 0:
                    price_som = int(price_rub * RUB_RATE * 1.20)  # 20% ustama
                    prices.append({
                        "api": "vaksms",
                        "price_original": price_rub,
                        "currency": "RUB",
                        "price_som": price_som
                    })
            except:
                pass
        
        # 5SIM
        if self.fivesim and service_codes.get("fivesim") and country_codes.get("fivesim"):
            try:
                price_usd = self.fivesim.get_prices(
                    country_codes["fivesim"],
                    service_codes["fivesim"]
                )
                if price_usd and price_usd > 0:
                    price_som = int(price_usd * USD_RATE * 1.20)
                    prices.append({
                        "api": "fivesim",
                        "price_original": price_usd,
                        "currency": "USD",
                        "price_som": price_som
                    })
            except:
                pass
        
        # SMSPVA
        if self.smspva and service_codes.get("smspva") and country_codes.get("smspva"):
            try:
                price_usd = self.smspva.get_price(
                    service_codes["smspva"],
                    country_codes["smspva"]
                )
                if price_usd and price_usd > 0:
                    price_som = int(price_usd * USD_RATE * 1.20)
                    prices.append({
                        "api": "smspva",
                        "price_original": price_usd,
                        "currency": "USD",
                        "price_som": price_som
                    })
            except:
                pass
        
        # Eng arzonini topish
        if prices:
            best = min(prices, key=lambda x: x["price_som"])
            return best
        
        return None
    
    def get_all_prices(self, service, country):
        """Barcha API lardagi narxlar"""
        prices = []
        
        service_codes = self.SERVICES.get(service, {})
        country_codes = self.COUNTRIES.get(country, {})
        
        # VAK-SMS
        if self.vaksms and service_codes.get("vaksms") and country_codes.get("vaksms"):
            try:
                price_rub = self.vaksms.get_price(
                    service_codes["vaksms"],
                    country_codes["vaksms"]
                )
                if price_rub and price_rub > 0:
                    price_som = int(price_rub * RUB_RATE * 1.20)
                    prices.append({
                        "api": "vaksms",
                        "api_name": "VAK-SMS",
                        "price_original": price_rub,
                        "currency": "RUB",
                        "price_som": price_som
                    })
            except:
                pass
        
        # 5SIM
        if self.fivesim and service_codes.get("fivesim") and country_codes.get("fivesim"):
            try:
                price_usd = self.fivesim.get_prices(
                    country_codes["fivesim"],
                    service_codes["fivesim"]
                )
                if price_usd and price_usd > 0:
                    price_som = int(price_usd * USD_RATE * 1.20)
                    prices.append({
                        "api": "fivesim",
                        "api_name": "5SIM.NET",
                        "price_original": price_usd,
                        "currency": "USD",
                        "price_som": price_som
                    })
            except:
                pass
        
        # SMSPVA
        if self.smspva and service_codes.get("smspva") and country_codes.get("smspva"):
            try:
                price_usd = self.smspva.get_price(
                    service_codes["smspva"],
                    country_codes["smspva"]
                )
                if price_usd and price_usd > 0:
                    price_som = int(price_usd * USD_RATE * 1.20)
                    prices.append({
                        "api": "smspva",
                        "api_name": "SMSPVA",
                        "price_original": price_usd,
                        "currency": "USD",
                        "price_som": price_som
                    })
            except:
                pass
        
        # Narx bo'yicha saralash
        prices.sort(key=lambda x: x["price_som"])
        return prices
    
    def buy_number(self, service, country, preferred_api=None):
        """Raqam sotib olish - eng arzon API dan"""
        
        if preferred_api:
            # Ma'lum API dan olish
            return self._buy_from_api(preferred_api, service, country)
        
        # Eng arzon API ni topish
        best = self.get_best_price(service, country)
        if not best:
            return {"error": "Raqam mavjud emas"}
        
        return self._buy_from_api(best["api"], service, country)
    
    def _buy_from_api(self, api, service, country):
        """Ma'lum API dan raqam olish"""
        service_codes = self.SERVICES.get(service, {})
        country_codes = self.COUNTRIES.get(country, {})
        
        if api == "vaksms" and self.vaksms:
            result = self.vaksms.get_number(
                service_codes.get("vaksms"),
                country_codes.get("vaksms")
            )
            if "error" not in result:
                return {
                    "api": "vaksms",
                    "phone": result.get("tel", result.get("number")),
                    "order_id": result.get("idNum", result.get("id")),
                    "raw": result
                }
            return result
        
        elif api == "fivesim" and self.fivesim:
            result = self.fivesim.buy_number(
                country_codes.get("fivesim"),
                service_codes.get("fivesim")
            )
            if "error" not in result:
                return {
                    "api": "fivesim",
                    "phone": result.get("phone"),
                    "order_id": result.get("id"),
                    "raw": result
                }
            return result
        
        elif api == "smspva" and self.smspva:
            result = self.smspva.get_number(
                service_codes.get("smspva"),
                country_codes.get("smspva")
            )
            if "error" not in result and result.get("response") == "1":
                return {
                    "api": "smspva",
                    "phone": result.get("number"),
                    "order_id": result.get("id"),
                    "raw": result
                }
            return {"error": result.get("response", "Xatolik")}
        
        return {"error": "API topilmadi"}
    
    def get_sms(self, api, order_id):
        """SMS kodini olish"""
        if api == "vaksms" and self.vaksms:
            return self.vaksms.get_sms(order_id)
        elif api == "fivesim" and self.fivesim:
            return self.fivesim.get_sms(order_id)
        elif api == "smspva" and self.smspva:
            return self.smspva.get_sms(order_id)
        return {"error": "API topilmadi"}
    
    def cancel_number(self, api, order_id):
        """Raqamni bekor qilish"""
        if api == "vaksms" and self.vaksms:
            return self.vaksms.cancel_number(order_id)
        elif api == "fivesim" and self.fivesim:
            return self.fivesim.cancel_number(order_id)
        elif api == "smspva" and self.smspva:
            return self.smspva.cancel_number(order_id)
        return {"error": "API topilmadi"}
    
    def finish_number(self, api, order_id):
        """Raqamni yakunlash"""
        if api == "vaksms" and self.vaksms:
            return self.vaksms.finish_number(order_id)
        elif api == "fivesim" and self.fivesim:
            return self.fivesim.finish_number(order_id)
        elif api == "smspva" and self.smspva:
            return self.smspva.finish_number(order_id)
        return {"error": "API topilmadi"}


# Test
if __name__ == "__main__":
    api = MultiSMSAPI()
    print("Aktiv API lar:", api.active_apis)
    print("\nBalanslar:", api.get_all_balances())
    
    # Telegram narxlari
    print("\n=== TELEGRAM NARXLARI ===")
    for country in ["indonesia", "philippines", "bangladesh", "colombia", "russia"]:
        prices = api.get_all_prices("telegram", country)
        country_name = api.COUNTRIES.get(country, {}).get("name", country)
        print(f"\n{country_name}:")
        for p in prices:
            print(f"  {p['api_name']}: {p['price_original']} {p['currency']} = {p['price_som']:,} so'm")
