# -*- coding: utf-8 -*-
"""
SMS API integratsiyalari - VAK-SMS, 5SIM, SMSPVA
"""
import httpx
from typing import Dict, Any, Optional, List
from .config import SMS_API_KEY, FIVESIM_API_KEY, SMSPVA_API_KEY
from .services import SMS_PLATFORMS, SMS_COUNTRIES, get_rub_rate, get_markup_percent


class VakSMS:
    """VAK-SMS.COM API"""
    
    BASE_URL = "https://vak-sms.com/api"
    
    def __init__(self):
        self.api_key = SMS_API_KEY
    
    async def _request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """API so'rov"""
        url = f"{self.BASE_URL}/{endpoint}"
        if params is None:
            params = {}
        params["apiKey"] = self.api_key
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    return response.json()
                return {"error": response.text}
        except Exception as e:
            return {"error": str(e)}
    
    async def get_balance(self) -> float:
        """Balansni olish (RUB)"""
        result = await self._request("getBalance/")
        if isinstance(result, dict) and "balance" in result:
            return float(result["balance"])
        return 0.0
    
    async def get_price(self, service: str, country: str) -> Optional[Dict[str, Any]]:
        """Narxni olish"""
        result = await self._request("getCountNumber/", {
            "service": service,
            "country": country,
            "price": "true"
        })
        
        if isinstance(result, dict) and "error" not in result:
            return result
        return None
    
    async def buy_number(self, country: str, service: str) -> Dict[str, Any]:
        """Raqam sotib olish"""
        result = await self._request("getNumber/", {
            "service": service,
            "country": country
        })
        
        if isinstance(result, dict):
            if "tel" in result:
                return {
                    "success": True,
                    "phone": result["tel"],
                    "order_id": result.get("idNum", ""),
                    "price": result.get("price", 0)
                }
            return {"success": False, "error": result.get("error", "Xatolik")}
        return {"success": False, "error": "Noma'lum xatolik"}
    
    async def get_sms(self, order_id: str) -> Dict[str, Any]:
        """SMS kodini olish"""
        result = await self._request("getSmsCode/", {"idNum": order_id})
        
        if isinstance(result, dict):
            if "smsCode" in result:
                return {
                    "success": True,
                    "code": result["smsCode"],
                    "status": "received"
                }
            return {"success": False, "status": "waiting"}
        return {"success": False, "status": "error"}
    
    async def cancel_number(self, order_id: str) -> Dict[str, Any]:
        """Raqamni bekor qilish"""
        result = await self._request("setStatus/", {
            "idNum": order_id,
            "status": "end"
        })
        return result


