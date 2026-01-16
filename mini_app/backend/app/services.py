# -*- coding: utf-8 -*-
"""
Xizmatlar konfiguratsiyasi - Telegram, Instagram, YouTube, TikTok
"""
from typing import Dict, Any, List, Optional, Tuple
from .database import Database


# USD va RUB kurslarini olish
def get_usd_rate() -> int:
    return int(Database.get_setting('usd_rate', '12900'))

def get_rub_rate() -> int:
    return int(Database.get_setting('rub_rate', '140'))

def get_markup_percent() -> int:
    return int(Database.get_setting('markup_percent', '20'))


# ==================== PLATFORMALAR ====================

PLATFORMS = {
    "telegram": {
        "id": "telegram",
        "name": "Telegram",
        "emoji": "✈️",
        "color": "#0088cc"
    },
    "instagram": {
        "id": "instagram",
        "name": "Instagram",
        "emoji": "📸",
        "color": "#E1306C"
    },
    "youtube": {
        "id": "youtube",
        "name": "YouTube",
        "emoji": "▶️",
        "color": "#FF0000"
    },
    "tiktok": {
        "id": "tiktok",
        "name": "TikTok",
        "emoji": "🎵",
        "color": "#000000"
    },
    "sms": {
        "id": "sms",
        "name": "Virtual Raqamlar",
        "emoji": "📱",
        "color": "#4CAF50"
    }
}


# ==================== TELEGRAM XIZMATLARI ====================

