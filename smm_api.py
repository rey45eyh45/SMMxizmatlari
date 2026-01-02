# -*- coding: utf-8 -*-
"""
PROFESSIONAL SMM PANEL API INTEGRATSIYASI
Multi-Panel qo'llab-quvvatlash: Peakerr + SMMMain
Eng arzon narxlarni avtomatik tanlash
+ CACHE TIZIMI - 10x tezlik!
"""

import requests
from config import SMM_API_KEY, SMM_API_URL

# Cache import
try:
    from cache import services_cache, balance_cache, cached
except ImportError:
    # Cache mavjud bo'lmasa oddiy ishlaydi
    services_cache = None
    balance_cache = None
    cached = lambda *args, **kwargs: lambda f: f

# SMMMain API konfiguratsiyasi
try:
    from config import SMMMAIN_API_KEY, SMMMAIN_API_URL
except ImportError:
    SMMMAIN_API_KEY = ""
    SMMMAIN_API_URL = "https://smmmain.com/api/v2"


class SMMPanel:
    """Asosiy SMM Panel API class"""
    
    def __init__(self, api_url=None, api_key=None, name="Peakerr"):
        self.api_key = api_key or SMM_API_KEY
        self.api_url = api_url or SMM_API_URL
        self.name = name
    
    def _make_request(self, data):
        """API so'rov yuborish"""
        data['key'] = self.api_key
        try:
            response = requests.post(self.api_url, data=data, timeout=30)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_services(self, use_cache=True):
        """Barcha xizmatlar ro'yxatini olish (CACHED)"""
        cache_key = f"services:{self.name}"
        
        # Cache dan olish
        if use_cache and services_cache:
            cached_data = services_cache.get(cache_key)
            if cached_data is not None:
                return cached_data
        
        # API dan olish
        result = self._make_request({'action': 'services'})
        
        # Cache ga saqlash (1 soat)
        if services_cache and not isinstance(result, dict) or 'error' not in result:
            services_cache.set(cache_key, result, ttl=3600)
        
        return result
    
    def get_balance(self, use_cache=True):
        """Panel balansingizni tekshirish (CACHED - 1 daqiqa)"""
        cache_key = f"balance:{self.name}"
        
        # Cache dan olish
        if use_cache and balance_cache:
            cached_data = balance_cache.get(cache_key)
            if cached_data is not None:
                return cached_data
        
        # API dan olish
        result = self._make_request({'action': 'balance'})
        balance = 0.0
        if 'balance' in result:
            balance = float(result['balance'])
        
        # Cache ga saqlash (1 daqiqa)
        if balance_cache:
            balance_cache.set(cache_key, balance, ttl=60)
        
        return balance
    
    def add_order(self, service_id, link, quantity):
        """Yangi buyurtma qo'shish"""
        data = {
            'action': 'add',
            'service': service_id,
            'link': link,
            'quantity': quantity
        }
        return self._make_request(data)
    
    def get_order_status(self, order_id):
        """Buyurtma holatini tekshirish"""
        return self._make_request({'action': 'status', 'order': order_id})
    
    def get_multiple_orders_status(self, order_ids):
        """Bir nechta buyurtma holatini tekshirish"""
        return self._make_request({
            'action': 'status',
            'orders': ','.join(map(str, order_ids))
        })
    
    def cancel_order(self, order_id):
        """Buyurtmani bekor qilish"""
        return self._make_request({'action': 'cancel', 'order': order_id})
    
    def refill_order(self, order_id):
        """Buyurtmani qayta to'ldirish"""
        return self._make_request({'action': 'refill', 'order': order_id})