class FiveSim:
    """5SIM.NET API"""
    
    BASE_URL = "https://5sim.net/v1"
    
    def __init__(self):
        self.api_key = FIVESIM_API_KEY
    
    async def _request(self, endpoint: str, method: str = "GET") -> Dict[str, Any]:
        """API so'rov"""
        url = f"{self.BASE_URL}/{endpoint}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                if method == "GET":
                    response = await client.get(url, headers=headers)
                else:
                    response = await client.post(url, headers=headers)
                
                if response.status_code == 200:
                    return response.json()
                return {"error": response.text}
        except Exception as e:
            return {"error": str(e)}
    
    async def get_balance(self) -> float:
        """Balansni olish (RUB)"""
        result = await self._request("user/profile")
        if isinstance(result, dict) and "balance" in result:
            return float(result["balance"])
        return 0.0
    
    async def get_prices(self, country: str, product: str) -> Optional[Dict[str, Any]]:
        """Narxlarni olish"""
        result = await self._request(f"guest/prices?country={country}&product={product}")
        return result if "error" not in result else None
    
    async def buy_number(self, country: str, product: str, operator: str = "any") -> Dict[str, Any]:
        """Raqam sotib olish"""
        result = await self._request(f"user/buy/activation/{country}/{operator}/{product}", "GET")
        
        if isinstance(result, dict):
            if "phone" in result:
                return {
                    "success": True,
                    "phone": result["phone"],
                    "order_id": str(result.get("id", "")),
                    "price": result.get("price", 0)
                }
            return {"success": False, "error": result.get("error", "Xatolik")}
        return {"success": False, "error": "Noma'lum xatolik"}
    
    async def check_order(self, order_id: str) -> Dict[str, Any]:
        """Buyurtma holatini tekshirish"""
        result = await self._request(f"user/check/{order_id}")
        
        if isinstance(result, dict):
            if result.get("sms"):
                sms = result["sms"][0] if result["sms"] else {}
                return {
                    "success": True,
                    "code": sms.get("code", ""),
                    "status": result.get("status", "")
                }
            return {"success": False, "status": result.get("status", "waiting")}
        return {"success": False, "status": "error"}
    
    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Buyurtmani bekor qilish"""
        return await self._request(f"user/cancel/{order_id}")


class MultiSMS:
    """Ko'p SMS provider boshqaruvi"""
    
    def __init__(self):
        self.providers = {}
        
        if SMS_API_KEY:
            self.providers['vaksms'] = VakSMS()
        
        if FIVESIM_API_KEY:
            self.providers['fivesim'] = FiveSim()
    
    async def get_all_balances(self) -> Dict[str, float]:
        """Barcha providerlar balansini olish"""
        balances = {}
        for name, provider in self.providers.items():
            try:
                balances[name] = await provider.get_balance()
            except:
                balances[name] = 0.0
        return balances
    
    async def get_prices(self, platform: str, country: str) -> List[Dict[str, Any]]:
        """Barcha providerlardan narxlarni olish"""
        prices = []
        rate = get_rub_rate()
        markup = 1 + (get_markup_percent() / 100)
        
        # VakSMS
        if 'vaksms' in self.providers:
            try:
                result = await self.providers['vaksms'].get_price(platform, country)
                if result:
                    price_rub = float(result.get("price", 0))
                    prices.append({
                        "provider": "vaksms",
                        "provider_name": "VAK-SMS",
                        "price_rub": price_rub,
                        "price_uzs": int(price_rub * rate * markup),
                        "available": result.get("count", 0)
                    })
            except:
                pass
        
        # 5SIM
        if 'fivesim' in self.providers:
            try:
                # 5SIM uses different service codes
                fivesim_product = self._convert_to_fivesim_product(platform)
                fivesim_country = self._convert_to_fivesim_country(country)
                
                result = await self.providers['fivesim'].get_prices(fivesim_country, fivesim_product)
                if result:
                    for operator, data in result.items():
                        if isinstance(data, dict) and "cost" in data:
                            price_rub = float(data["cost"])
                            prices.append({
                                "provider": "fivesim",
                                "provider_name": f"5SIM ({operator})",
                                "price_rub": price_rub,
                                "price_uzs": int(price_rub * rate * markup),
                                "available": data.get("count", 0)
                            })
                            break  # Faqat eng arzonini olish
            except:
                pass
        
        return sorted(prices, key=lambda x: x["price_uzs"])
    
    async def buy_number(self, provider: str, platform: str, country: str) -> Dict[str, Any]:
        """Raqam sotib olish"""
        if provider == "vaksms" and "vaksms" in self.providers:
            return await self.providers['vaksms'].buy_number(country, platform)
        elif provider == "fivesim" and "fivesim" in self.providers:
            fivesim_product = self._convert_to_fivesim_product(platform)
            fivesim_country = self._convert_to_fivesim_country(country)
            return await self.providers['fivesim'].buy_number(fivesim_country, fivesim_product)
        
        return {"success": False, "error": "Provider topilmadi"}
    
    async def get_sms(self, provider: str, order_id: str) -> Dict[str, Any]:
        """SMS kodini olish"""
        if provider == "vaksms" and "vaksms" in self.providers:
            return await self.providers['vaksms'].get_sms(order_id)
        elif provider == "fivesim" and "fivesim" in self.providers:
            return await self.providers['fivesim'].check_order(order_id)
        
        return {"success": False, "status": "error"}
    
    async def cancel_order(self, provider: str, order_id: str) -> Dict[str, Any]:
        """Buyurtmani bekor qilish"""
        if provider == "vaksms" and "vaksms" in self.providers:
            return await self.providers['vaksms'].cancel_number(order_id)
        elif provider == "fivesim" and "fivesim" in self.providers:
            return await self.providers['fivesim'].cancel_order(order_id)
        
        return {"error": "Provider topilmadi"}
    
    def _convert_to_fivesim_product(self, platform: str) -> str:
        """Platform kodini 5SIM formatiga o'tkazish"""
        mapping = {
            "tg": "telegram",
            "ig": "instagram",
            "wa": "whatsapp",
            "go": "google",
            "ya": "yandex",
            "tt": "tiktok",
            "fb": "facebook",
            "tw": "twitter",
            "ds": "discord",
            "oi": "openai",
        }
        return mapping.get(platform, platform)
    
    def _convert_to_fivesim_country(self, country: str) -> str:
        """Davlat kodini 5SIM formatiga o'tkazish"""
        mapping = {
            "ru": "russia",
            "ua": "ukraine",
            "kz": "kazakhstan",
            "uz": "uzbekistan",
            "tj": "tajikistan",
            "kg": "kyrgyzstan",
            "id": "indonesia",
            "ph": "philippines",
            "vn": "vietnam",
            "bd": "bangladesh",
            "in": "india",
            "ge": "georgia",
        }
        return mapping.get(country, country)


# Global instance
sms_api = MultiSMS()
