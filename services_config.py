# -*- coding: utf-8 -*-
"""
BARCHA SMM XIZMATLARI - API dan olingan haqiqiy ID lar
Peakerr + SMMMain API
"""

# Valyuta kurslari
USD_RATE = 12900
RUB_RATE = 140

# ==================== TELEGRAM XIZMATLARI ====================
TELEGRAM_SERVICES = {
    # ========== OBUNACHI/MEMBERS (Eng arzondan qimmgatga) ==========
    "tg_member_1": {
        "name": "Obunachi | Eng arzon",
        "emoji": "👥",
        "description": "Eng arzon va tez obunachi",
        "peakerr": {"id": 15050, "price_usd": 0.081},
        "smmmain": {"id": 48, "price_usd": 0.59},
        "min": 10, "max": 20000, "guarantee": "Yo'q", "speed": "5-10K/kun"
    },
    "tg_member_2": {
        "name": "Obunachi | Mix 700K",
        "emoji": "👥",
        "description": "Mix obunachi, katta hajm",
        "peakerr": {"id": 14455, "price_usd": 0.46},
        "smmmain": {"id": 48, "price_usd": 0.59},
        "min": 100, "max": 700000, "guarantee": "Yo'q", "speed": "10K/kun"
    },
    "tg_member_3": {
        "name": "Obunachi | No Limit",
        "emoji": "👥",
        "description": "Limitless obunachi",
        "peakerr": {"id": 15520, "price_usd": 0.494},
        "smmmain": {"id": 48, "price_usd": 0.59},
        "min": 100, "max": 100000, "guarantee": "Yo'q", "speed": "5K/kun"
    },
    "tg_member_4": {
        "name": "Obunachi | 30 kun R30",
        "emoji": "👥",
        "description": "30 kunlik kafolat",
        "peakerr": {"id": 12283, "price_usd": 0.5311},
        "smmmain": {"id": 48, "price_usd": 0.59},
        "min": 100, "max": 100000, "guarantee": "30 kun", "speed": "5K/kun"
    },
    "tg_member_5": {
        "name": "Obunachi | 30 kun kafolat",
        "emoji": "👥",
        "description": "30 kunlik kafolat bilan",
        "peakerr": {"id": 13896, "price_usd": 0.66},
        "smmmain": {"id": 48, "price_usd": 0.59},
        "min": 100, "max": 100000, "guarantee": "30 kun", "speed": "5K/kun"
    },
    "tg_member_6": {
        "name": "Obunachi | 60 kun kafolat",
        "emoji": "👥",
        "description": "60 kunlik kafolat bilan",
        "peakerr": {"id": 15521, "price_usd": 0.6916},
        "smmmain": {"id": 49, "price_usd": 0.64},
        "min": 100, "max": 100000, "guarantee": "60 kun", "speed": "3K/kun"
    },
    "tg_member_7": {
        "name": "Obunachi | 50K NonDrop",
        "emoji": "👥",
        "description": "Non-Drop 50K gacha",
        "peakerr": {"id": 15530, "price_usd": 0.7781},
        "smmmain": {"id": 49, "price_usd": 0.64},
        "min": 100, "max": 50000, "guarantee": "60 kun", "speed": "3K/kun"
    },
    "tg_member_8": {
        "name": "Obunachi | Real R60",
        "emoji": "👥",
        "description": "Real foydalanuvchilar 60 kun",
        "peakerr": {"id": 14453, "price_usd": 0.82},
        "smmmain": {"id": 51, "price_usd": 0.69},
        "min": 50, "max": 50000, "guarantee": "60 kun", "speed": "2K/kun"
    },
    "tg_member_9": {
        "name": "Obunachi | 90 kun kafolat",
        "emoji": "👥",
        "description": "90 kunlik kafolat",
        "peakerr": {"id": 15524, "price_usd": 1.0004},
        "smmmain": {"id": 51, "price_usd": 0.69},
        "min": 100, "max": 200000, "guarantee": "90 kun", "speed": "2K/kun"
    },
    "tg_member_10": {
        "name": "Obunachi | NonDrop 50K",
        "emoji": "👥",
        "description": "Non-Drop premium",
        "peakerr": {"id": 15573, "price_usd": 1.0868},
        "smmmain": {"id": 107, "price_usd": 0.89},
        "min": 100, "max": 50000, "guarantee": "120 kun", "speed": "2K/kun"
    },
    "tg_member_11": {
        "name": "Obunachi | High Quality",
        "emoji": "👥",
        "description": "Yuqori sifat",
        "peakerr": {"id": 24847, "price_usd": 1.157},
        "smmmain": {"id": 108, "price_usd": 0.99},
        "min": 100, "max": 300000, "guarantee": "180 kun", "speed": "3K/kun"
    },
    "tg_member_12": {
        "name": "Obunachi | No Drop 100K",
        "emoji": "👥",
        "description": "No Drop 100K gacha",
        "peakerr": {"id": 15754, "price_usd": 1.1765},
        "smmmain": {"id": 67, "price_usd": 1.31},
        "min": 100, "max": 100000, "guarantee": "Umrbod", "speed": "3K/kun"
    },
    "tg_member_13": {
        "name": "Obunachi | Non Drop 100K",
        "emoji": "👥",
        "description": "Non-Drop premium sifat",
        "peakerr": {"id": 12381, "price_usd": 1.2227},
        "smmmain": {"id": 67, "price_usd": 1.31},
        "min": 100, "max": 100000, "guarantee": "Umrbod", "speed": "2K/kun"
    },
    "tg_member_14": {
        "name": "Obunachi | Zero Drop 60 kun",
        "emoji": "👥",
        "description": "Zero Drop 60 kunlik",
        "peakerr": {"id": 15756, "price_usd": 1.3624},
        "smmmain": {"id": 58, "price_usd": 1.28},
        "min": 100, "max": 100000, "guarantee": "60 kun", "speed": "3K/kun"
    },
    "tg_member_15": {
        "name": "Obunachi | 270 kun kafolat",
        "emoji": "👥",
        "description": "270 kunlik kafolat",
        "peakerr": {"id": 15756, "price_usd": 1.3624},
        "smmmain": {"id": 112, "price_usd": 1.39},
        "min": 100, "max": 100000, "guarantee": "270 kun", "speed": "2K/kun"
    },
    "tg_member_16": {
        "name": "Obunachi | 100% Real",
        "emoji": "👥",
        "description": "100% Real foydalanuvchilar",
        "peakerr": {"id": 15311, "price_usd": 1.445},
        "smmmain": {"id": 69, "price_usd": 1.35},
        "min": 100, "max": 15000, "guarantee": "30 kun", "speed": "1K/kun"
    },
    "tg_member_premium_1": {
        "name": "Premium Obunachi | 7-14 kun",
        "emoji": "⭐",
        "description": "Telegram Premium users",
        "peakerr": {"id": 19081, "price_usd": 9.23},
        "smmmain": {"id": 607, "price_usd": 2.99},
        "min": 10, "max": 20000, "guarantee": "7-14 kun", "speed": "500/kun"
    },
    "tg_member_premium_2": {
        "name": "Premium Obunachi | 15-30 kun",
        "emoji": "⭐",
        "description": "Telegram Premium 15-30 kun",
        "peakerr": {"id": 19081, "price_usd": 9.23},
        "smmmain": {"id": 606, "price_usd": 5.99},
        "min": 10, "max": 10000, "guarantee": "15-30 kun", "speed": "300/kun"
    },
    "tg_member_premium_3": {
        "name": "Premium Obunachi | New",
        "emoji": "⭐",
        "description": "Yangi Premium users",
        "peakerr": {"id": 19081, "price_usd": 9.23},
        "smmmain": {"id": 605, "price_usd": 14.00},
        "min": 10, "max": 5000, "guarantee": "30 kun", "speed": "200/kun"
    },
    "tg_member_premium_4": {
        "name": "Premium Obunachi | ZeroDrop",
        "emoji": "⭐",
        "description": "Premium Zero Drop",
        "peakerr": {"id": 19081, "price_usd": 9.23},
        "smmmain": {"id": 600, "price_usd": 24.00},
        "min": 10, "max": 5000, "guarantee": "Umrbod", "speed": "100/kun"
    },
    
    # ========== KO'RISH/VIEWS (Eng arzondan qimmgatga) ==========
    "tg_view_1": {
        "name": "Ko'rish | 1 post Eng arzon",
        "emoji": "👁",
        "description": "Eng arzon 1 post ko'rish",
        "peakerr": {"id": 15974, "price_usd": 0.0026},
        "smmmain": {"id": 41, "price_usd": 0.004},
        "min": 100, "max": 100000, "guarantee": "Kafolatli", "speed": "100K/soat"
    },
    "tg_view_2": {
        "name": "Ko'rish | Super Fast 50M",
        "emoji": "👁",
        "description": "Super tez 50M gacha",
        "peakerr": {"id": 23471, "price_usd": 0.0052},
        "smmmain": {"id": 41, "price_usd": 0.004},
        "min": 100, "max": 50000000, "guarantee": "Kafolatli", "speed": "1M/soat"
    },
    "tg_view_3": {
        "name": "Ko'rish | Instant 100M",
        "emoji": "👁",
        "description": "Instant 100M gacha",
        "peakerr": {"id": 13290, "price_usd": 0.006},
        "smmmain": {"id": 41, "price_usd": 0.004},
        "min": 100, "max": 100000000, "guarantee": "Kafolatli", "speed": "Super tez"
    },
    "tg_view_4": {
        "name": "Ko'rish | Speed 20K/soat",
        "emoji": "👁",
        "description": "Tez 20K/soat",
        "peakerr": {"id": 1368, "price_usd": 0.0073},
        "smmmain": {"id": 41, "price_usd": 0.004},
        "min": 100, "max": 100000, "guarantee": "Kafolatli", "speed": "20K/soat"
    },
    "tg_view_5": {
        "name": "Ko'rish | Last 1 Post 500K",
        "emoji": "👁",
        "description": "Oxirgi 1 post 500K",
        "peakerr": {"id": 9094, "price_usd": 0.0195},
        "smmmain": {"id": 41, "price_usd": 0.004},
        "min": 100, "max": 500000, "guarantee": "Kafolatli", "speed": "50K/soat"
    },
    "tg_view_6": {
        "name": "Ko'rish | USA Lifetime",
        "emoji": "👁",
        "description": "USA Lifetime Refill",
        "peakerr": {"id": 15958, "price_usd": 0.091},
        "smmmain": {"id": 41, "price_usd": 0.004},
        "min": 100, "max": 10000000, "guarantee": "Umrbod", "speed": "100K/soat"
    },
    "tg_view_7": {
        "name": "Ko'rish | Story",
        "emoji": "👁",
        "description": "Story ko'rish",
        "peakerr": {"id": 15958, "price_usd": 0.091},
        "smmmain": {"id": 640, "price_usd": 0.10},
        "min": 100, "max": 100000, "guarantee": "Kafolatli", "speed": "50K/soat"
    },
    "tg_view_8": {
        "name": "Ko'rish | Last 20 Post",
        "emoji": "👁",
        "description": "Oxirgi 20 post",
        "peakerr": {"id": 12298, "price_usd": 0.1235},
        "smmmain": {"id": 42, "price_usd": 0.30},
        "min": 100, "max": 300000, "guarantee": "Kafolatli", "speed": "30K/soat"
    },
    "tg_view_9": {
        "name": "Ko'rish | Last 50 Post",
        "emoji": "👁",
        "description": "Oxirgi 50 post",
        "peakerr": {"id": 1369, "price_usd": 0.1463},
        "smmmain": {"id": 42, "price_usd": 0.30},
        "min": 100, "max": 300000, "guarantee": "Kafolatli", "speed": "20K/soat"
    },
    "tg_view_10": {
        "name": "Ko'rish | Last 20 Post v2",
        "emoji": "👁",
        "description": "Oxirgi 20 post v2",
        "peakerr": {"id": 15347, "price_usd": 0.1476},
        "smmmain": {"id": 42, "price_usd": 0.30},
        "min": 100, "max": 10000000, "guarantee": "Kafolatli", "speed": "100K/soat"
    },
    "tg_view_11": {
        "name": "Ko'rish | Premium Story",
        "emoji": "⭐",
        "description": "Premium Story views",
        "peakerr": {"id": 15958, "price_usd": 0.091},
        "smmmain": {"id": 519, "price_usd": 0.20},
        "min": 100, "max": 50000, "guarantee": "Kafolatli", "speed": "30K/soat"
    },
    
    # ========== REAKSIYALAR (Eng arzondan qimmgatga) ==========
    "tg_react_1": {
        "name": "Reaksiya | Auto Pozitiv",
        "emoji": "👍",
        "description": "Avtomatik pozitiv reaksiya",
        "peakerr": {"id": 13420, "price_usd": 0.0169},
        "smmmain": {"id": 180, "price_usd": 0.10},
        "min": 10, "max": 500000, "guarantee": "Yo'q", "speed": "50K/soat"
    },
    "tg_react_2": {
        "name": "Reaksiya + Views | Pozitiv",
        "emoji": "👍",
        "description": "Pozitiv + bepul ko'rish",
        "peakerr": {"id": 18339, "price_usd": 0.039},
        "smmmain": {"id": 180, "price_usd": 0.10},
        "min": 10, "max": 10000000, "guarantee": "Yo'q", "speed": "100K/soat"
    },
    "tg_react_3": {
        "name": "Reaksiya | Pozitiv + Views",
        "emoji": "👍",
        "description": "Pozitiv reaksiya + ko'rish",
        "peakerr": {"id": 15582, "price_usd": 0.0618},
        "smmmain": {"id": 180, "price_usd": 0.10},
        "min": 10, "max": 500000, "guarantee": "Yo'q", "speed": "50K/soat"
    },
    "tg_react_4": {
        "name": "Reaksiya | Premium Whale",
        "emoji": "🐳",
        "description": "Premium whale emoji",
        "peakerr": {"id": 15396, "price_usd": 0.0878},
        "smmmain": {"id": 180, "price_usd": 0.10},
        "min": 10, "max": 100000, "guarantee": "Yo'q", "speed": "30K/soat"
    },
    "tg_react_5": {
        "name": "Reaksiya | Premium Strawberry",
        "emoji": "🍓",
        "description": "Premium strawberry emoji",
        "peakerr": {"id": 15403, "price_usd": 0.0878},
        "smmmain": {"id": 180, "price_usd": 0.10},
        "min": 10, "max": 100000, "guarantee": "Yo'q", "speed": "30K/soat"
    },
    "tg_react_6": {
        "name": "Reaksiya | Like + Views",
        "emoji": "👍",
        "description": "Like reaksiya + ko'rish",
        "peakerr": {"id": 13292, "price_usd": 0.1332},
        "smmmain": {"id": 180, "price_usd": 0.10},
        "min": 10, "max": 500000, "guarantee": "Yo'q", "speed": "50K/soat"
    },
    "tg_react_7": {
        "name": "Reaksiya | Like",
        "emoji": "👍",
        "description": "Faqat Like reaksiya",
        "peakerr": {"id": 12312, "price_usd": 0.1545},
        "smmmain": {"id": 180, "price_usd": 0.10},
        "min": 10, "max": 1000000, "guarantee": "Yo'q", "speed": "100K/soat"
    },
    "tg_react_8": {
        "name": "Reaksiya | Heart",
        "emoji": "❤️",
        "description": "Heart yurak reaksiya",
        "peakerr": {"id": 12312, "price_usd": 0.1545},
        "smmmain": {"id": 182, "price_usd": 0.10},
        "min": 10, "max": 1000000, "guarantee": "Yo'q", "speed": "100K/soat"
    },
    "tg_react_9": {
        "name": "Reaksiya | Fire",
        "emoji": "🔥",
        "description": "Fire olov reaksiya",
        "peakerr": {"id": 12312, "price_usd": 0.1545},
        "smmmain": {"id": 183, "price_usd": 0.10},
        "min": 10, "max": 1000000, "guarantee": "Yo'q", "speed": "100K/soat"
    },
    "tg_react_10": {
        "name": "Reaksiya | Party",
        "emoji": "🎉",
        "description": "Party bayram reaksiya",
        "peakerr": {"id": 12312, "price_usd": 0.1545},
        "smmmain": {"id": 184, "price_usd": 0.10},
        "min": 10, "max": 1000000, "guarantee": "Yo'q", "speed": "100K/soat"
    },
    "tg_react_11": {
        "name": "Reaksiya | Star-Struck",
        "emoji": "🤩",
        "description": "Star-struck reaksiya",
        "peakerr": {"id": 12317, "price_usd": 0.1545},
        "smmmain": {"id": 185, "price_usd": 0.10},
        "min": 10, "max": 1000000, "guarantee": "Yo'q", "speed": "100K/soat"
    },
    "tg_react_12": {
        "name": "Reaksiya | Dislike",
        "emoji": "👎",
        "description": "Dislike reaksiya",
        "peakerr": {"id": 12313, "price_usd": 0.1545},
        "smmmain": {"id": 181, "price_usd": 0.10},
        "min": 10, "max": 1000000, "guarantee": "Yo'q", "speed": "100K/soat"
    },
    "tg_react_13": {
        "name": "Reaksiya | Cry",
        "emoji": "😢",
        "description": "Cry yig'lash reaksiya",
        "peakerr": {"id": 12320, "price_usd": 0.1545},
        "smmmain": {"id": 188, "price_usd": 0.10},
        "min": 10, "max": 1000000, "guarantee": "Yo'q", "speed": "100K/soat"
    },
    "tg_react_14": {
        "name": "Reaksiya | Poo",
        "emoji": "💩",
        "description": "Poo reaksiya",
        "peakerr": {"id": 12321, "price_usd": 0.1545},
        "smmmain": {"id": 189, "price_usd": 0.10},
        "min": 10, "max": 1000000, "guarantee": "Yo'q", "speed": "100K/soat"
    },
    "tg_react_15": {
        "name": "Reaksiya | Scream",
        "emoji": "😱",
        "description": "Scream qo'rqish reaksiya",
        "peakerr": {"id": 12311, "price_usd": 0.1545},
        "smmmain": {"id": 186, "price_usd": 0.10},
        "min": 10, "max": 1000000, "guarantee": "Yo'q", "speed": "100K/soat"
    },
    "tg_react_16": {
        "name": "Reaksiya | Smile",
        "emoji": "😁",
        "description": "Smile kulish reaksiya",
        "peakerr": {"id": 12310, "price_usd": 0.1545},
        "smmmain": {"id": 187, "price_usd": 0.10},
        "min": 10, "max": 1000000, "guarantee": "Yo'q", "speed": "100K/soat"
    },
    "tg_react_17": {
        "name": "Reaksiya | Vomit",
        "emoji": "🤮",
        "description": "Vomit reaksiya",
        "peakerr": {"id": 12311, "price_usd": 0.1545},
        "smmmain": {"id": 190, "price_usd": 0.10},
        "min": 10, "max": 1000000, "guarantee": "Yo'q", "speed": "100K/soat"
    },
    "tg_react_18": {
        "name": "Reaksiya | Pray",
        "emoji": "🙏",
        "description": "Pray duo reaksiya",
        "peakerr": {"id": 16149, "price_usd": 0.253},
        "smmmain": {"id": 178, "price_usd": 0.10},
        "min": 10, "max": 100000, "guarantee": "Yo'q", "speed": "30K/soat"
    },
    "tg_react_19": {
        "name": "Reaksiya | Angry",
        "emoji": "🤬",
        "description": "Angry g'azab reaksiya",
        "peakerr": {"id": 16153, "price_usd": 0.253},
        "smmmain": {"id": 179, "price_usd": 0.10},
        "min": 10, "max": 100000, "guarantee": "Yo'q", "speed": "30K/soat"
    },
    
    # ========== SHARE/FORWARD ==========
    "tg_share_1": {
        "name": "Share | Real",
        "emoji": "🔄",
        "description": "Real share/forward",
        "peakerr": {"id": 16052, "price_usd": 0.0156},
        "smmmain": None,
        "min": 100, "max": 1000000, "guarantee": "Yo'q", "speed": "50K/kun"
    },
    "tg_share_2": {
        "name": "Share | Static",
        "emoji": "🔄",
        "description": "Static kontentli share",
        "peakerr": {"id": 12323, "price_usd": 0.0606},
        "smmmain": None,
        "min": 100, "max": 100000, "guarantee": "Yo'q", "speed": "30K/kun"
    },
    "tg_share_3": {
        "name": "Share | USA",
        "emoji": "🔄",
        "description": "USA share",
        "peakerr": {"id": 12329, "price_usd": 0.0606},
        "smmmain": None,
        "min": 100, "max": 100000, "guarantee": "Yo'q", "speed": "20K/kun"
    },
    "tg_share_4": {
        "name": "Share | India",
        "emoji": "🔄",
        "description": "India share",
        "peakerr": {"id": 15594, "price_usd": 0.0606},
        "smmmain": None,
        "min": 100, "max": 100000, "guarantee": "Yo'q", "speed": "20K/kun"
    },
    
    # ========== VOTE/POLL ==========
    "tg_vote_1": {
        "name": "Vote | Poll/So'rovnoma",
        "emoji": "📊",
        "description": "So'rovnomaga ovoz",
        "peakerr": {"id": 13291, "price_usd": 0.339},
        "smmmain": None,
        "min": 100, "max": 300000, "guarantee": "Yo'q", "speed": "10K/soat"
    },
}

# Jami xizmatlar soni
TELEGRAM_TOTAL = len(TELEGRAM_SERVICES)
print(f"Jami Telegram xizmatlari: {TELEGRAM_TOTAL} ta")