class MultiPanel:
    """
    Multi-Panel Menejer
    Bir nechta SMM Panel'larni boshqarish va eng arzon narxlarni topish
    """
    
    def __init__(self):
        # Asosiy panellar
        self.panels = {}
        
        # Peakerr (Asosiy)
        if SMM_API_KEY:
            self.panels['peakerr'] = SMMPanel(
                api_url=SMM_API_URL,
                api_key=SMM_API_KEY,
                name="Peakerr"
            )
        
        # SMMMain (Ikkinchi)
        if SMMMAIN_API_KEY:
            self.panels['smmmain'] = SMMPanel(
                api_url=SMMMAIN_API_URL,
                api_key=SMMMAIN_API_KEY,
                name="SMMMain"
            )
    
    def get_panel(self, panel_name):
        """Panel olish"""
        return self.panels.get(panel_name.lower())
    
    def get_all_balances(self):
        """Barcha panellar balansini olish"""
        balances = {}
        for name, panel in self.panels.items():
            try:
                balances[name] = {
                    'name': panel.name,
                    'balance': panel.get_balance()
                }
            except:
                balances[name] = {'name': panel.name, 'balance': 0.0}
        return balances
    
    def place_order(self, panel_name, service_id, link, quantity):
        """Belgilangan panelga buyurtma yuborish"""
        panel = self.get_panel(panel_name)
        if not panel:
            return {"success": False, "error": f"Panel topilmadi: {panel_name}"}
        
        result = panel.add_order(service_id, link, quantity)
        
        if 'order' in result:
            return {
                "success": True, 
                "order_id": result['order'],
                "panel": panel_name
            }
        elif 'error' in result:
            return {"success": False, "error": result['error']}
        else:
            return {"success": False, "error": "Noma'lum xato"}
    
    def check_order(self, panel_name, order_id):
        """Buyurtma holatini tekshirish"""
        panel = self.get_panel(panel_name)
        if not panel:
            return {"error": f"Panel topilmadi: {panel_name}"}
        return panel.get_order_status(order_id)


# ==================== XIZMATLAR MAPPING ====================
# Har bir xizmat uchun qaysi paneldan olish kerakligini belgilash