TELEGRAM_SERVICES = {
    # ========== OBUNACHI ==========
    "tg_member_cheap": {
        "name": "Obunachi (Arzon)",
        "description": "Eng arzon obunachi - tez yetkazish",
        "category": "members",
        "peakerr": {"id": 15050, "price_usd": 0.081},
        "smmmain": {"id": 48, "price_usd": 0.59},
        "min": 10, "max": 20000, "guarantee": "Yo'q", "speed": "5-10K/kun"
    },
    "tg_member_30day": {
        "name": "Obunachi (30 kun kafolat)",
        "description": "30 kunlik kafolat bilan obunachi",
        "category": "members",
        "peakerr": {"id": 13896, "price_usd": 0.66},
        "smmmain": {"id": 48, "price_usd": 0.59},
        "min": 100, "max": 100000, "guarantee": "30 kun", "speed": "5K/kun"
    },
    "tg_member_60day": {
        "name": "Obunachi (60 kun kafolat)",
        "description": "60 kunlik kafolat bilan obunachi",
        "category": "members",
        "peakerr": {"id": 15530, "price_usd": 0.78},
        "smmmain": {"id": 49, "price_usd": 0.64},
        "min": 100, "max": 50000, "guarantee": "60 kun", "speed": "3K/kun"
    },
    "tg_member_90day": {
        "name": "Obunachi (90 kun kafolat)",
        "description": "90 kunlik kafolat bilan obunachi",
        "category": "members",
        "peakerr": {"id": 15573, "price_usd": 1.09},
        "smmmain": {"id": 51, "price_usd": 0.69},
        "min": 100, "max": 50000, "guarantee": "90 kun", "speed": "2K/kun"
    },
    "tg_member_nodrop": {
        "name": "Obunachi (No Drop)",
        "description": "Tushmaydigan obunachi - eng sifatli",
        "category": "members",
        "peakerr": {"id": 15754, "price_usd": 1.18},
        "smmmain": {"id": 67, "price_usd": 1.31},
        "min": 100, "max": 100000, "guarantee": "Umrbod", "speed": "2K/kun"
    },
    "tg_member_real": {
        "name": "Real Obunachi",
        "description": "Haqiqiy faol foydalanuvchilar",
        "category": "members",
        "peakerr": {"id": 14453, "price_usd": 0.82},
        "smmmain": {"id": 69, "price_usd": 1.35},
        "min": 50, "max": 50000, "guarantee": "60 kun", "speed": "1K/kun"
    },
    "tg_member_high": {
        "name": "Yuqori sifatli Obunachi",
        "description": "High Quality - eng yaxshi sifat",
        "category": "members",
        "peakerr": {"id": 15756, "price_usd": 1.36},
        "smmmain": {"id": 58, "price_usd": 1.28},
        "min": 100, "max": 100000, "guarantee": "60 kun", "speed": "3K/kun"
    },
    "tg_member_premium": {
        "name": "Premium Obunachi",
        "description": "Telegram Premium foydalanuvchilar",
        "category": "members",
        "peakerr": {"id": 19081, "price_usd": 9.23},
        "smmmain": {"id": 607, "price_usd": 2.99},
        "min": 10, "max": 20000, "guarantee": "7-14 kun", "speed": "500/kun"
    },
    
    # ========== KO'RISH ==========
    "tg_view_cheap": {
        "name": "Ko'rish (Eng arzon)",
        "description": "Eng arzon post ko'rish",
        "category": "views",
        "peakerr": {"id": 23471, "price_usd": 0.0052},
        "smmmain": {"id": 41, "price_usd": 0.004},
        "min": 100, "max": 50000000, "guarantee": "Kafolatli", "speed": "1M/soat"
    },
    "tg_view_instant": {
        "name": "Ko'rish (Instant)",
        "description": "Darhol yetkazish",
        "category": "views",
        "peakerr": {"id": 13290, "price_usd": 0.006},
        "smmmain": {"id": 41, "price_usd": 0.004},
        "min": 100, "max": 100000000, "guarantee": "Kafolatli", "speed": "Super tez"
    },
    "tg_view_fast": {
        "name": "Ko'rish (Tez)",
        "description": "Tez yetkazish - 20K/soat",
        "category": "views",
        "peakerr": {"id": 1368, "price_usd": 0.0073},
        "smmmain": {"id": 41, "price_usd": 0.004},
        "min": 100, "max": 100000, "guarantee": "Kafolatli", "speed": "20K/soat"
    },
    "tg_view_last10": {
        "name": "So'nggi 10 Post Ko'rish",
        "description": "Oxirgi 10 postga avtomatik ko'rish",
        "category": "views",
        "peakerr": {"id": 9094, "price_usd": 0.0195},
        "smmmain": {"id": 42, "price_usd": 0.30},
        "min": 100, "max": 500000, "guarantee": "Kafolatli", "speed": "50K/soat"
    },
    "tg_story_view": {
        "name": "Story Ko'rish",
        "description": "Story/Hikoyalarga ko'rish",
        "category": "views",
        "peakerr": {"id": 15958, "price_usd": 0.091},
        "smmmain": {"id": 640, "price_usd": 0.10},
        "min": 100, "max": 100000, "guarantee": "Kafolatli", "speed": "50K/soat"
    },
    
    # ========== REAKSIYALAR ==========
    "tg_reaction_like": {
        "name": "👍 Like Reaksiya",
        "description": "Faqat 👍 like reaksiya",
        "category": "reactions",
        "peakerr": {"id": 12312, "price_usd": 0.1545},
        "smmmain": {"id": 180, "price_usd": 0.10},
        "min": 10, "max": 1000000, "guarantee": "Yo'q", "speed": "100K/soat"
    },
    "tg_reaction_heart": {
        "name": "❤️ Heart Reaksiya",
        "description": "Faqat ❤️ yurak reaksiya",
        "category": "reactions",
        "peakerr": {"id": 12312, "price_usd": 0.1545},
        "smmmain": {"id": 182, "price_usd": 0.10},
        "min": 10, "max": 1000000, "guarantee": "Yo'q", "speed": "100K/soat"
    },
    "tg_reaction_fire": {
        "name": "🔥 Fire Reaksiya",
        "description": "Faqat 🔥 olov reaksiya",
        "category": "reactions",
        "peakerr": {"id": 12312, "price_usd": 0.1545},
        "smmmain": {"id": 183, "price_usd": 0.10},
        "min": 10, "max": 1000000, "guarantee": "Yo'q", "speed": "100K/soat"
    },
    "tg_reaction_premium": {
        "name": "⭐ Premium Reaksiya",
        "description": "Premium emoji reaksiya",
        "category": "reactions",
        "peakerr": {"id": 15396, "price_usd": 0.0878},
        "smmmain": {"id": 180, "price_usd": 0.10},
        "min": 10, "max": 100000, "guarantee": "Yo'q", "speed": "30K/soat"
    },
    
    # ========== SHARE ==========
    "tg_share": {
        "name": "Share/Ulashish",
        "description": "Postni boshqalarga ulashish",
        "category": "other",
        "peakerr": {"id": 16052, "price_usd": 0.0156},
        "smmmain": {"id": 42, "price_usd": 0.30},
        "min": 100, "max": 1000000, "guarantee": "Yo'q", "speed": "50K/kun"
    },
    "tg_vote": {
        "name": "So'rovnoma ovozi",
        "description": "So'rovnomaga ovoz berish",
        "category": "other",
        "peakerr": {"id": 13291, "price_usd": 0.339},
        "smmmain": {"id": 42, "price_usd": 0.30},
        "min": 100, "max": 300000, "guarantee": "Yo'q", "speed": "10K/soat"
    },
}