SERVICES_MAPPING = {
    # ===== TELEGRAM MEMBERS =====
    "tg_subscriber": {
        "panel": "peakerr",
        "service_id": 1495,
        "name": "Obunachi",
        "price_usd": 0.08,
        "min": 10, "max": 10000
    },
    "tg_subscriber_20d": {
        "panel": "peakerr",
        "service_id": 3890,
        "name": "Obunachi ✅ 20 kun",
        "price_usd": 0.345,
        "min": 10, "max": 50000
    },
    "tg_subscriber_30d": {
        "panel": "peakerr",
        "service_id": 7025,
        "name": "Obunachi ✅ 30 kun",
        "price_usd": 0.49,
        "min": 10, "max": 300000
    },
    "tg_subscriber_nodrop": {
        "panel": "peakerr",
        "service_id": 6898,
        "name": "Zero Drop (Tushmaslik)",
        "price_usd": 0.90,
        "min": 500, "max": 100000
    },
    
    # SMMMain - O'zbekiston targetli
    "tg_subscriber_uz": {
        "panel": "smmmain",
        "service_id": 78,
        "name": "🇺🇿 O'zbekiston Members",
        "price_usd": 0.59,
        "min": 500, "max": 50000
    },
    "tg_subscriber_ru": {
        "panel": "smmmain",
        "service_id": 79,
        "name": "🇷🇺 Rossiya Members",
        "price_usd": 0.59,
        "min": 500, "max": 100000
    },
    "tg_subscriber_usa": {
        "panel": "smmmain",
        "service_id": 36,
        "name": "🇺🇸 AQSh Members",
        "price_usd": 1.10,
        "min": 500, "max": 500000
    },
    
    # ===== TELEGRAM PREMIUM MEMBERS =====
    "tg_premium": {
        "panel": "peakerr",
        "service_id": 6882,
        "name": "Premium Obunachi 7 kun",
        "price_usd": 4.77,
        "min": 10, "max": 70000
    },
    "tg_premium_30d": {
        "panel": "smmmain",
        "service_id": 606,
        "name": "Premium⭐️ 15-30 kun",
        "price_usd": 5.99,
        "min": 500, "max": 60000
    },
    
    # ===== TELEGRAM VIEWS =====
    "tg_view": {
        "panel": "peakerr",
        "service_id": 99,
        "name": "Ko'rish",
        "price_usd": 0.0026,
        "min": 50, "max": 20000
    },
    "tg_view_nodrop": {
        "panel": "smmmain",
        "service_id": 41,
        "name": "Ko'rish (Cheapest)",
        "price_usd": 0.004,
        "min": 10, "max": 400000
    },
    "tg_view_5posts": {
        "panel": "smmmain",
        "service_id": 3,
        "name": "Ko'rish (5 post)",
        "price_usd": 0.03,
        "min": 10, "max": 10000000
    },
    
    # ===== TELEGRAM REACTIONS =====
    "tg_reaction_positive": {
        "panel": "smmmain",
        "service_id": 191,
        "name": "Reaction (Positive 👍❤️🔥)",
        "price_usd": 0.10,
        "min": 50, "max": 1000000
    },
    "tg_reaction_negative": {
        "panel": "smmmain",
        "service_id": 192,
        "name": "Reaction (Negative 👎😢)",
        "price_usd": 0.10,
        "min": 50, "max": 1000000
    },
    "tg_reaction_like": {
        "panel": "peakerr",
        "service_id": 6814,
        "name": "Reaction 👍",
        "price_usd": 0.12,
        "min": 10, "max": 100000
    },
    "tg_reaction_fire": {
        "panel": "peakerr",
        "service_id": 6815,
        "name": "Reaction 🔥",
        "price_usd": 0.12,
        "min": 10, "max": 100000
    },
    "tg_reaction_heart": {
        "panel": "peakerr",
        "service_id": 6816,
        "name": "Reaction ❤️",
        "price_usd": 0.12,
        "min": 10, "max": 100000
    },
    
    # ===== TELEGRAM SHARE/FORWARD =====
    "tg_share": {
        "panel": "smmmain",
        "service_id": 220,
        "name": "Share Post",
        "price_usd": 0.04,
        "min": 10, "max": 1000000
    },
    
    # ===== TELEGRAM VOTE/POLL =====
    "tg_vote": {
        "panel": "smmmain",
        "service_id": 10,
        "name": "Vote/Poll",
        "price_usd": 0.25,
        "min": 10, "max": 300000
    },
    
    # ===== INSTAGRAM =====
    "ig_followers": {
        "panel": "peakerr",
        "service_id": 9,
        "name": "Followers",
        "price_usd": 0.09,
        "min": 10, "max": 500000
    },
    "ig_likes": {
        "panel": "peakerr",
        "service_id": 1,
        "name": "Likes",
        "price_usd": 0.015,
        "min": 10, "max": 80000
    },
    "ig_views": {
        "panel": "peakerr",
        "service_id": 161,
        "name": "Views",
        "price_usd": 0.01,
        "min": 100, "max": 10000000
    },
    "ig_comments": {
        "panel": "peakerr",
        "service_id": 6600,
        "name": "Comments (Random)",
        "price_usd": 0.70,
        "min": 5, "max": 50000
    },
    
    # ===== YOUTUBE =====
    "yt_subscribers": {
        "panel": "peakerr",
        "service_id": 7088,
        "name": "Subscribers",
        "price_usd": 1.20,
        "min": 50, "max": 100000
    },
    "yt_views": {
        "panel": "peakerr",
        "service_id": 5316,
        "name": "Views",
        "price_usd": 0.80,
        "min": 100, "max": 1000000
    },
    "yt_likes": {
        "panel": "peakerr",
        "service_id": 5328,
        "name": "Likes",
        "price_usd": 1.00,
        "min": 50, "max": 100000
    },
    
    # ===== TIKTOK =====
    "tt_followers": {
        "panel": "peakerr",
        "service_id": 6270,
        "name": "Followers",
        "price_usd": 0.40,
        "min": 100, "max": 1000000
    },
    "tt_likes": {
        "panel": "peakerr",
        "service_id": 1597,
        "name": "Likes",
        "price_usd": 0.05,
        "min": 100, "max": 500000
    },
    "tt_views": {
        "panel": "peakerr",
        "service_id": 1581,
        "name": "Views",
        "price_usd": 0.015,
        "min": 100, "max": 10000000
    },
    
    # ===== FACEBOOK =====
    "fb_followers": {
        "panel": "peakerr",
        "service_id": 6044,
        "name": "Page Followers",
        "price_usd": 0.75,
        "min": 100, "max": 1000000
    },
    "fb_likes": {
        "panel": "peakerr",
        "service_id": 2920,
        "name": "Post Likes",
        "price_usd": 0.20,
        "min": 20, "max": 50000
    },
    
    # ===== TWITTER/X =====
    "tw_followers": {
        "panel": "peakerr",
        "service_id": 4746,
        "name": "Followers",
        "price_usd": 0.55,
        "min": 100, "max": 1000000
    },
    "tw_likes": {
        "panel": "peakerr",
        "service_id": 7098,
        "name": "Likes",
        "price_usd": 0.30,
        "min": 10, "max": 100000
    },
    
    # ===== SPOTIFY =====
    "sp_followers": {
        "panel": "peakerr",
        "service_id": 5952,
        "name": "Followers",
        "price_usd": 0.40,
        "min": 100, "max": 1000000
    },
    "sp_plays": {
        "panel": "peakerr",
        "service_id": 4706,
        "name": "Plays",
        "price_usd": 0.50,
        "min": 1000, "max": 10000000
    },
}