# ==================== INSTAGRAM XIZMATLARI ====================

INSTAGRAM_SERVICES = {
    "ig_follower": {
        "name": "Follower",
        "description": "Real ko'rinishdagi follower",
        "category": "followers",
        "peakerr": {"id": 16350, "price_usd": 0.47},
        "smmmain": {"id": 1105, "price_usd": 0.52},
        "min": 50, "max": 100000, "guarantee": "30 kun", "speed": "10K/kun"
    },
    "ig_follower_premium": {
        "name": "Premium Follower",
        "description": "Yuqori sifatli, faol follower",
        "category": "followers",
        "peakerr": {"id": 16355, "price_usd": 0.80},
        "smmmain": {"id": 1106, "price_usd": 0.85},
        "min": 50, "max": 50000, "guarantee": "60 kun", "speed": "5K/kun"
    },
    "ig_like": {
        "name": "Like",
        "description": "Postlarga like",
        "category": "likes",
        "peakerr": {"id": 27278, "price_usd": 0.137},
        "smmmain": {"id": 1109, "price_usd": 0.14},
        "min": 10, "max": 100000, "guarantee": "Yo'q", "speed": "100K/kun"
    },
    "ig_view": {
        "name": "Video Ko'rish",
        "description": "Reels va videolarga ko'rish",
        "category": "views",
        "peakerr": {"id": 19865, "price_usd": 0.0011},
        "smmmain": {"id": 1115, "price_usd": 0.002},
        "min": 100, "max": 10000000, "guarantee": "Kafolatli", "speed": "1M/soat"
    },
    "ig_reel_view": {
        "name": "Reels Ko'rish",
        "description": "Faqat Reels videolarga",
        "category": "views",
        "peakerr": {"id": 19870, "price_usd": 0.0008},
        "smmmain": {"id": 1116, "price_usd": 0.001},
        "min": 100, "max": 50000000, "guarantee": "Kafolatli", "speed": "5M/soat"
    },
    "ig_story_view": {
        "name": "Story Ko'rish",
        "description": "Story'larga ko'rish",
        "category": "views",
        "peakerr": {"id": 19875, "price_usd": 0.003},
        "smmmain": {"id": 1117, "price_usd": 0.004},
        "min": 100, "max": 500000, "guarantee": "Kafolatli", "speed": "100K/soat"
    },
    "ig_comment": {
        "name": "Izoh",
        "description": "Postlarga izoh",
        "category": "comments",
        "peakerr": {"id": 19880, "price_usd": 0.50},
        "smmmain": {"id": 1120, "price_usd": 0.55},
        "min": 5, "max": 10000, "guarantee": "Yo'q", "speed": "1K/kun"
    },
    "ig_save": {
        "name": "Saqlash",
        "description": "Postlarni saqlash",
        "category": "other",
        "peakerr": {"id": 19890, "price_usd": 0.20},
        "smmmain": {"id": 1125, "price_usd": 0.22},
        "min": 10, "max": 50000, "guarantee": "Yo'q", "speed": "10K/kun"
    },
}


# ==================== YOUTUBE XIZMATLARI ====================

YOUTUBE_SERVICES = {
    "yt_subscriber": {
        "name": "Subscriber",
        "description": "Kanalingizga obuna",
        "category": "subscribers",
        "peakerr": {"id": 23304, "price_usd": 0.15},
        "smmmain": {"id": 1201, "price_usd": 0.20},
        "min": 50, "max": 100000, "guarantee": "30 kun", "speed": "5K/kun"
    },
    "yt_view": {
        "name": "Ko'rish",
        "description": "Videolarga ko'rish",
        "category": "views",
        "peakerr": {"id": 27356, "price_usd": 0.042},
        "smmmain": {"id": 1205, "price_usd": 0.05},
        "min": 100, "max": 1000000, "guarantee": "Kafolatli", "speed": "50K/kun"
    },
    "yt_like": {
        "name": "Like",
        "description": "Videolarga like",
        "category": "likes",
        "peakerr": {"id": 20363, "price_usd": 0.078},
        "smmmain": {"id": 1209, "price_usd": 0.09},
        "min": 10, "max": 100000, "guarantee": "30 kun", "speed": "50K/kun"
    },
    "yt_comment": {
        "name": "Izoh",
        "description": "Videolarga izoh",
        "category": "comments",
        "peakerr": {"id": 20370, "price_usd": 0.80},
        "smmmain": {"id": 1215, "price_usd": 0.90},
        "min": 5, "max": 5000, "guarantee": "Yo'q", "speed": "500/kun"
    },
    "yt_share": {
        "name": "Ulashish",
        "description": "Videolarni ulashish",
        "category": "other",
        "peakerr": {"id": 20380, "price_usd": 0.05},
        "smmmain": {"id": 1220, "price_usd": 0.06},
        "min": 100, "max": 100000, "guarantee": "Yo'q", "speed": "50K/kun"
    },
}


# ==================== TIKTOK XIZMATLARI ====================

TIKTOK_SERVICES = {
    "tt_follower": {
        "name": "Follower",
        "description": "Profilingizga follower",
        "category": "followers",
        "peakerr": {"id": 28047, "price_usd": 0.22},
        "smmmain": {"id": 1301, "price_usd": 0.25},
        "min": 50, "max": 500000, "guarantee": "30 kun", "speed": "20K/kun"
    },
    "tt_view": {
        "name": "Ko'rish",
        "description": "Videolarga ko'rish",
        "category": "views",
        "peakerr": {"id": 14075, "price_usd": 0.0002},
        "smmmain": {"id": 1305, "price_usd": 0.0005},
        "min": 100, "max": 100000000, "guarantee": "Kafolatli", "speed": "10M/soat"
    },
    "tt_like": {
        "name": "Like",
        "description": "Videolarga like",
        "category": "likes",
        "peakerr": {"id": 25003, "price_usd": 0.022},
        "smmmain": {"id": 1309, "price_usd": 0.03},
        "min": 50, "max": 1000000, "guarantee": "Yo'q", "speed": "100K/kun"
    },
    "tt_comment": {
        "name": "Izoh",
        "description": "Videolarga izoh",
        "category": "comments",
        "peakerr": {"id": 25010, "price_usd": 0.60},
        "smmmain": {"id": 1315, "price_usd": 0.70},
        "min": 5, "max": 10000, "guarantee": "Yo'q", "speed": "1K/kun"
    },
    "tt_share": {
        "name": "Ulashish",
        "description": "Videolarni ulashish",
        "category": "other",
        "peakerr": {"id": 25020, "price_usd": 0.03},
        "smmmain": {"id": 1320, "price_usd": 0.04},
        "min": 100, "max": 1000000, "guarantee": "Yo'q", "speed": "100K/kun"
    },
    "tt_save": {
        "name": "Saqlash",
        "description": "Videolarni saqlash",
        "category": "other",
        "peakerr": {"id": 25025, "price_usd": 0.04},
        "smmmain": {"id": 1325, "price_usd": 0.05},
        "min": 50, "max": 500000, "guarantee": "Yo'q", "speed": "50K/kun"
    },
}


# ==================== SMS PLATFORMALARI ====================

SMS_PLATFORMS = {
    "tg": {"name": "Telegram", "emoji": "📱"},
    "ig": {"name": "Instagram", "emoji": "📷"},
    "wa": {"name": "WhatsApp", "emoji": "💬"},
    "go": {"name": "Google/Gmail", "emoji": "🔍"},
    "ya": {"name": "Yandex", "emoji": "🔴"},
    "tt": {"name": "TikTok", "emoji": "🎵"},
    "fb": {"name": "Facebook", "emoji": "📘"},
    "tw": {"name": "Twitter/X", "emoji": "🐦"},
    "ds": {"name": "Discord", "emoji": "🎮"},
    "oi": {"name": "OpenAI/ChatGPT", "emoji": "🤖"},
}

SMS_COUNTRIES = {
    "ru": {"name": "Rossiya", "flag": "🇷🇺"},
    "ua": {"name": "Ukraina", "flag": "🇺🇦"},
    "kz": {"name": "Qozog'iston", "flag": "🇰🇿"},
    "uz": {"name": "O'zbekiston", "flag": "🇺🇿"},
    "tj": {"name": "Tojikiston", "flag": "🇹🇯"},
    "kg": {"name": "Qirg'iziston", "flag": "🇰🇬"},
    "id": {"name": "Indoneziya", "flag": "🇮🇩"},
    "ph": {"name": "Filippin", "flag": "🇵🇭"},
    "vn": {"name": "Vetnam", "flag": "🇻🇳"},
    "bd": {"name": "Bangladesh", "flag": "🇧🇩"},
    "in": {"name": "Hindiston", "flag": "🇮🇳"},
    "ge": {"name": "Gruziya", "flag": "🇬🇪"},
}


# ==================== PREMIUM TARIFLAR ====================