# ==================== HELPER FUNCTIONS ====================

# Global multi-panel instance
multi_panel = MultiPanel()


def place_smm_order(service_key, link, quantity):
    """
    Xizmat kaliti bo'yicha buyurtma yuborish
    
    Args:
        service_key: Xizmat kaliti (masalan: "tg_subscriber")
        link: Kanal/profil havolasi
        quantity: Miqdor
    
    Returns:
        dict: {"success": True, "order_id": 12345, "panel": "peakerr"}
    """
    # Xizmat ma'lumotlarini olish
    service = SERVICES_MAPPING.get(service_key)
    
    if not service:
        return {"success": False, "error": f"Xizmat topilmadi: {service_key}"}
    
    panel_name = service['panel']
    service_id = service['service_id']
    
    # Buyurtma yuborish
    return multi_panel.place_order(panel_name, service_id, link, quantity)


def place_order_direct(panel_name, service_id, link, quantity):
    """To'g'ridan-to'g'ri panel va service_id bilan buyurtma"""
    return multi_panel.place_order(panel_name, service_id, link, quantity)


def check_order_status(order_id, panel_name="peakerr"):
    """Buyurtma holatini tekshirish"""
    return multi_panel.check_order(panel_name, order_id)


def get_panel_balance(panel_name=None):
    """Panel balansini olish
    
    Args:
        panel_name: "peakerr" yoki "smmmain" - None bo'lsa Peakerr qaytadi
    """
    if panel_name:
        panel = multi_panel.get_panel(panel_name)
        if panel:
            return panel.get_balance()
        return 0.0
    else:
        # Asosiy panel (Peakerr) balansi
        panel = multi_panel.get_panel("peakerr")
        if panel:
            return panel.get_balance()
        return 0.0


def get_all_balances():
    """Barcha panellar balansi - dict qaytaradi"""
    return multi_panel.get_all_balances()


def get_service_info(service_key):
    """Xizmat ma'lumotlarini olish"""
    return SERVICES_MAPPING.get(service_key)


def get_services_by_platform(platform):
    """Platforma bo'yicha xizmatlarni olish"""
    prefix_map = {
        "telegram": "tg_",
        "instagram": "ig_",
        "youtube": "yt_",
        "tiktok": "tt_",
        "facebook": "fb_",
        "twitter": "tw_",
        "spotify": "sp_"
    }
    
    prefix = prefix_map.get(platform.lower(), "")
    if not prefix:
        return {}
    
    return {k: v for k, v in SERVICES_MAPPING.items() if k.startswith(prefix)}


def place_smm_order(service_id, link, quantity, panel_name="peakerr"):
    """SMM buyurtma berish"""
    result = multi_panel.place_order(panel_name, service_id, link, quantity)
    return result


# Test
if __name__ == "__main__":
    print("=" * 60)
    print("MULTI-PANEL SMM API TEST")
    print("=" * 60)
    
    # Balanslar
    print("\n💰 PANEL BALANSLARI:")
    balances = get_all_balances()
    for name, data in balances.items():
        print(f"  {data['name']}: ${data['balance']:.2f}")
    
    # Telegram xizmatlari
    print("\n📱 TELEGRAM XIZMATLARI:")
    tg_services = get_services_by_platform("telegram")
    for key, service in tg_services.items():
        print(f"  {key}: {service['name']} - ${service['price_usd']}/1000 ({service['panel']})")
    
    print("\n" + "=" * 60)