PREMIUM_PLANS = {
    1: {"months": 1, "price": 52000, "original_price": 60000},
    3: {"months": 3, "price": 156000, "original_price": 180000},
    6: {"months": 6, "price": 270000, "original_price": 360000, "popular": True},
    12: {"months": 12, "price": 415000, "original_price": 720000, "best_value": True},
}


# ==================== BARCHA XIZMATLAR ====================

ALL_SERVICES: Dict[str, Dict[str, Any]] = {}
ALL_SERVICES.update({k: {**v, "platform": "telegram"} for k, v in TELEGRAM_SERVICES.items()})
ALL_SERVICES.update({k: {**v, "platform": "instagram"} for k, v in INSTAGRAM_SERVICES.items()})
ALL_SERVICES.update({k: {**v, "platform": "youtube"} for k, v in YOUTUBE_SERVICES.items()})
ALL_SERVICES.update({k: {**v, "platform": "tiktok"} for k, v in TIKTOK_SERVICES.items()})


# ==================== HELPER FUNKSIYALAR ====================

def usd_to_uzs(usd_price: float) -> int:
    """USD dan UZS ga konvertatsiya"""
    rate = get_usd_rate()
    markup = 1 + (get_markup_percent() / 100)
    return int(usd_price * rate * markup)


def get_best_price(service_key: str) -> Tuple[Optional[str], Optional[int], int]:
    """Eng yaxshi narxni topish (panel, service_id, price_uzs)"""
    if service_key not in ALL_SERVICES:
        return None, None, 0
    
    service = ALL_SERVICES[service_key]
    peakerr = service.get("peakerr")
    smmmain = service.get("smmmain")
    
    best_panel = None
    best_price = float('inf')
    best_id = None
    
    if peakerr and peakerr["price_usd"] < best_price:
        best_price = peakerr["price_usd"]
        best_panel = "peakerr"
        best_id = peakerr["id"]
    
    if smmmain and smmmain["price_usd"] < best_price:
        best_price = smmmain["price_usd"]
        best_panel = "smmmain"
        best_id = smmmain["id"]
    
    if best_panel:
        return best_panel, best_id, usd_to_uzs(best_price)
    
    return None, None, 0


def get_service_info(service_key: str) -> Optional[Dict[str, Any]]:
    """Xizmat haqida to'liq ma'lumot"""
    if service_key not in ALL_SERVICES:
        return None
    
    service = ALL_SERVICES[service_key]
    panel, service_id, price = get_best_price(service_key)
    
    return {
        "id": service_key,
        "name": service["name"],
        "description": service["description"],
        "price_per_1000": price,
        "min_quantity": service["min"],
        "max_quantity": service["max"],
        "guarantee": service["guarantee"],
        "speed": service["speed"],
        "panel": panel,
        "panel_service_id": service_id,
        "category": service.get("category", "other"),
        "platform": service.get("platform", "unknown"),
    }


def get_services_by_platform(platform: str) -> List[Dict[str, Any]]:
    """Platforma bo'yicha xizmatlar"""
    services = []
    for key, service in ALL_SERVICES.items():
        if service.get("platform") == platform:
            info = get_service_info(key)
            if info:
                services.append(info)
    return sorted(services, key=lambda x: x["price_per_1000"])


def get_categories_by_platform(platform: str) -> List[Dict[str, Any]]:
    """Platforma bo'yicha kategoriyalar"""
    categories = {}
    for key, service in ALL_SERVICES.items():
        if service.get("platform") == platform:
            cat = service.get("category", "other")
            if cat not in categories:
                categories[cat] = {"id": cat, "count": 0}
            categories[cat]["count"] += 1
    
    # Kategoriya nomlari
    cat_names = {
        "members": {"name": "Obunachi", "emoji": "👥"},
        "followers": {"name": "Follower", "emoji": "👥"},
        "subscribers": {"name": "Subscriber", "emoji": "👥"},
        "views": {"name": "Ko'rish", "emoji": "👁"},
        "likes": {"name": "Like", "emoji": "❤️"},
        "reactions": {"name": "Reaksiya", "emoji": "👍"},
        "comments": {"name": "Izoh", "emoji": "💬"},
        "other": {"name": "Boshqa", "emoji": "📦"},
    }
    
    result = []
    for cat_id, data in categories.items():
        cat_info = cat_names.get(cat_id, {"name": cat_id, "emoji": "📦"})
        result.append({
            "id": cat_id,
            "name": cat_info["name"],
            "emoji": cat_info["emoji"],
            "services_count": data["count"]
        })
    
    return result
