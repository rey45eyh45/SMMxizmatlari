# -*- coding: utf-8 -*-
"""
IDEAL SMM XIZMATLARI BOT - Aiogram 3.x
Eng to'liq xizmatlar: Telegram, Instagram, YouTube, TikTok, Facebook, Twitter/X, Spotify
+ Virtual telefon raqamlar (SMS Verification)
"""
import logging
import sqlite3
import asyncio
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, Router, F
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery, InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, ADMIN_ID, DATABASE_NAME, PAYMENT_CARDS
from keyboards_v3 import *
from database import *
from smm_api import MultiPanel
from sms_api import VakSMS
from services_config import TELEGRAM_SERVICES
from sms_prices import TELEGRAM_SMS_PRICES, get_cheapest_by_country

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Bot va Dispatcher
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

# Bot profil rasmi URL (cache) - bot ishga tushganda yuklanadi
BOT_PHOTO_URL = None

# SMS API
sms_api = VakSMS()

# SMM Multi-Panel API
smm_api = MultiPanel()

# ==================== HOLATLAR (FSM States) ====================
class OrderState(StatesGroup):
    waiting_for_link = State()
    waiting_for_quantity = State()
    confirm_order = State()

class PaymentState(StatesGroup):
    waiting_for_amount = State()
    waiting_for_screenshot = State()

class SMSState(StatesGroup):
    waiting_for_sms = State()

class AdminState(StatesGroup):
    waiting_for_partial_amount = State()  # To'lov tasdiqlash uchun
    waiting_for_cancel_order = State()  # Buyurtma raqamini kutish
    waiting_for_cancel_confirm = State()  # Tasdiqlashni kutish
    waiting_for_user_search = State()  # Foydalanuvchi qidirish
    waiting_for_user_action = State()  # Foydalanuvchi ustida amal
    waiting_for_balance_change = State()  # Balans o'zgartirish
    waiting_for_user_message = State()  # Foydalanuvchiga xabar
    waiting_for_broadcast = State()  # Ommaviy xabar matni
    waiting_for_broadcast_media = State()  # Ommaviy xabar media
    waiting_for_broadcast_button = State()  # Ommaviy xabar tugma
    waiting_for_broadcast_confirm = State()  # Xabar tasdiqlash
    waiting_for_global_balance = State()  # Global balans boshqarish
    waiting_for_global_balance_amount = State()  # Global balans miqdori
    waiting_for_restore_file = State()  # Zaxira fayl kutish
    waiting_for_restore_confirm = State()  # Tiklash tasdiqlash
    # Sozlamalar uchun
    waiting_for_usd_rate = State()  # Dollar kursi
    waiting_for_rub_rate = State()  # Rubl kursi
    waiting_for_markup = State()  # Ustama foiz
    waiting_for_card_number = State()  # Karta raqam
    waiting_for_card_holder = State()  # Karta egasi
    waiting_for_min_deposit = State()  # Minimal to'lov
    waiting_for_new_admin = State()  # Yangi admin
    waiting_for_ref_bonus = State()  # Referal bonus


class PremiumState(StatesGroup):
    waiting_for_phone = State()  # Telefon raqam kutish
    waiting_for_payment = State()  # To'lov kutish


# ==================== SOZLAMALARDAN QIYMAT OLUVCHI FUNKSIYALAR ====================
def get_usd_rate():
    """USD kursini sozlamalardan olish"""
    return int(get_setting('usd_rate', '12900'))

def get_rub_rate():
    """RUB kursini sozlamalardan olish"""
    return int(get_setting('rub_rate', '140'))

def get_markup_percent():
    """Ustama foizni sozlamalardan olish"""
    return int(get_setting('markup_percent', '20'))

def get_min_deposit():
    """Minimal to'lov summasini sozlamalardan olish"""
    return int(get_setting('min_deposit', '5000'))

def get_referral_bonus():
    """Referal bonusni sozlamalardan olish"""
    return int(get_setting('referral_bonus', '500'))


# ==================== CONSTANTS ====================
SMS_PLATFORMS = {
    "tg": {"name": "Telegram", "code": "tg", "emoji": "📱"},
    "ig": {"name": "Instagram", "code": "ig", "emoji": "📷"},
    "wa": {"name": "WhatsApp", "code": "wa", "emoji": "💬"},
    "go": {"name": "Google/Gmail", "code": "go", "emoji": "🔍"},
    "ya": {"name": "Yandex", "code": "ya", "emoji": "🔴"},
    "tt": {"name": "TikTok", "code": "tt", "emoji": "🎵"},
    "fb": {"name": "Facebook", "code": "fb", "emoji": "📘"},
    "tw": {"name": "Twitter/X", "code": "tw", "emoji": "🐦"},
    "ds": {"name": "Discord", "code": "ds", "emoji": "🎮"},
    "am": {"name": "Amazon", "code": "am", "emoji": "📦"},
    "mi": {"name": "Microsoft", "code": "mi", "emoji": "💻"},
    "oi": {"name": "OpenAI/ChatGPT", "code": "oi", "emoji": "🤖"},
}

SMS_COUNTRIES = {
    "ru": "🇷🇺 Rossiya",
    "ua": "🇺🇦 Ukraina",
    "kz": "🇰🇿 Qozog'iston",
    "uz": "🇺🇿 O'zbekiston",
    "tj": "🇹🇯 Tojikiston",
    "kg": "🇰🇬 Qirg'iziston",
    "id": "🇮🇩 Indoneziya",
    "ph": "🇵🇭 Filippin",
    "vn": "🇻🇳 Vetnam",
    "bd": "🇧🇩 Bangladesh",
    "in": "🇮🇳 Hindiston",
    "ge": "🇬🇪 Gruziya",
}

# ==================== XIZMATLAR ====================
SERVICES_MAP = {
    # ===================== TELEGRAM =====================
    # ========== OBUNACHI/MEMBERS ==========
    "tg_member_cheap": {
        "name": "👥 Obunachi (Arzon)",
        "description": "Eng arzon obunachi - tez yetkazish",
        "peakerr": {"id": 15050, "price_usd": 0.081},
        "smmmain": {"id": 48, "price_usd": 0.59},
        "min": 10, "max": 20000, "guarantee": "Yo'q", "speed": "5-10K/kun"
    },
    "tg_member_30day": {
        "name": "👥 Obunachi (30 kun kafolat)",
        "description": "30 kunlik kafolat bilan obunachi",
        "peakerr": {"id": 13896, "price_usd": 0.66},
        "smmmain": {"id": 48, "price_usd": 0.59},
        "min": 100, "max": 100000, "guarantee": "30 kun", "speed": "5K/kun"
    },
    "tg_member_60day": {
        "name": "👥 Obunachi (60 kun kafolat)",
        "description": "60 kunlik kafolat bilan obunachi",
        "peakerr": {"id": 15530, "price_usd": 0.78},
        "smmmain": {"id": 49, "price_usd": 0.64},
        "min": 100, "max": 50000, "guarantee": "60 kun", "speed": "3K/kun"
    },
    "tg_member_90day": {
        "name": "👥 Obunachi (90 kun kafolat)",
        "description": "90 kunlik kafolat bilan obunachi",
        "peakerr": {"id": 15573, "price_usd": 1.09},
        "smmmain": {"id": 51, "price_usd": 0.69},
        "min": 100, "max": 50000, "guarantee": "90 kun", "speed": "2K/kun"
    },
    "tg_member_nodrop": {
        "name": "👥 Obunachi (No Drop)",
        "description": "Tushmaydigan obunachi - eng sifatli",
        "peakerr": {"id": 15754, "price_usd": 1.18},
        "smmmain": {"id": 67, "price_usd": 1.31},
        "min": 100, "max": 100000, "guarantee": "Umrbod", "speed": "2K/kun"
    },
    "tg_member_real": {
        "name": "👥 Real Obunachi",
        "description": "Haqiqiy faol foydalanuvchilar",
        "peakerr": {"id": 14453, "price_usd": 0.82},
        "smmmain": {"id": 69, "price_usd": 1.35},
        "min": 50, "max": 50000, "guarantee": "60 kun", "speed": "1K/kun"
    },
    "tg_member_high": {
        "name": "👥 Yuqori sifatli Obunachi",
        "description": "High Quality - eng yaxshi sifat",
        "peakerr": {"id": 15756, "price_usd": 1.36},
        "smmmain": {"id": 58, "price_usd": 1.28},
        "min": 100, "max": 100000, "guarantee": "60 kun", "speed": "3K/kun"
    },
    "tg_member_premium": {
        "name": "⭐ Premium Obunachi",
        "description": "Telegram Premium foydalanuvchilar",
        "peakerr": {"id": 19081, "price_usd": 9.23},
        "smmmain": {"id": 607, "price_usd": 2.99},
        "min": 10, "max": 20000, "guarantee": "7-14 kun", "speed": "500/kun"
    },
    "tg_subscriber": {
        "name": "👥 Telegram Obunachi",
        "description": "Kanalingizga real ko'rinishdagi obunachi",
        "peakerr": {"id": 15050, "price_usd": 0.08},
        "smmmain": {"id": 48, "price_usd": 0.59},
        "min": 10, "max": 20000, "guarantee": "30 kun", "speed": "5-10K/kun"
    },
    "tg_subscriber_premium": {
        "name": "📸 Telegram Premium Obunachi",
        "description": "Premium hisoblardan obunachi - yuqori sifat",
        "peakerr": {"id": 19081, "price_usd": 9.23},
        "smmmain": {"id": 607, "price_usd": 2.99},
        "min": 10, "max": 5000, "guarantee": "60 kun", "speed": "1-3K/kun"
    },
    "tg_subscriber_uzbek": {
        "name": "🇺🇿 O'zbek Obunachi",
        "description": "O'zbekistonlik real obunachi",
        "peakerr": {"id": 15311, "price_usd": 1.45},
        "smmmain": {"id": 67, "price_usd": 1.31},
        "min": 50, "max": 15000, "guarantee": "30 kun", "speed": "500-1K/kun"
    },
    
    # ========== KO'RISH/VIEWS ==========
    "tg_view": {
        "name": "👁 Ko'rish (1 post)",
        "description": "Bitta postga ko'rish",
        "peakerr": {"id": 15974, "price_usd": 0.0026},
        "smmmain": {"id": 41, "price_usd": 0.004},
        "min": 100, "max": 100000, "guarantee": "Kafolatli", "speed": "100K/soat"
    },
    "tg_view_cheap": {
        "name": "👁 Ko'rish (Eng arzon)",
        "description": "Eng arzon post ko'rish",
        "peakerr": {"id": 23471, "price_usd": 0.0052},
        "smmmain": {"id": 41, "price_usd": 0.004},
        "min": 100, "max": 50000000, "guarantee": "Kafolatli", "speed": "1M/soat"
    },
    "tg_view_instant": {
        "name": "👁 Ko'rish (Instant)",
        "description": "Darhol yetkazish",
        "peakerr": {"id": 13290, "price_usd": 0.006},
        "smmmain": {"id": 41, "price_usd": 0.004},
        "min": 100, "max": 100000000, "guarantee": "Kafolatli", "speed": "Super tez"
    },
    "tg_view_fast": {
        "name": "👁 Ko'rish (Tez)",
        "description": "Tez yetkazish - 20K/soat",
        "peakerr": {"id": 1368, "price_usd": 0.0073},
        "smmmain": {"id": 41, "price_usd": 0.004},
        "min": 100, "max": 100000, "guarantee": "Kafolatli", "speed": "20K/soat"
    },
    "tg_view_last10": {
        "name": "👁 So'nggi 10 Post Ko'rish",
        "description": "Oxirgi 10 postga avtomatik ko'rish",
        "peakerr": {"id": 9094, "price_usd": 0.0195},
        "smmmain": {"id": 42, "price_usd": 0.30},
        "min": 100, "max": 500000, "guarantee": "Kafolatli", "speed": "50K/soat"
    },
    "tg_view_last20": {
        "name": "👁 So'nggi 20 Post Ko'rish",
        "description": "Oxirgi 20 postga avtomatik ko'rish",
        "peakerr": {"id": 12298, "price_usd": 0.1235},
        "smmmain": {"id": 42, "price_usd": 0.30},
        "min": 100, "max": 300000, "guarantee": "Kafolatli", "speed": "30K/soat"
    },
    "tg_view_last50": {
        "name": "👁 So'nggi 50 Post Ko'rish",
        "description": "Oxirgi 50 postga avtomatik ko'rish",
        "peakerr": {"id": 1369, "price_usd": 0.1463},
        "smmmain": {"id": 42, "price_usd": 0.30},
        "min": 100, "max": 300000, "guarantee": "Kafolatli", "speed": "20K/soat"
    },
    "tg_view_usa": {
        "name": "👁 Ko'rish (USA)",
        "description": "Amerika foydalanuvchilaridan ko'rish",
        "peakerr": {"id": 15958, "price_usd": 0.091},
        "smmmain": {"id": 41, "price_usd": 0.004},
        "min": 100, "max": 10000000, "guarantee": "Umrbod", "speed": "100K/soat"
    },
    "tg_story_view": {
        "name": "👁 Story Ko'rish",
        "description": "Story/Hikoyalarga ko'rish",
        "peakerr": {"id": 15958, "price_usd": 0.091},
        "smmmain": {"id": 640, "price_usd": 0.10},
        "min": 100, "max": 100000, "guarantee": "Kafolatli", "speed": "50K/soat"
    },
    "tg_story_view_premium": {
        "name": "⭐ Premium Story Ko'rish",
        "description": "Premium hisoblardan story ko'rish",
        "peakerr": {"id": 15958, "price_usd": 0.091},
        "smmmain": {"id": 519, "price_usd": 0.20},
        "min": 100, "max": 50000, "guarantee": "Kafolatli", "speed": "30K/soat"
    },
    
    # ========== REAKSIYALAR ==========
    "tg_reaction": {
        "name": "👍 Reaksiya (Pozitiv)",
        "description": "👍❤️🔥🎉🤩 - avtomatik",
        "peakerr": {"id": 13420, "price_usd": 0.0169},
        "smmmain": {"id": 180, "price_usd": 0.10},
        "min": 10, "max": 500000, "guarantee": "Yo'q", "speed": "50K/soat"
    },
    "tg_reaction_like": {
        "name": "👍 Like Reaksiya",
        "description": "Faqat 👍 like reaksiya",
        "peakerr": {"id": 12312, "price_usd": 0.1545},
        "smmmain": {"id": 180, "price_usd": 0.10},
        "min": 10, "max": 1000000, "guarantee": "Yo'q", "speed": "100K/soat"
    },
    "tg_reaction_heart": {
        "name": "❤️ Heart Reaksiya",
        "description": "Faqat ❤️ yurak reaksiya",
        "peakerr": {"id": 12312, "price_usd": 0.1545},
        "smmmain": {"id": 182, "price_usd": 0.10},
        "min": 10, "max": 1000000, "guarantee": "Yo'q", "speed": "100K/soat"
    },
    "tg_reaction_fire": {
        "name": "🔥 Fire Reaksiya",
        "description": "Faqat 🔥 olov reaksiya",
        "peakerr": {"id": 12312, "price_usd": 0.1545},
        "smmmain": {"id": 183, "price_usd": 0.10},
        "min": 10, "max": 1000000, "guarantee": "Yo'q", "speed": "100K/soat"
    },
    "tg_reaction_party": {
        "name": "🎉 Party Reaksiya",
        "description": "Faqat 🎉 bayram reaksiya",
        "peakerr": {"id": 12312, "price_usd": 0.1545},
        "smmmain": {"id": 184, "price_usd": 0.10},
        "min": 10, "max": 1000000, "guarantee": "Yo'q", "speed": "100K/soat"
    },
    "tg_reaction_sad": {
        "name": "📸 Sad Reaksiya",
        "description": "Faqat 📸 g'amgin reaksiya",
        "peakerr": {"id": 12320, "price_usd": 0.1545},
        "smmmain": {"id": 188, "price_usd": 0.10},
        "min": 10, "max": 1000000, "guarantee": "Yo'q", "speed": "100K/soat"
    },
    "tg_reaction_dislike": {
        "name": "👎 Dislike Reaksiya",
        "description": "Faqat 👎 dislike reaksiya",
        "peakerr": {"id": 12313, "price_usd": 0.1545},
        "smmmain": {"id": 181, "price_usd": 0.10},
        "min": 10, "max": 1000000, "guarantee": "Yo'q", "speed": "100K/soat"
    },
    "tg_reaction_negative": {
        "name": "😱 Negativ Reaksiya",
        "description": "👎😱💩😢🤮 - negativ reaksiya",
        "peakerr": {"id": 12311, "price_usd": 0.1545},
        "smmmain": {"id": 186, "price_usd": 0.10},
        "min": 10, "max": 500000, "guarantee": "Yo'q", "speed": "50K/soat"
    },
    "tg_reaction_premium": {
        "name": "🐳 Premium Reaksiya",
        "description": "Premium emoji reaksiya (🐳📸...)",
        "peakerr": {"id": 15396, "price_usd": 0.0878},
        "smmmain": {"id": 180, "price_usd": 0.10},
        "min": 10, "max": 100000, "guarantee": "Yo'q", "speed": "30K/soat"
    },
    "tg_reaction_custom": {
        "name": "🎭 Custom Reaksiya",
        "description": "O'zingiz tanlagan reaksiya",
        "peakerr": {"id": 16149, "price_usd": 0.253},
        "smmmain": {"id": 180, "price_usd": 0.10},
        "min": 10, "max": 100000, "guarantee": "Yo'q", "speed": "30K/soat"
    },
    "tg_reaction_views": {
        "name": "👍 Reaksiya + Ko'rish",
        "description": "Reaksiya va bepul ko'rish",
        "peakerr": {"id": 18339, "price_usd": 0.039},
        "smmmain": {"id": 180, "price_usd": 0.10},
        "min": 10, "max": 10000000, "guarantee": "Yo'q", "speed": "100K/soat"
    },
    
    # ========== SHARE/FORWARD ==========
    "tg_share": {
        "name": "🔄 Share/Ulashish",
        "description": "Postni boshqalarga ulashish",
        "peakerr": {"id": 16052, "price_usd": 0.0156},
        "smmmain": {"id": 42, "price_usd": 0.30},
        "min": 100, "max": 1000000, "guarantee": "Yo'q", "speed": "50K/kun"
    },
    "tg_share_static": {
        "name": "🔄 Share (Static)",
        "description": "Statik kontentli ulashish",
        "peakerr": {"id": 12323, "price_usd": 0.0606},
        "smmmain": {"id": 42, "price_usd": 0.30},
        "min": 100, "max": 100000, "guarantee": "Yo'q", "speed": "30K/kun"
    },
    "tg_share_usa": {
        "name": "🔄 Share (USA)",
        "description": "USA foydalanuvchilaridan ulashish",
        "peakerr": {"id": 12329, "price_usd": 0.0606},
        "smmmain": {"id": 42, "price_usd": 0.30},
        "min": 100, "max": 100000, "guarantee": "Yo'q", "speed": "20K/kun"
    },
    
    # ========== VOTE/POLL ==========
    "tg_vote": {
        "name": "📊 Ovoz/So'rovnoma",
        "description": "So'rovnomaga ovoz berish",
        "peakerr": {"id": 13291, "price_usd": 0.339},
        "smmmain": {"id": 42, "price_usd": 0.30},
        "min": 100, "max": 300000, "guarantee": "Yo'q", "speed": "10K/soat"
    },
    
    # ===================== INSTAGRAM =====================
    # Follower
    "ig_follower": {
        "name": "👥 Instagram Follower",
        "description": "Real ko'rinishdagi follower",
        "peakerr": {"id": 16350, "price_usd": 0.47},
        "smmmain": {"id": 1105, "price_usd": 0.52},
        "min": 50, "max": 100000, "guarantee": "30 kun", "speed": "10K/kun"
    },
    "ig_follower_premium": {
        "name": "👥 Instagram Premium Follower",
        "description": "Yuqori sifatli, faol follower",
        "peakerr": {"id": 16355, "price_usd": 0.80},
        "smmmain": {"id": 1106, "price_usd": 0.85},
        "min": 50, "max": 50000, "guarantee": "60 kun", "speed": "5K/kun"
    },
    "ig_follower_real": {
        "name": "👥 Instagram Real Follower",
        "description": "100% haqiqiy faol foydalanuvchilar",
        "peakerr": {"id": 16360, "price_usd": 1.50},
        "smmmain": {"id": 1107, "price_usd": 1.60},
        "min": 100, "max": 10000, "guarantee": "90 kun", "speed": "1K/kun"
    },
    # Like
    "ig_like": {
        "name": "❤️ Instagram Like",
        "description": "Postlarga like",
        "peakerr": {"id": 27278, "price_usd": 0.137},
        "smmmain": {"id": 1109, "price_usd": 0.14},
        "min": 10, "max": 100000, "guarantee": "Yo'q", "speed": "100K/kun"
    },
    "ig_like_premium": {
        "name": "❤️ Instagram Premium Like",
        "description": "Yuqori sifatli, real hisoblardan",
        "peakerr": {"id": 27280, "price_usd": 0.25},
        "smmmain": {"id": 1110, "price_usd": 0.28},
        "min": 10, "max": 50000, "guarantee": "Kafolatli", "speed": "50K/kun"
    },
    # Ko'rish
    "ig_view": {
        "name": "👁 Instagram Video Ko'rish",
        "description": "Reels va videolarga ko'rish",
        "peakerr": {"id": 19865, "price_usd": 0.0011},
        "smmmain": {"id": 1115, "price_usd": 0.002},
        "min": 100, "max": 10000000, "guarantee": "Kafolatli", "speed": "1M/soat"
    },
    "ig_reel_view": {
        "name": "👁 Instagram Reels Ko'rish",
        "description": "Faqat Reels videolarga",
        "peakerr": {"id": 19870, "price_usd": 0.0008},
        "smmmain": {"id": 1116, "price_usd": 0.001},
        "min": 100, "max": 50000000, "guarantee": "Kafolatli", "speed": "5M/soat"
    },
    "ig_story_view": {
        "name": "👁 Instagram Story Ko'rish",
        "description": "Story'larga ko'rish",
        "peakerr": {"id": 19875, "price_usd": 0.003},
        "smmmain": {"id": 1117, "price_usd": 0.004},
        "min": 100, "max": 500000, "guarantee": "Kafolatli", "speed": "100K/soat"
    },
    # Comment
    "ig_comment": {
        "name": "💬 Instagram Comment",
        "description": "Postlarga izoh (random)",
        "peakerr": {"id": 19880, "price_usd": 0.50},
        "smmmain": {"id": 1120, "price_usd": 0.55},
        "min": 5, "max": 10000, "guarantee": "Yo'q", "speed": "1K/kun"
    },
    "ig_comment_custom": {
        "name": "💬 Instagram Custom Comment",
        "description": "O'zingiz yozgan izoh",
        "peakerr": {"id": 19885, "price_usd": 1.00},
        "smmmain": {"id": 1121, "price_usd": 1.10},
        "min": 1, "max": 1000, "guarantee": "Yo'q", "speed": "500/kun"
    },
    # Save
    "ig_save": {
        "name": "📥 Instagram Save/Saqlash",
        "description": "Postlarni saqlash",
        "peakerr": {"id": 19890, "price_usd": 0.20},
        "smmmain": {"id": 1125, "price_usd": 0.22},
        "min": 10, "max": 50000, "guarantee": "Yo'q", "speed": "10K/kun"
    },
    # Share
    "ig_share": {
        "name": "🔄 Instagram Share",
        "description": "Postlarni ulashish",
        "peakerr": {"id": 19895, "price_usd": 0.15},
        "smmmain": {"id": 1126, "price_usd": 0.18},
        "min": 10, "max": 50000, "guarantee": "Yo'q", "speed": "20K/kun"
    },
    
    # ===================== YOUTUBE =====================
    # Subscriber
    "yt_subscriber": {
        "name": "👥 YouTube Subscriber",
        "description": "Kanalingizga obuna",
        "peakerr": {"id": 23304, "price_usd": 0.15},
        "smmmain": {"id": 1201, "price_usd": 0.20},
        "min": 50, "max": 100000, "guarantee": "30 kun", "speed": "5K/kun"
    },
    "yt_subscriber_premium": {
        "name": "👥 YouTube Premium Subscriber",
        "description": "Yuqori sifatli, faol obuna",
        "peakerr": {"id": 23310, "price_usd": 0.35},
        "smmmain": {"id": 1202, "price_usd": 0.40},
        "min": 50, "max": 50000, "guarantee": "60 kun", "speed": "2K/kun"
    },
    # Ko'rish
    "yt_view": {
        "name": "👁 YouTube Ko'rish",
        "description": "Videolarga ko'rish",
        "peakerr": {"id": 27356, "price_usd": 0.042},
        "smmmain": {"id": 1205, "price_usd": 0.05},
        "min": 100, "max": 1000000, "guarantee": "Kafolatli", "speed": "50K/kun"
    },
    "yt_view_fast": {
        "name": "👁 YouTube Tez Ko'rish",
        "description": "Tez yetkazib berish",
        "peakerr": {"id": 27360, "price_usd": 0.08},
        "smmmain": {"id": 1206, "price_usd": 0.09},
        "min": 100, "max": 500000, "guarantee": "Kafolatli", "speed": "100K/kun"
    },
    "yt_view_4000h": {
        "name": "⏱ YouTube 4000 soat ko'rish",
        "description": "Monetizatsiya uchun soatlik ko'rish",
        "peakerr": {"id": 27365, "price_usd": 0.10},
        "smmmain": {"id": 1207, "price_usd": 0.12},
        "min": 1000, "max": 100000, "guarantee": "Kafolatli", "speed": "10K/kun"
    },
    # Like
    "yt_like": {
        "name": "👍 YouTube Like",
        "description": "Videolarga like",
        "peakerr": {"id": 20363, "price_usd": 0.078},
        "smmmain": {"id": 1209, "price_usd": 0.09},
        "min": 10, "max": 100000, "guarantee": "30 kun", "speed": "50K/kun"
    },
    "yt_like_premium": {
        "name": "👍 YouTube Premium Like",
        "description": "Yuqori sifatli like",
        "peakerr": {"id": 20365, "price_usd": 0.15},
        "smmmain": {"id": 1210, "price_usd": 0.18},
        "min": 10, "max": 50000, "guarantee": "60 kun", "speed": "20K/kun"
    },
    # Comment
    "yt_comment": {
        "name": "💬 YouTube Comment",
        "description": "Videolarga izoh",
        "peakerr": {"id": 20370, "price_usd": 0.80},
        "smmmain": {"id": 1215, "price_usd": 0.90},
        "min": 5, "max": 5000, "guarantee": "Yo'q", "speed": "500/kun"
    },
    "yt_comment_custom": {
        "name": "💬 YouTube Custom Comment",
        "description": "O'zingiz yozgan izoh",
        "peakerr": {"id": 20375, "price_usd": 1.50},
        "smmmain": {"id": 1216, "price_usd": 1.60},
        "min": 1, "max": 1000, "guarantee": "Yo'q", "speed": "200/kun"
    },
    # Share
    "yt_share": {
        "name": "🔄 YouTube Share",
        "description": "Videolarni ulashish",
        "peakerr": {"id": 20380, "price_usd": 0.05},
        "smmmain": {"id": 1220, "price_usd": 0.06},
        "min": 100, "max": 100000, "guarantee": "Yo'q", "speed": "50K/kun"
    },
    
    # ===================== TIKTOK =====================
    # Follower
    "tt_follower": {
        "name": "👥 TikTok Follower",
        "description": "Profilingizga follower",
        "peakerr": {"id": 28047, "price_usd": 0.22},
        "smmmain": {"id": 1301, "price_usd": 0.25},
        "min": 50, "max": 500000, "guarantee": "30 kun", "speed": "20K/kun"
    },
    "tt_follower_premium": {
        "name": "👥 TikTok Premium Follower",
        "description": "Yuqori sifatli, faol follower",
        "peakerr": {"id": 28050, "price_usd": 0.45},
        "smmmain": {"id": 1302, "price_usd": 0.50},
        "min": 50, "max": 100000, "guarantee": "60 kun", "speed": "10K/kun"
    },
    # Ko'rish
    "tt_view": {
        "name": "👁 TikTok Ko'rish",
        "description": "Videolarga ko'rish",
        "peakerr": {"id": 14075, "price_usd": 0.0002},
        "smmmain": {"id": 1305, "price_usd": 0.0005},
        "min": 100, "max": 100000000, "guarantee": "Kafolatli", "speed": "10M/soat"
    },
    "tt_view_live": {
        "name": "👁 TikTok Live Ko'rish",
        "description": "Jonli efirga ko'ruvchi",
        "peakerr": {"id": 14080, "price_usd": 0.02},
        "smmmain": {"id": 1306, "price_usd": 0.025},
        "min": 10, "max": 50000, "guarantee": "Yo'q", "speed": "1K/daqiqa"
    },
    # Like
    "tt_like": {
        "name": "❤️ TikTok Like",
        "description": "Videolarga like",
        "peakerr": {"id": 25003, "price_usd": 0.022},
        "smmmain": {"id": 1309, "price_usd": 0.03},
        "min": 50, "max": 1000000, "guarantee": "Yo'q", "speed": "100K/kun"
    },
    "tt_like_premium": {
        "name": "❤️ TikTok Premium Like",
        "description": "Yuqori sifatli like",
        "peakerr": {"id": 25005, "price_usd": 0.05},
        "smmmain": {"id": 1310, "price_usd": 0.06},
        "min": 50, "max": 500000, "guarantee": "30 kun", "speed": "50K/kun"
    },
    # Comment
    "tt_comment": {
        "name": "💬 TikTok Comment",
        "description": "Videolarga izoh",
        "peakerr": {"id": 25010, "price_usd": 0.60},
        "smmmain": {"id": 1315, "price_usd": 0.70},
        "min": 5, "max": 10000, "guarantee": "Yo'q", "speed": "1K/kun"
    },
    "tt_comment_custom": {
        "name": "💬 TikTok Custom Comment",
        "description": "O'zingiz yozgan izoh",
        "peakerr": {"id": 25015, "price_usd": 1.20},
        "smmmain": {"id": 1316, "price_usd": 1.30},
        "min": 1, "max": 1000, "guarantee": "Yo'q", "speed": "300/kun"
    },
    # Share
    "tt_share": {
        "name": "🔄 TikTok Share",
        "description": "Videolarni ulashish",
        "peakerr": {"id": 25020, "price_usd": 0.03},
        "smmmain": {"id": 1320, "price_usd": 0.04},
        "min": 100, "max": 1000000, "guarantee": "Yo'q", "speed": "100K/kun"
    },
    # Save
    "tt_save": {
        "name": "📥 TikTok Save/Saqlash",
        "description": "Videolarni saqlash",
        "peakerr": {"id": 25025, "price_usd": 0.04},
        "smmmain": {"id": 1325, "price_usd": 0.05},
        "min": 50, "max": 500000, "guarantee": "Yo'q", "speed": "50K/kun"
    },
}

# TELEGRAM_SERVICES ni SERVICES_MAP ga qo'shish
for key, value in TELEGRAM_SERVICES.items():
    if key not in SERVICES_MAP:
        SERVICES_MAP[key] = {
            "name": f"{value['emoji']} {value['name']}",
            "description": value['description'],
            "peakerr": value.get('peakerr'),
            "smmmain": value.get('smmmain'),
            "min": value['min'],
            "max": value['max'],
            "guarantee": value['guarantee'],
            "speed": value['speed']
        }


# ==================== HELPER FUNKSIYALAR ====================
def rub_to_som(rub_price):
    """RUB dan SO'M ga konvertatsiya - sozlamalardan kurs va ustama oladi"""
    rate = get_rub_rate()
    markup = 1 + (get_markup_percent() / 100)
    return int(rub_price * rate * markup)

def usd_to_som(usd_price):
    """USD dan SO'M ga konvertatsiya - sozlamalardan kurs va ustama oladi"""
    rate = get_usd_rate()
    markup = 1 + (get_markup_percent() / 100)
    return int(usd_price * rate * markup)

def get_best_service_price(service_key):
    if service_key not in SERVICES_MAP:
        return None, None, None
    
    info = SERVICES_MAP[service_key]
    peakerr = info.get("peakerr")
    smmmain = info.get("smmmain")
    
    best_panel = None
    best_price = float('inf')
    best_id = None
    
    if peakerr:
        price = peakerr["price_usd"]
        if price < best_price:
            best_price = price
            best_panel = "peakerr"
            best_id = peakerr["id"]
    
    if smmmain:
        price = smmmain["price_usd"]
        if price < best_price:
            best_price = price
            best_panel = "smmmain"
            best_id = smmmain["id"]
    
    if best_panel:
        rate = get_usd_rate()
        markup = 1 + (get_markup_percent() / 100)
        price_som = int(best_price * rate * markup)
        return best_panel, best_id, price_som
    
    return None, None, None


def get_service_details_text(service_key):
    if service_key not in SERVICES_MAP:
        return "Ma'lumot topilmadi", 0, 100, 10000
    
    info = SERVICES_MAP[service_key]
    best_panel, best_id, price_som = get_best_service_price(service_key)
    
    if not best_panel:
        return "Xizmat mavjud emas", 0, 100, 10000
    
    min_qty = info["min"]
    max_qty = info["max"]
    guarantee = info["guarantee"]
    speed = info["speed"]
    name = info["name"]
    
    panel_emoji = "🔷" if best_panel == "peakerr" else "🔶"
    
    text = f"📦 <b>{name}</b>\n\n"
    text += f"💰 <b>Narx:</b> {price_som:,} so'm / 1000 ta\n"
    text += f"📊 <b>Min:</b> {min_qty:,} | <b>Max:</b> {max_qty:,}\n"
    text += f"🛡 <b>Kafolat:</b> {guarantee}\n"
    text += f"⚡ <b>Tezlik:</b> {speed}\n"
    text += f"{panel_emoji} <b>Panel:</b> {best_panel.upper()}\n"
    
    return text, price_som, min_qty, max_qty


def get_dynamic_price(service_key):
    """Xizmat uchun dinamik narx hisoblash"""
    if service_key not in SERVICES_MAP:
        return 0
    
    info = SERVICES_MAP[service_key]
    peakerr = info.get("peakerr")
    smmmain = info.get("smmmain")
    
    best_price = float('inf')
    
    if peakerr:
        if peakerr["price_usd"] < best_price:
            best_price = peakerr["price_usd"]
    
    if smmmain:
        if smmmain["price_usd"] < best_price:
            best_price = smmmain["price_usd"]
    
    if best_price == float('inf'):
        return 0
    
    rate = get_usd_rate()
    markup = 1 + (get_markup_percent() / 100)
    return int(best_price * rate * markup)


def telegram_members_dynamic():
    """Telegram Obunachi - Dinamik narxlar bilan"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="━━━ 👥 OBUNACHI ━━━", callback_data="section_tg"))
    
    services = [
        ("tg_member_cheap", "👥 Eng arzon", "tg_member_1"),
        ("tg_member_30day", "👥 30 kun kafolat", "tg_member_5"),
        ("tg_member_60day", "👥 60 kun kafolat", "tg_member_6"),
        ("tg_member_90day", "👥 90 kun kafolat", "tg_member_9"),
        ("tg_member_nodrop", "👥 No Drop", "tg_member_12"),
        ("tg_member_real", "👥 Real", "tg_member_8"),
        ("tg_member_high", "👥 High Quality", "tg_member_11"),
    ]
    
    for service_key, name, callback in services:
        price = get_dynamic_price(service_key)
        if price > 0:
            builder.row(InlineKeyboardButton(
                text=f"{name} | {price:,} so'm",
                callback_data=callback
            ))
    
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_telegram"))
    return builder.as_markup()


def telegram_premium_members_dynamic():
    """Telegram Premium Obunachi - Dinamik narxlar bilan"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="━━━ ⭐ PREMIUM OBUNACHI ━━━", callback_data="section_tg"))
    
    price = get_dynamic_price("tg_member_premium")
    if price > 0:
        builder.row(InlineKeyboardButton(
            text=f"⭐ Premium Obunachi | {price:,} so'm",
            callback_data="tg_member_premium_1"
        ))
    
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_telegram"))
    return builder.as_markup()


def telegram_views_dynamic():
    """Telegram Ko'rish - Dinamik narxlar bilan"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="━━━ 👁 KO'RISH ━━━", callback_data="section_tg"))
    
    services = [
        ("tg_view_cheap", "👁 1 Post Eng arzon", "tg_view_1"),
        ("tg_view", "👁 1 Post", "tg_view_2"),
        ("tg_view_instant", "👁 Instant", "tg_view_3"),
        ("tg_view_fast", "👁 Tez", "tg_view_4"),
        ("tg_view_last10", "👁 So'nggi 10 Post", "tg_view_5"),
        ("tg_view_last20", "👁 So'nggi 20 Post", "tg_view_6"),
        ("tg_story_view", "👁 Story Ko'rish", "tg_view_7"),
    ]
    
    for service_key, name, callback in services:
        price = get_dynamic_price(service_key)
        if price > 0:
            builder.row(InlineKeyboardButton(
                text=f"{name} | {price:,} so'm",
                callback_data=callback
            ))
    
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_telegram"))
    return builder.as_markup()


def telegram_reactions_dynamic():
    """Telegram Reaksiya - Dinamik narxlar bilan"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="━━━ 👍 REAKSIYA ━━━", callback_data="section_tg"))
    
    services = [
        ("tg_reaction", "👍 Pozitiv Mix", "tg_reaction_1"),
        ("tg_reaction_like", "👍 Like", "tg_reaction_2"),
        ("tg_reaction_heart", "❤️ Heart", "tg_reaction_3"),
        ("tg_reaction_fire", "🔥 Fire", "tg_reaction_4"),
        ("tg_reaction_views", "👍 Reaksiya + Ko'rish", "tg_reaction_5"),
    ]
    
    for service_key, name, callback in services:
        price = get_dynamic_price(service_key)
        if price > 0:
            builder.row(InlineKeyboardButton(
                text=f"{name} | {price:,} so'm",
                callback_data=callback
            ))
    
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_telegram"))
    return builder.as_markup()


def instagram_services_dynamic():
    """Instagram xizmatlari - Dinamik narxlar bilan"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="━━━ 📸 INSTAGRAM ━━━", callback_data="section_ig"))
    
    services = [
        ("ig_follower", "👥 Follower", "ig_follower"),
        ("ig_follower_premium", "👥 Premium Follower", "ig_follower_premium"),
        ("ig_like", "❤️ Like", "ig_like"),
        ("ig_view", "👁 Video Ko'rish", "ig_view"),
        ("ig_reel_view", "👁 Reels Ko'rish", "ig_reel_view"),
        ("ig_comment", "💬 Comment", "ig_comment"),
    ]
    
    for service_key, name, callback in services:
        price = get_dynamic_price(service_key)
        if price > 0:
            builder.row(InlineKeyboardButton(
                text=f"{name} | {price:,} so'm",
                callback_data=callback
            ))
    
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_services"))
    return builder.as_markup()


def youtube_services_dynamic():
    """YouTube xizmatlari - Dinamik narxlar bilan"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="━━━ ▶️ YOUTUBE ━━━", callback_data="section_yt"))
    
    services = [
        ("yt_subscriber", "👥 Subscriber", "yt_subscriber"),
        ("yt_subscriber_premium", "👥 Premium Subscriber", "yt_subscriber_premium"),
        ("yt_view", "👁 Ko'rish", "yt_view"),
        ("yt_like", "👍 Like", "yt_like"),
        ("yt_comment", "💬 Comment", "yt_comment"),
    ]
    
    for service_key, name, callback in services:
        price = get_dynamic_price(service_key)
        if price > 0:
            builder.row(InlineKeyboardButton(
                text=f"{name} | {price:,} so'm",
                callback_data=callback
            ))
    
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_services"))
    return builder.as_markup()


def tiktok_services_dynamic():
    """TikTok xizmatlari - Dinamik narxlar bilan"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="━━━ 🎵 TIKTOK ━━━", callback_data="section_tt"))
    
    services = [
        ("tt_follower", "👥 Follower", "tt_follower"),
        ("tt_follower_premium", "👥 Premium Follower", "tt_follower_premium"),
        ("tt_view", "👁 Ko'rish", "tt_view"),
        ("tt_like", "❤️ Like", "tt_like"),
        ("tt_comment", "💬 Comment", "tt_comment"),
    ]
    
    for service_key, name, callback in services:
        price = get_dynamic_price(service_key)
        if price > 0:
            builder.row(InlineKeyboardButton(
                text=f"{name} | {price:,} so'm",
                callback_data=callback
            ))
    
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_services"))
    return builder.as_markup()


async def get_all_api_balances():
    loop = asyncio.get_event_loop()
    results = await asyncio.gather(
        loop.run_in_executor(None, smm_api.get_all_balances),
        loop.run_in_executor(None, sms_api.get_balance),
        return_exceptions=True
    )
    
    smm_balances = results[0] if not isinstance(results[0], Exception) else {}
    sms_balance = results[1] if not isinstance(results[1], Exception) else 0.0
    
    peakerr_data = smm_balances.get("peakerr", {})
    smmmain_data = smm_balances.get("smmmain", {})
    
    return {
        'peakerr': peakerr_data.get("balance", 0) if isinstance(peakerr_data, dict) else 0,
        'smmmain': smmmain_data.get("balance", 0) if isinstance(smmmain_data, dict) else 0,
        'sms': sms_balance
    }


def get_payment_info(method, amount):
    """To'lov ma'lumotlarini olish - avval sozlamalardan, keyin config dan"""
    # Avval sozlamalardan tekshirish
    try:
        from database import get_setting
        card = get_setting('card_number', '')
        name = get_setting('card_holder', '')
        
        if card and name and card != '9860 **** **** ****':
            return f"💳 Karta: <code>{card}</code>\n👤 Egasi: {name}"
    except:
        pass
    
    # Sozlamalarda yo'q bo'lsa config dan olish
    card_info = PAYMENT_CARDS.get(method, {"card": "0000 0000 0000 0000", "name": "IDEAL SMM"})
    card = card_info["card"]
    name = card_info["name"]
    return f"💳 Karta: <code>{card}</code>\n👤 Egasi: {name}"


# ==================== HANDLERS ====================

@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name
    
    # Bloklangan foydalanuvchini tekshirish
    user = get_user(user_id)
    if user and len(user) > 8 and user[8] == 1:
        await message.answer("🚫 <b>Sizning hisobingiz bloklangan!</b>\n\nAdmin bilan bog'laning: @komilov_manager")
        return
    
    # Referal tekshirish
    args = message.text.split()
    referral_id = None
    if len(args) > 1 and args[1].startswith("ref_"):
        try:
            referral_id = int(args[1].split("_")[1])
            if referral_id == user_id:
                referral_id = None
        except:
            referral_id = None
    
    # Foydalanuvchini bazaga qo'shish
    bonus_given = add_user(user_id, username, full_name, referral_id)
    
    user = get_user(user_id)
    balance = user[3] if user else 0
    
    welcome_text = "🎯 <b>SMM XIZMATLARI | 24/7</b>\n"
    welcome_text += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    if bonus_given:
        bonus_amount = get_referral_bonus()
        welcome_text += f"🎁 <b>Tabriklaymiz!</b> Sizga {bonus_amount:,} so'm bonus berildi!\n\n"
        try:
            await bot.send_message(
                referral_id,
                f"🎉 <b>Yangi referal!</b>\n\n👤 {full_name} sizning havolangiz orqali qo'shildi!\n💰 Sizga {bonus_amount:,} so'm bonus berildi!"
            )
        except:
            pass
    
    welcome_text += f"👋 Assalomu alaykum, <b>{full_name}</b>!\n\n"
    welcome_text += "📱 <b>Bizning xizmatlar:</b>\n"
    welcome_text += "├ 📲 Telegram obunachi, ko'rish, reaksiya\n"
    welcome_text += "├ 📸 Instagram follower, like, view\n"
    welcome_text += "├ ▶️ YouTube subscriber, view, like\n"
    welcome_text += "├ 🎵 TikTok follower, like, view\n"
    welcome_text += "└ 📱 Virtual telefon raqamlar (SMS)\n\n"
    welcome_text += f"💰 <b>Balansingiz:</b> {balance:,.0f} so'm\n\n"
    welcome_text += "👇 Quyidagi tugmalardan birini tanlang:"
    
    await message.answer(welcome_text, reply_markup=main_menu())


@router.message(Command("help"))
async def cmd_help(message: Message):
    text = "❓ <b>YORDAM</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += "📋 <b>Buyruqlar:</b>\n"
    text += "/start - Botni ishga tushirish\n"
    text += "/help - Yordam\n"
    text += "/balance - Balansni ko'rish\n"
    text += "/orders - Buyurtmalarim\n"
    text += "/referral - Referal dasturi\n\n"
    text += "💡 <b>Qanday ishlaydi?</b>\n"
    text += "1️⃣ Balansni to'ldiring\n"
    text += "2️⃣ Kerakli xizmatni tanlang\n"
    text += "3️⃣ Havola va miqdorni kiriting\n"
    text += "4️⃣ Buyurtma avtomatik bajariladi\n"
    
    await message.answer(text, reply_markup=main_menu())


@router.message(Command("balance"))
async def cmd_balance(message: Message):
    user_id = message.from_user.id
    balance = get_balance(user_id)
    
    text = "💰 <b>BALANS</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += f"💳 Sizning balansingiz: <b>{balance:,.0f}</b> so'm\n\n"
    text += "💵 Balansni to'ldirish uchun \"💵 Hisob to'ldirish\" tugmasini bosing."
    
    await message.answer(text, reply_markup=main_menu())


@router.message(Command("orders"))
async def cmd_orders(message: Message):
    user_id = message.from_user.id
    orders = get_user_orders(user_id)
    
    if not orders:
        await message.answer("📭 <b>Buyurtmalaringiz yo'q!</b>\n\nBirinchi buyurtmangizni bering.", reply_markup=main_menu())
        return
    
    text = "📦 <b>BUYURTMALARIM</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for order in orders[:10]:
        oid = order[0]
        service = order[2] if len(order) > 2 else "Noma'lum"
        qty = order[4] if len(order) > 4 else 0
        price = order[5] if len(order) > 5 else 0
        status = order[6] if len(order) > 6 else "pending"
        
        status_emoji = {
            "pending": "⏳ Kutilmoqda",
            "processing": "🔄 Jarayonda",
            "completed": "✅ Bajarildi",
            "canceled": "❌ Bekor qilindi",
            "partial": "⚠️ Qisman"
        }.get(status, "❓ Noma'lum")
        
        text += f"🆔 #{oid}\n"
        text += f"├ 📦 {service[:25]}\n"
        text += f"├ 📊 {qty:,} ta | 💰 {price:,.0f} so'm\n"
        text += f"└ {status_emoji}\n\n"
    
    await message.answer(text, reply_markup=main_menu())


@router.message(Command("referral"))
async def cmd_referral(message: Message):
    user_id = message.from_user.id
    ref_count, ref_earnings = get_referral_stats(user_id)
    
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start=ref_{user_id}"
    bonus_amount = get_referral_bonus()
    
    text = "👥 <b>REFERAL DASTURI</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += "🎁 <b>Qanday ishlaydi?</b>\n"
    text += f"Do'stingizni taklif qiling va har bir referal uchun <b>{bonus_amount:,} so'm</b> oling!\n\n"
    text += f"📊 <b>Sizning statistikangiz:</b>\n"
    text += f"├ 👥 Referallar: <b>{ref_count}</b>\n"
    text += f"└ 💰 Daromad: <b>{ref_earnings:,.0f}</b> so'm\n\n"
    text += f"🔗 <b>Sizning havolangiz:</b>\n"
    text += f"<code>{ref_link}</code>\n\n"
    text += "👇 Tugmani bosib do'stlaringizga yuboring!"
    
    await message.answer(text, reply_markup=referral_share_inline(ref_link, bot_info.username))


# ==================== ADMIN PANEL ====================

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Admin panel - Asosiy menyu"""
    user_id = message.from_user.id
    
    if user_id != ADMIN_ID:
        await message.answer("⛔ <b>Sizga ruxsat yo'q!</b>")
        return
    
    text = "🛡 <b>ADMIN PANEL</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += "👋 Xush kelibsiz, <b>Admin</b>!\n\n"
    text += "👇 Quyidagi bo'limlardan birini tanlang:"
    
    await message.answer(text, reply_markup=admin_main_menu())


async def show_admin_stats(message: Message):
    """Professional statistika ko'rsatish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # ============ BUGUNGI STATISTIKA ============
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    # Bugungi foydalanuvchilar
    cursor.execute("SELECT COUNT(*) FROM users WHERE created_at LIKE ?", (f"{today}%",))
    today_users = cursor.fetchone()[0]
    
    # Kechagi foydalanuvchilar
    cursor.execute("SELECT COUNT(*) FROM users WHERE created_at LIKE ?", (f"{yesterday}%",))
    yesterday_users = cursor.fetchone()[0]
    
    # Bugungi buyurtmalar va daromad
    cursor.execute("SELECT COUNT(*), COALESCE(SUM(price), 0) FROM orders WHERE created_at LIKE ?", (f"{today}%",))
    today_data = cursor.fetchone()
    today_orders = today_data[0] or 0
    today_revenue = today_data[1] or 0
    
    # Kechagi buyurtmalar va daromad
    cursor.execute("SELECT COUNT(*), COALESCE(SUM(price), 0) FROM orders WHERE created_at LIKE ?", (f"{yesterday}%",))
    yesterday_data = cursor.fetchone()
    yesterday_orders = yesterday_data[0] or 0
    yesterday_revenue = yesterday_data[1] or 0
    
    # ============ HAFTALIK STATISTIKA ============
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    cursor.execute("SELECT COUNT(*) FROM users WHERE created_at >= ?", (week_ago,))
    week_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*), COALESCE(SUM(price), 0) FROM orders WHERE created_at >= ?", (week_ago,))
    week_data = cursor.fetchone()
    week_orders = week_data[0] or 0
    week_revenue = week_data[1] or 0
    
    # ============ OYLIK STATISTIKA ============
    month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    cursor.execute("SELECT COUNT(*) FROM users WHERE created_at >= ?", (month_ago,))
    month_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*), COALESCE(SUM(price), 0) FROM orders WHERE created_at >= ?", (month_ago,))
    month_data = cursor.fetchone()
    month_orders = month_data[0] or 0
    month_revenue = month_data[1] or 0
    
    # ============ UMUMIY STATISTIKA ============
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*), COALESCE(SUM(price), 0) FROM orders")
    total_data = cursor.fetchone()
    total_orders = total_data[0] or 0
    total_revenue = total_data[1] or 0
    
    # Aktiv foydalanuvchilar (buyurtma berganlar)
    cursor.execute("SELECT COUNT(DISTINCT user_id) FROM orders")
    active_users = cursor.fetchone()[0]
    
    # Kutilayotgan to'lovlar
    cursor.execute("SELECT COUNT(*), COALESCE(SUM(amount), 0) FROM payments WHERE status='pending'")
    pending_data = cursor.fetchone()
    pending_count = pending_data[0] or 0
    pending_amount = pending_data[1] or 0
    
    # Tasdiqlangan to'lovlar (bugun)
    cursor.execute("SELECT COUNT(*), COALESCE(SUM(amount), 0) FROM payments WHERE status='approved' AND created_at LIKE ?", (f"{today}%",))
    approved_data = cursor.fetchone()
    approved_count = approved_data[0] or 0
    approved_amount = approved_data[1] or 0
    
    # ============ BUYURTMA HOLATLARI ============
    cursor.execute("SELECT status, COUNT(*) FROM orders GROUP BY status")
    order_statuses = dict(cursor.fetchall())
    
    # ============ TOP XIZMATLAR ============
    cursor.execute("""
        SELECT service_type, COUNT(*) as cnt, SUM(price) as revenue 
        FROM orders 
        GROUP BY service_type 
        ORDER BY cnt DESC 
        LIMIT 5
    """)
    top_services = cursor.fetchall()
    
    # ============ TOP PLATFORMALAR ============
    cursor.execute("""
        SELECT platform, COUNT(*) as cnt, SUM(price) as revenue 
        FROM orders 
        WHERE platform IS NOT NULL
        GROUP BY platform 
        ORDER BY cnt DESC 
        LIMIT 5
    """)
    top_platforms = cursor.fetchall()
    
    # ============ OXIRGI 7 KUN GRAFIK ============
    daily_stats = []
    for i in range(6, -1, -1):
        day = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        day_short = (datetime.now() - timedelta(days=i)).strftime("%d/%m")
        cursor.execute("SELECT COUNT(*), COALESCE(SUM(price), 0) FROM orders WHERE created_at LIKE ?", (f"{day}%",))
        day_data = cursor.fetchone()
        daily_stats.append((day_short, day_data[0] or 0, day_data[1] or 0))
    
    conn.close()
    
    # API balanslarini olish
    api_balances = await get_all_api_balances()
    
    # Premium statistikasi
    from database import get_premium_stats
    premium_stats = get_premium_stats()
    
    # ============ MATN YARATISH ============
    # O'sish/tushish ko'rsatkichlari
    user_trend = "📈" if today_users >= yesterday_users else "📉"
    order_trend = "📈" if today_orders >= yesterday_orders else "📉"
    revenue_trend = "📈" if today_revenue >= yesterday_revenue else "📉"
    
    text = "🛡 <b>ADMIN PANEL - STATISTIKA</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # BUGUNGI
    text += f"📅 <b>BUGUN ({today})</b>\n"
    text += f"┣ 👥 Yangi foydalanuvchilar: <b>{today_users}</b> {user_trend}\n"
    text += f"┣ 📦 Buyurtmalar: <b>{today_orders}</b> {order_trend}\n"
    text += f"┣ 💰 Daromad: <b>{today_revenue:,.0f}</b> so'm {revenue_trend}\n"
    text += f"┗ ✅ To'lovlar: <b>{approved_count}</b> ({approved_amount:,.0f} so'm)\n\n"
    
    # HAFTALIK
    text += f"📊 <b>HAFTALIK (7 kun)</b>\n"
    text += f"┣ 👥 Foydalanuvchilar: <b>{week_users}</b>\n"
    text += f"┣ 📦 Buyurtmalar: <b>{week_orders}</b>\n"
    text += f"┗ 💰 Daromad: <b>{week_revenue:,.0f}</b> so'm\n\n"
    
    # OYLIK
    text += f"📈 <b>OYLIK (30 kun)</b>\n"
    text += f"┣ 👥 Foydalanuvchilar: <b>{month_users}</b>\n"
    text += f"┣ 📦 Buyurtmalar: <b>{month_orders}</b>\n"
    text += f"┗ 💰 Daromad: <b>{month_revenue:,.0f}</b> so'm\n\n"
    
    # UMUMIY
    text += f"🏆 <b>UMUMIY</b>\n"
    text += f"┣ 👥 Jami foydalanuvchilar: <b>{total_users:,}</b>\n"
    text += f"┣ 🎯 Aktiv foydalanuvchilar: <b>{active_users}</b>\n"
    text += f"┣ 📦 Jami buyurtmalar: <b>{total_orders:,}</b>\n"
    text += f"┗ 💰 Jami daromad: <b>{total_revenue:,.0f}</b> so'm\n\n"
    
    # TO'LOVLAR
    text += f"💳 <b>TO'LOVLAR</b>\n"
    text += f"┗ ⏳ Kutilayotgan: <b>{pending_count}</b> ({pending_amount:,.0f} so'm)\n\n"
    
    # BUYURTMA HOLATLARI
    text += f"📋 <b>BUYURTMA HOLATLARI</b>\n"
    text += f"┣ ⏳ Kutilmoqda: <b>{order_statuses.get('pending', 0)}</b>\n"
    text += f"┣ 🔄 Jarayonda: <b>{order_statuses.get('processing', 0)}</b>\n"
    text += f"┣ ✅ Bajarildi: <b>{order_statuses.get('completed', 0)}</b>\n"
    text += f"┣ ❌ Bekor: <b>{order_statuses.get('canceled', 0)}</b>\n"
    text += f"┗ ⚠️ Qisman: <b>{order_statuses.get('partial', 0)}</b>\n\n"
    
    # API BALANSLAR
    text += f"💰 <b>API BALANSLAR</b>\n"
    text += f"┣ 🔵 Peakerr: <b>${api_balances['peakerr']:.2f}</b>\n"
    text += f"┣ 🟠 SMMMain: <b>${api_balances['smmmain']:.2f}</b>\n"
    text += f"┗ 📱 VAK-SMS: <b>{api_balances['sms']:.2f}</b> RUB\n\n"
    
    # PREMIUM STATISTIKA
    text += f"⭐ <b>PREMIUM OBUNA</b>\n"
    text += f"┣ 📦 Jami sotilgan: <b>{premium_stats['total_sold']}</b>\n"
    text += f"┣ ✅ Aktiv premium: <b>{premium_stats['active_count']}</b>\n"
    text += f"┗ 💰 Jami daromad: <b>{premium_stats['total_revenue']:,.0f}</b> so'm\n\n"
    
    # OXIRGI 7 KUN GRAFIK
    text += f"📊 <b>OXIRGI 7 KUN</b>\n"
    max_orders = max([d[1] for d in daily_stats]) if daily_stats else 1
    for day_short, orders, revenue in daily_stats:
        bar_len = int((orders / max(max_orders, 1)) * 8)
        bar = "█" * bar_len + "░" * (8 - bar_len)
        text += f"<code>{day_short}</code> {bar} <b>{orders}</b> ({revenue:,.0f})\n"
    
    await message.answer(text, reply_markup=admin_main_menu())


# ==================== TEXT HANDLERS ====================

@router.message(F.text == "📁 Xizmatlar")
async def services_menu(message: Message):
    """Xizmatlar menyusi"""
    await message.answer(
        "✅ <b>Bizning xizmatlarimizni tanlaganingizdan xursandmiz!</b>\n\n👇 Quyidagi Ijtimoiy tarmoqlardan birini tanlang.",
        reply_markup=social_networks_menu()
    )


@router.message(F.text == "✈️ Telegram")
async def telegram_menu(message: Message):
    """Telegram xizmatlari"""
    text = "✈️ <b>TELEGRAM XIZMATLARI</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += "📌 <b>Narxlar 1000 dona uchun</b>\n"
    text += "⚡ <b>Tez va sifatli yetkazib berish</b>\n"
    text += "✅ <b>Kafolat beriladi</b>\n\n"
    text += "👇 Xizmat turini tanlang:"
    await message.answer(text, reply_markup=telegram_services_inline())


@router.message(F.text == "📸 Instagram")
async def instagram_menu(message: Message):
    """Instagram xizmatlari"""
    text = "📸 <b>INSTAGRAM XIZMATLARI</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += "📌 <b>Narxlar 1000 dona uchun</b>\n"
    text += "⚡ <b>Tez va sifatli yetkazib berish</b>\n"
    text += "✅ <b>Kafolat beriladi</b>\n\n"
    text += "👇 Xizmat turini tanlang:"
    await message.answer(text, reply_markup=instagram_services_inline())


@router.message(F.text == "▶️ Youtube")
async def youtube_menu(message: Message):
    """YouTube xizmatlari"""
    text = "▶️ <b>YOUTUBE XIZMATLARI</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += "📌 <b>Narxlar 1000 dona uchun</b>\n"
    text += "⚡ <b>Tez va sifatli yetkazib berish</b>\n"
    text += "✅ <b>Kafolat beriladi</b>\n\n"
    text += "👇 Xizmat turini tanlang:"
    await message.answer(text, reply_markup=youtube_services_inline())


@router.message(F.text == "🎵 Tik-Tok")
async def tiktok_menu(message: Message):
    """TikTok xizmatlari"""
    text = "🎵 <b>TIKTOK XIZMATLARI</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += "📌 <b>Narxlar 1000 dona uchun</b>\n"
    text += "⚡ <b>Tez va sifatli yetkazib berish</b>\n"
    text += "✅ <b>Kafolat beriladi</b>\n\n"
    text += "👇 Xizmat turini tanlang:"
    await message.answer(text, reply_markup=tiktok_services_inline())


@router.message(F.text == "⬅️ Orqaga")
async def back_to_main(message: Message):
    """Asosiy menyuga qaytish"""
    await message.answer("🏠 Asosiy menyu", reply_markup=main_menu())


@router.message(F.text == "💰 Mening hisobim")
async def check_balance(message: Message):
    user_id = message.from_user.id
    balance = get_balance(user_id)
    user = get_user(user_id)
    
    # Ro'yxatdan o'tgan sana - 7-indeks (0: user_id, 1: username, 2: full_name, 3: balance, 4: referral_id, 5: referral_count, 6: referral_earnings, 7: created_at, 8: is_banned)
    if user and len(user) > 7 and user[7]:
        try:
            created_date = user[7].split(" ")[0]  # "2026-01-01 12:00:00" -> "2026-01-01"
        except:
            created_date = user[7]
    else:
        created_date = "Noma'lum"
    
    # Premium status tekshirish
    from database import check_premium_status, get_premium_remaining_days
    is_premium = check_premium_status(user_id)
    premium_days = get_premium_remaining_days(user_id) if is_premium else 0
    
    text = "💰 <b>MENING HISOBIM</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += f"👤 <b>Ism:</b> {message.from_user.full_name}\n"
    text += f"🆔 <b>Telegram ID:</b> <code>{user_id}</code>\n"
    text += f"📅 <b>Ro'yxatdan o'tgan:</b> {created_date}\n\n"
    
    # Premium badge
    if is_premium:
        text += f"⭐ <b>Status:</b> PREMIUM ✨\n"
        text += f"📅 <b>Qolgan kun:</b> {premium_days} kun\n\n"
    else:
        text += f"👤 <b>Status:</b> Oddiy foydalanuvchi\n\n"
    
    text += f"💳 <b>Balans:</b> {balance:,.0f} so'm\n"
    
    await message.answer(text)


@router.message(F.text == "💵 Hisob to'ldirish")
async def add_balance(message: Message):
    await message.answer(
        "💵 <b>Hisob to'ldirish</b>\n\nTo'lov usulini tanlang:",
        reply_markup=payment_methods()
    )


@router.message(F.text == "🔍 Buyurtmalarim")
async def my_orders(message: Message):
    await cmd_orders(message)


@router.message(F.text == "🗣 Referal")
async def referral_menu(message: Message):
    await cmd_referral(message)


@router.inline_query()
async def inline_referral(query: InlineQuery):
    """Inline rejimda referal xabarini yuborish"""
    user_id = query.from_user.id
    bot_info = await bot.get_me()
    
    text = "🎁 <b>𝗦𝗶𝘇 𝘂𝗰𝗵𝘂𝗻 𝗮𝗷𝗼𝘆𝗶𝗯 𝘁𝗮𝗸𝗹𝗶𝗳!</b>\n\n"
    text += "🚀 <i>SMM xizmatlari bot orqali ijtimoiy tarmoqlaringizni rivojlantiring!</i>\n\n"
    text += "✅ 𝗧𝗲𝗹𝗲𝗴𝗿𝗮𝗺 obunachi\n"
    text += "✅ 𝗜𝗻𝘀𝘁𝗮𝗴𝗿𝗮𝗺 follower\n"
    text += "✅ 𝗬𝗼𝘂𝗧𝘂𝗯𝗲 subscriber\n"
    text += "✅ 𝗧𝗶𝗸𝗧𝗼𝗸 follower\n"
    text += "✅ Va boshqa ko'plab xizmatlar!\n\n"
    text += "💰 Ro'yxatdan o'ting va <b>𝗕𝗢𝗡𝗨𝗦</b> oling!\n\n"
    text += "👇 <b>Quyidagi tugmani bosing va boshlang!</b>"
    
    # Bot profil rasmi (cache'dan) yoki default
    global BOT_PHOTO_URL
    thumb_url = BOT_PHOTO_URL if BOT_PHOTO_URL else "https://i.postimg.cc/4xqMJPrz/smm-bot-logo.png"
    
    results = [
        InlineQueryResultArticle(
            id="referral_invite",
            title="🎁 Do'stni taklif qilish",
            description="Do'stingizga SMM Xizmatlari botini tavsiya qiling",
            thumbnail_url=thumb_url,
            input_message_content=InputTextMessageContent(
                message_text=text,
                parse_mode="HTML"
            ),
            reply_markup=referral_join_inline(bot_info.username, str(user_id))
        )
    ]
    
    await query.answer(results, cache_time=300, is_personal=True)


# ==================== ADMIN TUGMALAR HANDLERS ====================

@router.message(F.text == "📊 Statistika")
async def admin_stats_btn(message: Message):
    """Admin statistika tugmasi"""
    if message.from_user.id != ADMIN_ID:
        return
    await show_admin_stats(message)


@router.message(F.text == "📋 Buyurtmalar")
async def admin_orders_btn(message: Message, state: FSMContext):
    """Admin buyurtmalar bo'limi"""
    if message.from_user.id != ADMIN_ID:
        return
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Umumiy statistika
    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0]
    
    # Holat bo'yicha
    cursor.execute("SELECT status, COUNT(*) FROM orders GROUP BY status")
    status_counts = dict(cursor.fetchall())
    
    # Bugungi buyurtmalar
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT COUNT(*), COALESCE(SUM(price), 0) FROM orders WHERE created_at LIKE ?", (f"{today}%",))
    today_data = cursor.fetchone()
    today_count = today_data[0] or 0
    today_sum = today_data[1] or 0
    
    # Oxirgi 15 ta buyurtma
    cursor.execute("""
        SELECT o.id, o.user_id, o.service_type, o.quantity, o.price, o.status, o.created_at, u.full_name
        FROM orders o
        LEFT JOIN users u ON o.user_id = u.user_id
        ORDER BY o.id DESC
        LIMIT 15
    """)
    recent_orders = cursor.fetchall()
    
    conn.close()
    
    # Matn
    text = "📋 <b>BUYURTMALAR BO'LIMI</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    text += "📊 <b>UMUMIY STATISTIKA</b>\n"
    text += f"┣ 📦 Jami: <b>{total_orders:,}</b>\n"
    text += f"┣ ⏳ Kutilmoqda: <b>{status_counts.get('pending', 0)}</b>\n"
    text += f"┣ 🔄 Jarayonda: <b>{status_counts.get('processing', 0)}</b>\n"
    text += f"┣ ✅ Bajarildi: <b>{status_counts.get('completed', 0)}</b>\n"
    text += f"┣ ❌ Bekor: <b>{status_counts.get('canceled', 0)}</b>\n"
    text += f"┗ ⚠️ Qisman: <b>{status_counts.get('partial', 0)}</b>\n\n"
    
    text += f"📅 <b>BUGUN</b>: {today_count} ta | {today_sum:,.0f} so'm\n\n"
    
    text += "📝 <b>OXIRGI BUYURTMALAR</b>\n"
    
    for order in recent_orders:
        oid, user_id, service, qty, price, status, created, user_name = order
        
        status_emoji = {
            "pending": "⏳",
            "processing": "🔄",
            "completed": "✅",
            "canceled": "❌",
            "partial": "⚠️"
        }.get(status, "❓")
        
        service_short = (service[:18] + "..") if service and len(service) > 20 else (service or "N/A")
        
        text += f"{status_emoji} <b>#{oid}</b> | {service_short} | {price:,.0f}\n"
    
    text += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "❌ <b>Buyurtmani bekor qilish:</b>\n"
    text += "Buyurtma raqamini yozing (masalan: <code>123</code>)"
    
    await state.set_state(AdminState.waiting_for_cancel_order)
    await message.answer(text, reply_markup=admin_main_menu())


@router.message(AdminState.waiting_for_cancel_order)
async def process_cancel_order(message: Message, state: FSMContext):
    """Buyurtma raqamini qabul qilish va tasdiqlash so'rash"""
    if message.from_user.id != ADMIN_ID:
        return
    
    # Agar admin menyudan boshqa tugma bossa - holatni tozalash
    if message.text in ["📊 Statistika", "📋 Buyurtmalar", "👥 Foydalanuvchilar", "💳 To'lovlar", 
                        "📢 Xabar yuborish", "💰 Balans boshqarish", "💾 Zaxira nusxa", "⚙️ Sozlamalar", "/admin"]:
        await state.clear()
        return
    
    try:
        order_id = int(message.text.strip().replace("#", ""))
    except ValueError:
        await message.answer("❌ Noto'g'ri format! Faqat raqam kiriting (masalan: 123)")
        return
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Buyurtmani tekshirish
    cursor.execute("""
        SELECT o.id, o.user_id, o.service_type, o.quantity, o.price, o.status, u.full_name
        FROM orders o
        LEFT JOIN users u ON o.user_id = u.user_id
        WHERE o.id = ?
    """, (order_id,))
    order = cursor.fetchone()
    conn.close()
    
    if not order:
        await message.answer(f"❌ Buyurtma #{order_id} topilmadi!")
        return
    
    oid, user_id, service, qty, price, status, user_name = order
    
    if status == "canceled":
        await message.answer(f"⚠️ Buyurtma #{order_id} allaqachon bekor qilingan!")
        return
    
    if status == "completed":
        await message.answer(f"⚠️ Buyurtma #{order_id} allaqachon bajarilgan! Bekor qilib bo'lmaydi.")
        return
    
    # Buyurtma ma'lumotlarini saqlash
    await state.update_data(
        cancel_order_id=order_id,
        cancel_user_id=user_id,
        cancel_price=price,
        cancel_service=service
    )
    
    # Tasdiqlash so'rash
    status_text = {"pending": "⏳ Kutilmoqda", "processing": "🔄 Jarayonda"}.get(status, status)
    
    text = f"⚠️ <b>Buyurtmani bekor qilishni tasdiqlang:</b>\n\n"
    text += f"🆔 Buyurtma: <b>#{order_id}</b>\n"
    text += f"👤 Foydalanuvchi: {user_name or 'Nomalum'}\n"
    text += f"🆔 User ID: <code>{user_id}</code>\n"
    text += f"📦 Xizmat: {service}\n"
    text += f"📊 Miqdor: {qty:,} ta\n"
    text += f"💰 Narxi: <b>{price:,.0f}</b> so'm\n"
    text += f"📊 Holat: {status_text}\n\n"
    text += f"💵 Foydalanuvchiga <b>{price:,.0f}</b> so'm qaytariladi\n\n"
    text += f"✅ <b>Ha</b> - Bekor qilish\n"
    text += f"❌ <b>Yo'q</b> - Bekor qilmaslik"
    
    # Tasdiqlash tugmalari
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="✅ Ha, bekor qilish"),
        KeyboardButton(text="❌ Yo'q")
    )
    
    await state.set_state(AdminState.waiting_for_cancel_confirm)
    await message.answer(text, reply_markup=builder.as_markup(resize_keyboard=True))


@router.message(AdminState.waiting_for_cancel_confirm)
async def process_cancel_confirm(message: Message, state: FSMContext):
    """Bekor qilishni tasdiqlash"""
    if message.from_user.id != ADMIN_ID:
        return
    
    data = await state.get_data()
    order_id = data.get("cancel_order_id")
    user_id = data.get("cancel_user_id")
    price = data.get("cancel_price")
    service = data.get("cancel_service")
    
    if message.text == "❌ Yo'q":
        await state.clear()
        await message.answer("✅ Bekor qilish rad etildi.", reply_markup=admin_main_menu())
        return
    
    if message.text != "✅ Ha, bekor qilish":
        await message.answer("❌ Noto'g'ri tanlov! ✅ Ha yoki ❌ Yo'q tanlang.")
        return
    
    # Buyurtmani bekor qilish
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute("UPDATE orders SET status = 'canceled' WHERE id = ?", (order_id,))
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (price, user_id))
    
    # Foydalanuvchi ismini olish
    cursor.execute("SELECT full_name FROM users WHERE user_id = ?", (user_id,))
    user_row = cursor.fetchone()
    user_name = user_row[0] if user_row else user_id
    
    conn.commit()
    conn.close()
    
    # Admin uchun xabar
    text = f"✅ <b>Buyurtma bekor qilindi!</b>\n\n"
    text += f"🆔 Buyurtma: <b>#{order_id}</b>\n"
    text += f"👤 Foydalanuvchi: {user_name}\n"
    text += f"📦 Xizmat: {service}\n"
    text += f"💰 Qaytarildi: <b>{price:,.0f}</b> so'm\n"
    
    await message.answer(text, reply_markup=admin_main_menu())
    
    # Foydalanuvchiga xabar
    try:
        await bot.send_message(
            user_id,
            f"❌ <b>Buyurtmangiz bekor qilindi!</b>\n\n"
            f"🆔 Buyurtma: #{order_id}\n"
            f"📦 Xizmat: {service}\n"
            f"💰 Balansingizga qaytarildi: <b>{price:,.0f}</b> so'm\n\n"
            f"Yangi balans: <b>{get_balance(user_id):,.0f}</b> so'm"
        )
    except:
        pass
    
    await state.clear()


# ==================== FOYDALANUVCHILAR BO'LIMI ====================

@router.message(F.text == "👥 Foydalanuvchilar")
async def admin_users_btn(message: Message, state: FSMContext):
    """Foydalanuvchilar bo'limi"""
    if message.from_user.id != ADMIN_ID:
        return
    
    await state.clear()
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Umumiy statistika
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    # Bugun qo'shilganlar
    cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(created_at) = DATE('now')")
    today_users = cursor.fetchone()[0]
    
    # Haftalik
    cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(created_at) >= DATE('now', '-7 days')")
    week_users = cursor.fetchone()[0]
    
    # Oylik
    cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(created_at) >= DATE('now', '-30 days')")
    month_users = cursor.fetchone()[0]
    
    # Balanslar
    cursor.execute("SELECT SUM(balance) FROM users")
    total_balance = cursor.fetchone()[0] or 0
    
    # Faol foydalanuvchilar (buyurtma berganlar)
    cursor.execute("SELECT COUNT(DISTINCT user_id) FROM orders")
    active_users = cursor.fetchone()[0]
    
    # TOP 5 eng ko'p balansli
    cursor.execute("""
        SELECT user_id, full_name, balance 
        FROM users 
        WHERE balance > 0 
        ORDER BY balance DESC 
        LIMIT 5
    """)
    top_balance = cursor.fetchall()
    
    # TOP 5 eng ko'p buyurtma berganlar
    cursor.execute("""
        SELECT u.user_id, u.full_name, COUNT(o.id) as order_count
        FROM users u
        LEFT JOIN orders o ON u.user_id = o.user_id
        GROUP BY u.user_id
        HAVING order_count > 0
        ORDER BY order_count DESC
        LIMIT 5
    """)
    top_orders = cursor.fetchall()
    
    # Oxirgi 10 ta ro'yxatdan o'tgan
    cursor.execute("""
        SELECT user_id, full_name, created_at 
        FROM users 
        ORDER BY created_at DESC 
        LIMIT 10
    """)
    recent_users = cursor.fetchall()
    
    conn.close()
    
    # Xabar tuzish
    text = "👥 <b>FOYDALANUVCHILAR</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    text += "📊 <b>Statistika:</b>\n"
    text += f"┣ 👥 Jami: <b>{total_users:,}</b> ta\n"
    text += f"┣ 📅 Bugun: <b>+{today_users}</b>\n"
    text += f"┣ 📆 Hafta: <b>+{week_users}</b>\n"
    text += f"┣ 📆 Oy: <b>+{month_users}</b>\n"
    text += f"┣ ✅ Faol: <b>{active_users}</b> ta\n"
    text += f"┗ 💰 Jami balans: <b>{total_balance:,.0f}</b> so'm\n\n"
    
    if top_balance:
        text += "🏆 <b>TOP 5 balans:</b>\n"
        for i, (uid, name, bal) in enumerate(top_balance, 1):
            name_short = (name[:12] + "..") if name and len(name) > 14 else (name or "Nomalum")
            text += f"{i}. {name_short} - <b>{bal:,.0f}</b>\n"
        text += "\n"
    
    if top_orders:
        text += "📦 <b>TOP 5 buyurtmachi:</b>\n"
        for i, (uid, name, cnt) in enumerate(top_orders, 1):
            name_short = (name[:12] + "..") if name and len(name) > 14 else (name or "Nomalum")
            text += f"{i}. {name_short} - <b>{cnt}</b> ta\n"
        text += "\n"
    
    text += "👤 <b>Oxirgi ro'yxatdan o'tganlar:</b>\n"
    for uid, name, created in recent_users:
        name_short = (name[:15] + "..") if name and len(name) > 17 else (name or "Nomalum")
        date_str = created[:10] if created else "?"
        text += f"• <code>{uid}</code> | {name_short}\n"
    
    text += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "🔍 <b>Foydalanuvchi qidirish:</b>\n"
    text += "User ID yozing (masalan: <code>123456789</code>)"
    
    await state.set_state(AdminState.waiting_for_user_search)
    await message.answer(text, reply_markup=admin_main_menu())


@router.message(AdminState.waiting_for_user_search)
async def process_user_search(message: Message, state: FSMContext):
    """Foydalanuvchi qidirish"""
    if message.from_user.id != ADMIN_ID:
        return
    
    # Admin menyu tugmalari
    if message.text in ["📊 Statistika", "📋 Buyurtmalar", "👥 Foydalanuvchilar", "💳 To'lovlar", 
                        "📢 Xabar yuborish", "💰 Balans boshqarish", "💾 Zaxira nusxa", "⚙️ Sozlamalar", "/admin"]:
        await state.clear()
        return
    
    try:
        user_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Noto'g'ri format! Faqat raqam kiriting.")
        return
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Foydalanuvchi ma'lumotlari
    cursor.execute("""
        SELECT user_id, full_name, username, balance, created_at, referral_id, is_banned 
        FROM users 
        WHERE user_id = ?
    """, (user_id,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        await message.answer(f"❌ Foydalanuvchi <code>{user_id}</code> topilmadi!")
        return
    
    uid, name, username, balance, created, referrer, is_banned = user
    
    # Buyurtmalar statistikasi
    cursor.execute("SELECT COUNT(*), SUM(price) FROM orders WHERE user_id = ?", (user_id,))
    orders_data = cursor.fetchone()
    orders_count = orders_data[0] or 0
    orders_total = orders_data[1] or 0
    
    # To'lovlar
    cursor.execute("SELECT COUNT(*), SUM(amount) FROM payments WHERE user_id = ? AND status = 'completed'", (user_id,))
    payments_data = cursor.fetchone()
    payments_count = payments_data[0] or 0
    payments_total = payments_data[1] or 0
    
    # Referallar
    cursor.execute("SELECT COUNT(*) FROM users WHERE referral_id = ?", (user_id,))
    referrals_count = cursor.fetchone()[0]
    
    # Referal daromad
    cursor.execute("SELECT referral_earnings FROM users WHERE user_id = ?", (user_id,))
    ref_earnings = cursor.fetchone()[0] or 0
    
    # Oxirgi 5 ta buyurtma
    cursor.execute("""
        SELECT id, service_type, price, status, created_at 
        FROM orders 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT 5
    """, (user_id,))
    recent_orders = cursor.fetchall()
    
    conn.close()
    
    # Ma'lumotlarni saqlash
    await state.update_data(
        selected_user_id=user_id, 
        selected_user_name=name, 
        selected_user_balance=balance,
        selected_user_banned=is_banned
    )
    
    # Xabar tuzish
    text = f"👤 <b>FOYDALANUVCHI MA'LUMOTLARI</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    text += f"🆔 ID: <code>{uid}</code>\n"
    text += f"👤 Ism: <b>{name or 'Kiritilmagan'}</b>\n"
    text += f"📧 Username: @{username if username else 'Yoq'}\n"
    text += f"💰 Balans: <b>{balance:,.0f}</b> so'm\n"
    text += f"📅 Ro'yxatdan: {created[:10] if created else '?'}\n"
    if referrer:
        text += f"👥 Referrer: <code>{referrer}</code>\n"
    if is_banned:
        text += f"🚫 <b>BLOKLANGAN</b>\n"
    text += "\n"
    
    text += "📊 <b>Statistika:</b>\n"
    text += f"┣ 📦 Buyurtmalar: <b>{orders_count}</b> ta ({orders_total:,.0f} so'm)\n"
    text += f"┣ 💳 To'lovlar: <b>{payments_count}</b> ta ({payments_total:,.0f} so'm)\n"
    text += f"┣ 👥 Referallar: <b>{referrals_count}</b> ta\n"
    text += f"┗ 💵 Ref. daromad: <b>{ref_earnings:,.0f}</b> so'm\n\n"
    
    if recent_orders:
        text += "📦 <b>Oxirgi buyurtmalar:</b>\n"
        for oid, svc, price, status, created in recent_orders:
            st_emoji = {"pending": "⏳", "processing": "🔄", "completed": "✅", "canceled": "❌"}.get(status, "❓")
            svc_short = (svc[:18] + "..") if svc and len(svc) > 20 else (svc or "?")
            text += f"{st_emoji} #{oid} | {svc_short} | {price:,.0f}\n"
        text += "\n"
    
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "⚙️ <b>Amallar:</b>\n"
    text += "1️⃣ Balansni o'zgartirish\n"
    text += "2️⃣ Xabar yuborish\n"
    text += "3️⃣ Bloklash/Blokdan chiqarish\n"
    text += "0️⃣ Orqaga"
    
    # Amallar tugmalari (blok holatiga qarab)
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="💰 Balans o'zgartirish"),
        KeyboardButton(text="✉️ Xabar yuborish")
    )
    if is_banned:
        builder.row(
            KeyboardButton(text="✅ Blokdan chiqarish"),
            KeyboardButton(text="🔙 Orqaga")
        )
    else:
        builder.row(
            KeyboardButton(text="🚫 Bloklash"),
            KeyboardButton(text="🔙 Orqaga")
        )
    
    await state.set_state(AdminState.waiting_for_user_action)
    await message.answer(text, reply_markup=builder.as_markup(resize_keyboard=True))


@router.message(AdminState.waiting_for_user_action)
async def process_user_action(message: Message, state: FSMContext):
    """Foydalanuvchi ustida amal"""
    if message.from_user.id != ADMIN_ID:
        return
    
    data = await state.get_data()
    user_id = data.get("selected_user_id")
    user_name = data.get("selected_user_name")
    
    if message.text == "🔙 Orqaga":
        await state.clear()
        await message.answer("👥 Foydalanuvchilar bo'limiga qaytish uchun tugmani bosing.", reply_markup=admin_main_menu())
        return
    
    if message.text == "💰 Balans o'zgartirish":
        current_balance = data.get("selected_user_balance", 0)
        text = f"💰 <b>Balans o'zgartirish</b>\n\n"
        text += f"👤 Foydalanuvchi: {user_name or user_id}\n"
        text += f"🆔 ID: <code>{user_id}</code>\n"
        text += f"💵 Joriy balans: <b>{current_balance:,.0f}</b> so'm\n\n"
        text += "Yangi balans miqdorini kiriting:\n"
        text += "• <code>+5000</code> - 5000 qo'shish\n"
        text += "• <code>-3000</code> - 3000 ayirish\n"
        text += "• <code>10000</code> - 10000 ga o'rnatish"
        
        builder = ReplyKeyboardBuilder()
        builder.row(KeyboardButton(text="🔙 Bekor qilish"))
        
        await state.set_state(AdminState.waiting_for_balance_change)
        await message.answer(text, reply_markup=builder.as_markup(resize_keyboard=True))
        return
    
    if message.text == "✉️ Xabar yuborish":
        text = f"✉️ <b>Xabar yuborish</b>\n\n"
        text += f"👤 Foydalanuvchi: {user_name or user_id}\n"
        text += f"🆔 ID: <code>{user_id}</code>\n\n"
        text += "Xabar matnini yozing:"
        
        builder = ReplyKeyboardBuilder()
        builder.row(KeyboardButton(text="🔙 Bekor qilish"))
        
        await state.set_state(AdminState.waiting_for_user_message)
        await message.answer(text, reply_markup=builder.as_markup(resize_keyboard=True))
        return
    
    if message.text == "🚫 Bloklash":
        # Foydalanuvchini bloklash
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        
        await state.clear()
        await message.answer(
            f"🚫 <b>Foydalanuvchi bloklandi!</b>\n\n"
            f"👤 {user_name or 'Nomalum'}\n"
            f"🆔 ID: <code>{user_id}</code>\n\n"
            f"Endi u botdan foydalana olmaydi.",
            reply_markup=admin_main_menu()
        )
        
        # Foydalanuvchiga xabar
        try:
            await bot.send_message(
                user_id,
                "🚫 <b>Siz bloklangansiz!</b>\n\n"
                "Botdan foydalanish huquqingiz cheklandi.\n"
                "Savollar bo'lsa admin bilan bog'laning."
            )
        except:
            pass
        return
    
    if message.text == "✅ Blokdan chiqarish":
        # Foydalanuvchini blokdan chiqarish
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_banned = 0 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        
        await state.clear()
        await message.answer(
            f"✅ <b>Foydalanuvchi blokdan chiqarildi!</b>\n\n"
            f"👤 {user_name or 'Nomalum'}\n"
            f"🆔 ID: <code>{user_id}</code>\n\n"
            f"Endi u botdan foydalanishi mumkin.",
            reply_markup=admin_main_menu()
        )
        
        # Foydalanuvchiga xabar
        try:
            await bot.send_message(
                user_id,
                "✅ <b>Siz blokdan chiqarildingiz!</b>\n\n"
                "Endi botdan foydalanishingiz mumkin.\n"
                "/start buyrug'ini yuboring."
            )
        except:
            pass
        return


@router.message(AdminState.waiting_for_balance_change)
async def process_balance_change(message: Message, state: FSMContext):
    """Balansni o'zgartirish"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "🔙 Bekor qilish":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=admin_main_menu())
        return
    
    data = await state.get_data()
    user_id = data.get("selected_user_id")
    user_name = data.get("selected_user_name")
    current_balance = data.get("selected_user_balance", 0)
    
    text = message.text.strip().replace(" ", "").replace(",", "")
    
    try:
        if text.startswith("+"):
            amount = int(text[1:])
            new_balance = current_balance + amount
            action = f"+{amount:,}"
        elif text.startswith("-"):
            amount = int(text[1:])
            new_balance = max(0, current_balance - amount)
            action = f"-{amount:,}"
        else:
            new_balance = int(text)
            action = f"→ {new_balance:,}"
    except ValueError:
        await message.answer("❌ Noto'g'ri format! Raqam kiriting.")
        return
    
    # Balansni yangilash
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
    conn.commit()
    conn.close()
    
    text = f"✅ <b>Balans o'zgartirildi!</b>\n\n"
    text += f"👤 Foydalanuvchi: {user_name or user_id}\n"
    text += f"🆔 ID: <code>{user_id}</code>\n"
    text += f"💵 Eski balans: {current_balance:,.0f} so'm\n"
    text += f"📊 O'zgarish: {action} so'm\n"
    text += f"💰 Yangi balans: <b>{new_balance:,.0f}</b> so'm"
    
    await message.answer(text, reply_markup=admin_main_menu())
    
    # Foydalanuvchiga xabar
    try:
        diff = new_balance - current_balance
        if diff > 0:
            await bot.send_message(
                user_id,
                f"💰 <b>Balansingiz to'ldirildi!</b>\n\n"
                f"➕ Qo'shildi: <b>{diff:,.0f}</b> so'm\n"
                f"💵 Yangi balans: <b>{new_balance:,.0f}</b> so'm"
            )
        elif diff < 0:
            await bot.send_message(
                user_id,
                f"💰 <b>Balansingiz o'zgardi!</b>\n\n"
                f"➖ Ayirildi: <b>{abs(diff):,.0f}</b> so'm\n"
                f"💵 Yangi balans: <b>{new_balance:,.0f}</b> so'm"
            )
    except:
        pass
    
    await state.clear()


@router.message(AdminState.waiting_for_user_message)
async def process_user_message(message: Message, state: FSMContext):
    """Foydalanuvchiga xabar yuborish"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "🔙 Bekor qilish":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=admin_main_menu())
        return
    
    data = await state.get_data()
    user_id = data.get("selected_user_id")
    user_name = data.get("selected_user_name")
    
    try:
        await bot.send_message(
            user_id,
            f"📬 <b>Admin xabari:</b>\n\n{message.text}"
        )
        await message.answer(
            f"✅ <b>Xabar yuborildi!</b>\n\n"
            f"👤 Qabul qiluvchi: {user_name or user_id}\n"
            f"🆔 ID: <code>{user_id}</code>",
            reply_markup=admin_main_menu()
        )
    except Exception as e:
        await message.answer(f"❌ Xabar yuborib bo'lmadi!\n\nXatolik: {e}", reply_markup=admin_main_menu())
    
    await state.clear()


# ==================== TO'LOVLAR BO'LIMI ====================

@router.message(F.text == "💳 To'lovlar")
async def admin_payments_btn(message: Message, state: FSMContext):
    """To'lovlar bo'limi"""
    if message.from_user.id != ADMIN_ID:
        return
    
    await state.clear()
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Umumiy statistika
    cursor.execute("SELECT COUNT(*), SUM(amount) FROM payments WHERE status = 'completed'")
    completed = cursor.fetchone()
    completed_count = completed[0] or 0
    completed_sum = completed[1] or 0
    
    cursor.execute("SELECT COUNT(*), SUM(amount) FROM payments WHERE status = 'pending'")
    pending = cursor.fetchone()
    pending_count = pending[0] or 0
    pending_sum = pending[1] or 0
    
    # Bugungi
    cursor.execute("""
        SELECT COUNT(*), SUM(amount) FROM payments 
        WHERE status = 'completed' AND DATE(created_at) = DATE('now')
    """)
    today = cursor.fetchone()
    today_count = today[0] or 0
    today_sum = today[1] or 0
    
    # Haftalik
    cursor.execute("""
        SELECT COUNT(*), SUM(amount) FROM payments 
        WHERE status = 'completed' AND DATE(created_at) >= DATE('now', '-7 days')
    """)
    week = cursor.fetchone()
    week_count = week[0] or 0
    week_sum = week[1] or 0
    
    # Oylik
    cursor.execute("""
        SELECT COUNT(*), SUM(amount) FROM payments 
        WHERE status = 'completed' AND DATE(created_at) >= DATE('now', '-30 days')
    """)
    month = cursor.fetchone()
    month_count = month[0] or 0
    month_sum = month[1] or 0
    
    # Kutilayotgan to'lovlar
    cursor.execute("""
        SELECT p.id, p.user_id, u.full_name, p.amount, p.method, p.created_at
        FROM payments p
        LEFT JOIN users u ON p.user_id = u.user_id
        WHERE p.status = 'pending'
        ORDER BY p.created_at DESC
        LIMIT 10
    """)
    pending_payments = cursor.fetchall()
    
    # Oxirgi tasdiqlangan to'lovlar
    cursor.execute("""
        SELECT p.id, p.user_id, u.full_name, p.amount, p.method, p.created_at
        FROM payments p
        LEFT JOIN users u ON p.user_id = u.user_id
        WHERE p.status = 'completed'
        ORDER BY p.created_at DESC
        LIMIT 10
    """)
    recent_payments = cursor.fetchall()
    
    conn.close()
    
    # Xabar tuzish
    text = "💳 <b>TO'LOVLAR</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    text += "📊 <b>Statistika:</b>\n"
    text += f"┣ ✅ Tasdiqlangan: <b>{completed_count}</b> ta ({completed_sum:,.0f} so'm)\n"
    text += f"┣ ⏳ Kutilayotgan: <b>{pending_count}</b> ta ({pending_sum:,.0f} so'm)\n"
    text += f"┣ 📅 Bugun: <b>{today_count}</b> ta ({today_sum:,.0f} so'm)\n"
    text += f"┣ 📆 Hafta: <b>{week_count}</b> ta ({week_sum:,.0f} so'm)\n"
    text += f"┗ 📆 Oy: <b>{month_count}</b> ta ({month_sum:,.0f} so'm)\n\n"
    
    if pending_payments:
        text += "⏳ <b>Kutilayotgan to'lovlar:</b>\n"
        for pid, uid, name, amount, method, created in pending_payments:
            name_short = (name[:10] + "..") if name and len(name) > 12 else (name or "?")
            text += f"• #{pid} | {name_short} | <b>{amount:,.0f}</b> | {method or '?'}\n"
        text += "\n"
    
    if recent_payments:
        text += "✅ <b>Oxirgi to'lovlar:</b>\n"
        for pid, uid, name, amount, method, created in recent_payments[:5]:
            name_short = (name[:10] + "..") if name and len(name) > 12 else (name or "?")
            date_str = created[:10] if created else "?"
            text += f"• #{pid} | {name_short} | <b>{amount:,.0f}</b>\n"
    
    text += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "💡 Kutilayotgan to'lovlar avtomatik ko'rsatiladi"
    
    await message.answer(text, reply_markup=admin_main_menu())


# ==================== XABAR YUBORISH BO'LIMI (PROFESSIONAL) ====================

@router.message(F.text == "📢 Xabar yuborish")
async def admin_broadcast_btn(message: Message, state: FSMContext):
    """Ommaviy xabar yuborish - Professional"""
    if message.from_user.id != ADMIN_ID:
        return
    
    await state.clear()
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    conn.close()
    
    text = "📢 <b>OMMAVIY XABAR YUBORISH</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += f"👥 Jami foydalanuvchilar: <b>{total_users}</b> ta\n\n"
    text += "📝 <b>Xabar yuboring:</b>\n\n"
    text += "• 💬 Matn yozing\n"
    text += "• 📷 Rasm yuboring (caption bilan yoki bo'sh)\n"
    text += "• 🎬 Video yuboring (caption bilan yoki bo'sh)\n\n"
    text += "💡 <i>HTML formatlarni ishlatish mumkin:</i>\n"
    text += "• <code>&lt;b&gt;qalin&lt;/b&gt;</code> → <b>qalin</b>\n"
    text += "• <code>&lt;i&gt;kursiv&lt;/i&gt;</code> → <i>kursiv</i>"
    
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="🔙 Bekor qilish"))
    
    await state.set_state(AdminState.waiting_for_broadcast)
    await message.answer(text, reply_markup=builder.as_markup(resize_keyboard=True))


@router.message(AdminState.waiting_for_broadcast)
async def process_broadcast_text(message: Message, state: FSMContext):
    """Xabar matnini qabul qilish yoki mediasiz davom etish"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "🔙 Bekor qilish":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=admin_main_menu())
        return
    
    # Rasm yoki video kelsa - matnsiz xabar
    if message.photo:
        await state.update_data(
            broadcast_text=message.caption or "",
            broadcast_media=message.photo[-1].file_id,
            broadcast_media_type="photo"
        )
        # Tugma qadamiga o'tish
        await ask_for_button(message, state)
        return
    
    if message.video:
        await state.update_data(
            broadcast_text=message.caption or "",
            broadcast_media=message.video.file_id,
            broadcast_media_type="video"
        )
        # Tugma qadamiga o'tish
        await ask_for_button(message, state)
        return
    
    # Matnni saqlash
    await state.update_data(broadcast_text=message.text or "")
    
    text = "📸 <b>2-qadam:</b> Rasm yoki video qo'shing\n\n"
    text += "• 📷 Rasm yuborish\n"
    text += "• 🎬 Video yuborish\n"
    text += "• ⏭ O'tkazib yuborish (faqat matn)"
    
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="⏭ O'tkazib yuborish"))
    builder.row(KeyboardButton(text="🔙 Bekor qilish"))
    
    await state.set_state(AdminState.waiting_for_broadcast_media)
    await message.answer(text, reply_markup=builder.as_markup(resize_keyboard=True))


async def ask_for_button(message: Message, state: FSMContext):
    """Tugma so'rash - umumiy funksiya"""
    text = "🔗 <b>Tugma qo'shing</b>\n\n"
    text += "Tugma formatida yozing:\n"
    text += "<code>Tugma matni | https://link.com</code>\n\n"
    text += "Bir nechta tugma (har biri yangi qatorda):\n"
    text += "<code>Tugma 1 | https://link1.com\n"
    text += "Tugma 2 | https://link2.com</code>\n\n"
    text += "• ⏭ O'tkazib yuborish (tugmasiz)"
    
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="⏭ O'tkazib yuborish"))
    builder.row(KeyboardButton(text="🔙 Bekor qilish"))
    
    await state.set_state(AdminState.waiting_for_broadcast_button)
    await message.answer(text, reply_markup=builder.as_markup(resize_keyboard=True))


@router.message(AdminState.waiting_for_broadcast_media)
async def process_broadcast_media(message: Message, state: FSMContext):
    """Media qabul qilish"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "🔙 Bekor qilish":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=admin_main_menu())
        return
    
    if message.text == "⏭ O'tkazib yuborish":
        await state.update_data(broadcast_media=None, broadcast_media_type=None)
    elif message.photo:
        # Rasm
        await state.update_data(
            broadcast_media=message.photo[-1].file_id,
            broadcast_media_type="photo"
        )
    elif message.video:
        # Video
        await state.update_data(
            broadcast_media=message.video.file_id,
            broadcast_media_type="video"
        )
    else:
        await message.answer("❌ Faqat rasm yoki video yuborishingiz mumkin!")
        return
    
    text = "🔗 <b>3-qadam:</b> Tugma qo'shing\n\n"
    text += "Tugma formatida yozing:\n"
    text += "<code>Tugma matni | https://link.com</code>\n\n"
    text += "Bir nechta tugma (har biri yangi qatorda):\n"
    text += "<code>Tugma 1 | https://link1.com\n"
    text += "Tugma 2 | https://link2.com</code>\n\n"
    text += "• ⏭ O'tkazib yuborish (tugmasiz)"
    
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="⏭ O'tkazib yuborish"))
    builder.row(KeyboardButton(text="🔙 Bekor qilish"))
    
    await state.set_state(AdminState.waiting_for_broadcast_button)
    await message.answer(text, reply_markup=builder.as_markup(resize_keyboard=True))


@router.message(AdminState.waiting_for_broadcast_button)
async def process_broadcast_button(message: Message, state: FSMContext):
    """Tugma qabul qilish"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "🔙 Bekor qilish":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=admin_main_menu())
        return
    
    buttons = []
    if message.text != "⏭ O'tkazib yuborish":
        # Tugmalarni parse qilish
        lines = message.text.strip().split("\n")
        for line in lines:
            if "|" in line:
                parts = line.split("|", 1)
                if len(parts) == 2:
                    btn_text = parts[0].strip()
                    btn_url = parts[1].strip()
                    if btn_text and btn_url.startswith("http"):
                        buttons.append({"text": btn_text, "url": btn_url})
    
    await state.update_data(broadcast_buttons=buttons)
    
    # Preview ko'rsatish
    data = await state.get_data()
    broadcast_text = data.get("broadcast_text", "")
    media_type = data.get("broadcast_media_type")
    media = data.get("broadcast_media")
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    conn.close()
    
    # Inline tugmalar
    inline_kb = None
    if buttons:
        inline_builder = InlineKeyboardBuilder()
        for btn in buttons:
            inline_builder.row(InlineKeyboardButton(text=btn["text"], url=btn["url"]))
        inline_kb = inline_builder.as_markup()
    
    # Preview xabari
    preview_text = "📢 <b>Xabar ko'rinishi:</b>\n"
    preview_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    await message.answer(preview_text)
    
    # Xabarni yuborish (preview)
    try:
        if media_type == "photo":
            await message.answer_photo(media, caption=broadcast_text, reply_markup=inline_kb)
        elif media_type == "video":
            await message.answer_video(media, caption=broadcast_text, reply_markup=inline_kb)
        else:
            await message.answer(broadcast_text, reply_markup=inline_kb)
    except Exception as e:
        await message.answer(f"⚠️ Xatolik: {e}")
    
    text = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    text += f"👥 Yuboriladi: <b>{total_users}</b> ta foydalanuvchiga\n\n"
    text += "✅ <b>Ha</b> - Yuborish\n"
    text += "❌ <b>Yo'q</b> - Bekor qilish"
    
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="✅ Ha, yuborish"),
        KeyboardButton(text="❌ Yo'q")
    )
    
    await state.set_state(AdminState.waiting_for_broadcast_confirm)
    await message.answer(text, reply_markup=builder.as_markup(resize_keyboard=True))


@router.message(AdminState.waiting_for_broadcast_confirm)
async def process_broadcast_confirm(message: Message, state: FSMContext):
    """Xabar yuborishni tasdiqlash"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "❌ Yo'q":
        await state.clear()
        await message.answer("❌ Xabar yuborish bekor qilindi.", reply_markup=admin_main_menu())
        return
    
    if message.text != "✅ Ha, yuborish":
        await message.answer("❌ Noto'g'ri tanlov!")
        return
    
    data = await state.get_data()
    broadcast_text = data.get("broadcast_text", "")
    media_type = data.get("broadcast_media_type")
    media = data.get("broadcast_media")
    buttons = data.get("broadcast_buttons", [])
    
    # Inline tugmalar
    inline_kb = None
    if buttons:
        inline_builder = InlineKeyboardBuilder()
        for btn in buttons:
            inline_builder.row(InlineKeyboardButton(text=btn["text"], url=btn["url"]))
        inline_kb = inline_builder.as_markup()
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    conn.close()
    
    await state.clear()
    
    # Yuborish boshlandi
    status_msg = await message.answer("📤 Xabar yuborilmoqda...", reply_markup=admin_main_menu())
    
    success = 0
    failed = 0
    
    for (user_id,) in users:
        try:
            if media_type == "photo":
                await bot.send_photo(user_id, media, caption=broadcast_text, reply_markup=inline_kb)
            elif media_type == "video":
                await bot.send_video(user_id, media, caption=broadcast_text, reply_markup=inline_kb)
            else:
                await bot.send_message(user_id, broadcast_text, reply_markup=inline_kb)
            success += 1
        except:
            failed += 1
        
        # Har 20 ta xabardan keyin kuting (flood limitdan qochish)
        if (success + failed) % 20 == 0:
            await asyncio.sleep(1)
    
    # Natija
    await status_msg.edit_text(
        f"✅ <b>Xabar yuborildi!</b>\n\n"
        f"📤 Yuborildi: <b>{success}</b> ta\n"
        f"❌ Xatolik: <b>{failed}</b> ta\n"
        f"📊 Jami: <b>{success + failed}</b> ta"
    )


# ==================== ZAXIRA NUSXA BO'LIMI ====================

# Avtomatik zaxira uchun global o'zgaruvchi
auto_backup_enabled = False
auto_backup_task = None

@router.message(F.text == "💾 Zaxira nusxa")
async def admin_backup_btn(message: Message, state: FSMContext):
    """Zaxira nusxa menyusi"""
    if message.from_user.id != ADMIN_ID:
        return
    
    await state.clear()
    
    # Statistika
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM payments")
    total_payments = cursor.fetchone()[0]
    
    conn.close()
    
    global auto_backup_enabled
    
    text = "💾 <b>ZAXIRA NUSXA</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += "📊 <b>Ma'lumotlar bazasi:</b>\n"
    text += f"┣ 👥 Foydalanuvchilar: <b>{total_users}</b>\n"
    text += f"┣ 📦 Buyurtmalar: <b>{total_orders}</b>\n"
    text += f"┗ 💳 To'lovlar: <b>{total_payments}</b>\n\n"
    
    status = "🟢 Yoqilgan" if auto_backup_enabled else "🔴 O'chirilgan"
    text += f"⏰ <b>Avtomatik zaxira:</b> {status}\n"
    text += "<i>Har kuni soat 03:00 da avtomatik zaxira olinadi</i>\n\n"
    text += "📤 <b>Tiklash:</b> Zaxira faylni (.db) shu chatga yuboring"
    
    # Inline tugmalar
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Zaxira olish", callback_data="backup_create")],
        [
            InlineKeyboardButton(
                text="⏰ Avto-zaxira: 🟢" if auto_backup_enabled else "⏰ Avto-zaxira: 🔴", 
                callback_data="backup_auto_toggle"
            )
        ],
        [InlineKeyboardButton(text="📤 Zaxiradan tiklash", callback_data="backup_restore")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_back_main")]
    ])
    
    await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data == "backup_create")
async def backup_create_callback(callback: CallbackQuery):
    """Zaxira yaratish"""
    if callback.from_user.id != ADMIN_ID:
        return
    
    await callback.answer("⏳ Zaxira yaratilmoqda...")
    
    import shutil
    from datetime import datetime
    
    try:
        # Statistika
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders")
        total_orders = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM payments")
        total_payments = cursor.fetchone()[0]
        
        conn.close()
        
        # Zaxira nusxa yaratish
        backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy(DATABASE_NAME, backup_name)
        
        # Faylni yuborish
        from aiogram.types import FSInputFile
        backup_file = FSInputFile(backup_name)
        
        await callback.message.answer_document(
            backup_file,
            caption=f"💾 <b>Zaxira nusxa tayyor!</b>\n\n"
                    f"📅 Sana: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"👥 Foydalanuvchilar: {total_users}\n"
                    f"📦 Buyurtmalar: {total_orders}\n"
                    f"💳 To'lovlar: {total_payments}\n\n"
                    f"💡 <i>Bu faylni tiklash uchun botga yuboring</i>"
        )
        
        # Vaqtinchalik faylni o'chirish
        import os
        os.remove(backup_name)
        
    except Exception as e:
        await callback.message.answer(f"❌ Xatolik: {e}")


@router.callback_query(F.data == "backup_auto_toggle")
async def backup_auto_toggle_callback(callback: CallbackQuery):
    """Avtomatik zaxirani yoqish/o'chirish"""
    if callback.from_user.id != ADMIN_ID:
        return
    
    global auto_backup_enabled, auto_backup_task
    
    auto_backup_enabled = not auto_backup_enabled
    
    if auto_backup_enabled:
        # Avtomatik zaxira taskni boshlash
        await callback.answer("✅ Avtomatik zaxira yoqildi!")
    else:
        await callback.answer("🔴 Avtomatik zaxira o'chirildi!")
    
    # Tugmani yangilash
    status = "🟢 Yoqilgan" if auto_backup_enabled else "🔴 O'chirilgan"
    
    # Statistika
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM payments")
    total_payments = cursor.fetchone()[0]
    
    conn.close()
    
    text = "💾 <b>ZAXIRA NUSXA</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += "📊 <b>Ma'lumotlar bazasi:</b>\n"
    text += f"┣ 👥 Foydalanuvchilar: <b>{total_users}</b>\n"
    text += f"┣ 📦 Buyurtmalar: <b>{total_orders}</b>\n"
    text += f"┗ 💳 To'lovlar: <b>{total_payments}</b>\n\n"
    text += f"⏰ <b>Avtomatik zaxira:</b> {status}\n"
    text += "<i>Har kuni soat 03:00 da avtomatik zaxira olinadi</i>\n\n"
    text += "📤 <b>Tiklash:</b> Zaxira faylni (.db) shu chatga yuboring"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Zaxira olish", callback_data="backup_create")],
        [
            InlineKeyboardButton(
                text="⏰ Avto-zaxira: 🟢" if auto_backup_enabled else "⏰ Avto-zaxira: 🔴", 
                callback_data="backup_auto_toggle"
            )
        ],
        [InlineKeyboardButton(text="📤 Zaxiradan tiklash", callback_data="backup_restore")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_back_main")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)


@router.callback_query(F.data == "backup_restore")
async def backup_restore_callback(callback: CallbackQuery, state: FSMContext):
    """Zaxiradan tiklash - fayl so'rash"""
    if callback.from_user.id != ADMIN_ID:
        return
    
    await callback.answer()
    
    text = "📤 <b>ZAXIRADAN TIKLASH</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += "⚠️ <b>DIQQAT!</b>\n"
    text += "Tiklash jarayonida hozirgi barcha ma'lumotlar\n"
    text += "zaxira nusxadagi ma'lumotlar bilan almashtiriladi!\n\n"
    text += "📁 Zaxira faylini (.db) yuboring:\n"
    text += "<i>Faylni shu chatga document sifatida yuboring</i>"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="backup_cancel")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await state.set_state(AdminState.waiting_for_restore_file)


@router.callback_query(F.data == "backup_cancel")
async def backup_cancel_callback(callback: CallbackQuery, state: FSMContext):
    """Zaxira amalni bekor qilish"""
    if callback.from_user.id != ADMIN_ID:
        return
    
    await state.clear()
    await callback.answer("❌ Bekor qilindi")
    await callback.message.delete()


@router.message(AdminState.waiting_for_restore_file, F.document)
async def admin_restore_file_received(message: Message, state: FSMContext):
    """Zaxira fayl qabul qilish"""
    if message.from_user.id != ADMIN_ID:
        return
    
    document = message.document
    
    # Fayl nomini tekshirish
    if not document.file_name.endswith('.db'):
        await message.answer(
            "❌ <b>Noto'g'ri fayl formati!</b>\n\n"
            "Faqat .db formatidagi fayllar qabul qilinadi.\n"
            "Iltimos, to'g'ri zaxira faylini yuboring."
        )
        return
    
    # Fayl hajmini tekshirish (100MB dan kichik bo'lishi kerak)
    if document.file_size > 100 * 1024 * 1024:
        await message.answer("❌ Fayl juda katta! Maksimum 100MB")
        return
    
    # Faylni saqlash
    await state.update_data(restore_file_id=document.file_id, restore_file_name=document.file_name)
    
    text = "⚠️ <b>TASDIQLASH</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += f"📁 <b>Fayl:</b> {document.file_name}\n"
    text += f"📊 <b>Hajmi:</b> {document.file_size / 1024:.1f} KB\n\n"
    text += "⚠️ <b>OGOHLANTIRISH!</b>\n"
    text += "Bu amal hozirgi barcha ma'lumotlarni o'chirib,\n"
    text += "zaxira nusxadagi ma'lumotlarni tiklaydi!\n\n"
    text += "❓ <b>Davom etishni xohlaysizmi?</b>"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha, tiklash", callback_data="restore_confirm"),
            InlineKeyboardButton(text="❌ Yo'q, bekor", callback_data="restore_cancel")
        ]
    ])
    
    await message.answer(text, reply_markup=keyboard)
    await state.set_state(AdminState.waiting_for_restore_confirm)


@router.callback_query(F.data == "restore_confirm", AdminState.waiting_for_restore_confirm)
async def restore_confirm_callback(callback: CallbackQuery, state: FSMContext):
    """Tiklashni tasdiqlash"""
    if callback.from_user.id != ADMIN_ID:
        return
    
    data = await state.get_data()
    file_id = data.get('restore_file_id')
    file_name = data.get('restore_file_name')
    
    if not file_id:
        await callback.answer("❌ Fayl topilmadi!")
        await state.clear()
        return
    
    await callback.answer("⏳ Tiklanmoqda...")
    
    import shutil
    from datetime import datetime
    import os
    
    try:
        # Avval joriy bazani zaxira qilish (xavfsizlik uchun)
        backup_before = f"backup_before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy(DATABASE_NAME, backup_before)
        
        # Yuborilgan faylni yuklab olish
        file = await callback.bot.get_file(file_id)
        temp_file = f"temp_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        await callback.bot.download_file(file.file_path, temp_file)
        
        # Bazani tekshirish
        try:
            test_conn = sqlite3.connect(temp_file)
            test_cursor = test_conn.cursor()
            test_cursor.execute("SELECT COUNT(*) FROM users")
            new_users = test_cursor.fetchone()[0]
            test_cursor.execute("SELECT COUNT(*) FROM orders")
            new_orders = test_cursor.fetchone()[0]
            test_cursor.execute("SELECT COUNT(*) FROM payments")
            new_payments = test_cursor.fetchone()[0]
            test_conn.close()
        except Exception as e:
            os.remove(temp_file)
            await callback.message.edit_text(f"❌ <b>Noto'g'ri baza formati!</b>\n\nXatolik: {e}")
            await state.clear()
            return
        
        # Joriy bazani yopish va yangilash
        shutil.copy(temp_file, DATABASE_NAME)
        
        # Vaqtinchalik faylni o'chirish
        os.remove(temp_file)
        
        text = "✅ <b>MUVAFFAQIYATLI TIKLANDI!</b>\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        text += f"📁 <b>Fayl:</b> {file_name}\n"
        text += f"📅 <b>Sana:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        text += "📊 <b>Tiklangan ma'lumotlar:</b>\n"
        text += f"┣ 👥 Foydalanuvchilar: <b>{new_users}</b>\n"
        text += f"┣ 📦 Buyurtmalar: <b>{new_orders}</b>\n"
        text += f"┗ 💳 To'lovlar: <b>{new_payments}</b>\n\n"
        text += f"💾 <i>Oldingi baza saqlandi: {backup_before}</i>"
        
        await callback.message.edit_text(text)
        
        # Oldingi bazani ham yuborish
        from aiogram.types import FSInputFile
        backup_file = FSInputFile(backup_before)
        await callback.message.answer_document(
            backup_file,
            caption="💾 <b>Tiklashdan oldingi baza</b>\n"
                    "<i>Xatolik yuz bersa, bu fayldan tiklashingiz mumkin</i>"
        )
        
    except Exception as e:
        await callback.message.edit_text(f"❌ <b>Xatolik yuz berdi!</b>\n\n{e}")
    
    await state.clear()


@router.callback_query(F.data == "restore_cancel")
async def restore_cancel_callback(callback: CallbackQuery, state: FSMContext):
    """Tiklashni bekor qilish"""
    if callback.from_user.id != ADMIN_ID:
        return
    
    await state.clear()
    await callback.answer("❌ Tiklash bekor qilindi")
    await callback.message.edit_text("❌ <b>Tiklash bekor qilindi</b>")


# Avtomatik zaxira funksiyasi
async def auto_backup_job(bot):
    """Avtomatik zaxira yaratish (har kuni)"""
    global auto_backup_enabled
    
    if not auto_backup_enabled:
        return
    
    import shutil
    from datetime import datetime
    
    try:
        # Statistika
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders")
        total_orders = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM payments")
        total_payments = cursor.fetchone()[0]
        
        conn.close()
        
        # Zaxira nusxa yaratish
        backup_name = f"auto_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy(DATABASE_NAME, backup_name)
        
        # Faylni yuborish
        from aiogram.types import FSInputFile
        backup_file = FSInputFile(backup_name)
        
        await bot.send_document(
            chat_id=ADMIN_ID,
            document=backup_file,
            caption=f"🔄 <b>Avtomatik zaxira nusxa</b>\n\n"
                    f"📅 Sana: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"👥 Foydalanuvchilar: {total_users}\n"
                    f"📦 Buyurtmalar: {total_orders}\n"
                    f"💳 To'lovlar: {total_payments}\n\n"
                    f"💡 <i>Tiklash uchun bu faylni botga yuboring</i>"
        )
        
        # Vaqtinchalik faylni o'chirish
        import os
        os.remove(backup_name)
        
    except Exception as e:
        try:
            await bot.send_message(ADMIN_ID, f"❌ Avtomatik zaxira xatolik: {e}")
        except:
            pass


# Admin chatiga yuborilgan document fayllarni tekshirish
@router.message(F.document, lambda m: m.from_user.id == ADMIN_ID)
async def admin_document_received(message: Message, state: FSMContext):
    """Admin yuborgan document faylni tekshirish"""
    # Agar state bo'lmasa va .db fayl bo'lsa
    current_state = await state.get_state()
    
    if current_state is None and message.document.file_name.endswith('.db'):
        # Tiklash so'rovi
        await state.update_data(
            restore_file_id=message.document.file_id, 
            restore_file_name=message.document.file_name
        )
        
        document = message.document
        
        text = "⚠️ <b>ZAXIRADAN TIKLASH</b>\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        text += f"📁 <b>Fayl:</b> {document.file_name}\n"
        text += f"📊 <b>Hajmi:</b> {document.file_size / 1024:.1f} KB\n\n"
        text += "⚠️ <b>OGOHLANTIRISH!</b>\n"
        text += "Bu amal hozirgi barcha ma'lumotlarni o'chirib,\n"
        text += "zaxira nusxadagi ma'lumotlarni tiklaydi!\n\n"
        text += "❓ <b>Davom etishni xohlaysizmi?</b>"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Ha, tiklash", callback_data="restore_confirm"),
                InlineKeyboardButton(text="❌ Yo'q, bekor", callback_data="restore_cancel")
            ]
        ])
        
        await message.answer(text, reply_markup=keyboard)
        await state.set_state(AdminState.waiting_for_restore_confirm)


@router.callback_query(F.data == "admin_back_main")
async def admin_back_main_callback(callback: CallbackQuery, state: FSMContext):
    """Admin menyuga qaytish"""
    if callback.from_user.id != ADMIN_ID:
        return
    
    await state.clear()
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer("🔙 Bosh menyu", reply_markup=admin_main_menu())


# ==================== BALANS BOSHQARISH BO'LIMI ====================

@router.message(F.text == "💰 Balans boshqarish")
async def admin_balance_manage_btn(message: Message, state: FSMContext):
    """Balans boshqarish"""
    if message.from_user.id != ADMIN_ID:
        return
    
    await state.clear()
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*), SUM(balance) FROM users")
    stats = cursor.fetchone()
    total_users = stats[0] or 0
    total_balance = stats[1] or 0
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE balance > 0")
    users_with_balance = cursor.fetchone()[0]
    
    cursor.execute("SELECT AVG(balance) FROM users WHERE balance > 0")
    avg_balance = cursor.fetchone()[0] or 0
    
    conn.close()
    
    text = "💰 <b>BALANS BOSHQARISH</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    text += "📊 <b>Umumiy ma'lumot:</b>\n"
    text += f"┣ 👥 Jami foydalanuvchilar: <b>{total_users}</b>\n"
    text += f"┣ 💵 Jami balans: <b>{total_balance:,.0f}</b> so'm\n"
    text += f"┣ 👤 Balansli foydalanuvchilar: <b>{users_with_balance}</b>\n"
    text += f"┗ 📊 O'rtacha balans: <b>{avg_balance:,.0f}</b> so'm\n\n"
    
    text += "⚙️ <b>Amallar:</b>\n"
    text += "1️⃣ Hammaga balans qo'shish\n"
    text += "2️⃣ Hammaning balansini tozalash\n"
    text += "3️⃣ User ID orqali balans o'zgartirish"
    
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="➕ Hammaga qo'shish"),
        KeyboardButton(text="🗑 Hammasini tozalash")
    )
    builder.row(
        KeyboardButton(text="👤 User ID orqali"),
        KeyboardButton(text="🔙 Orqaga")
    )
    
    await state.set_state(AdminState.waiting_for_global_balance)
    await message.answer(text, reply_markup=builder.as_markup(resize_keyboard=True))


@router.message(AdminState.waiting_for_global_balance)
async def process_global_balance(message: Message, state: FSMContext):
    """Global balans amalini tanlash"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "🔙 Orqaga":
        await state.clear()
        await message.answer("Admin panel", reply_markup=admin_main_menu())
        return
    
    if message.text == "👤 User ID orqali":
        await state.clear()
        text = "🔍 <b>Foydalanuvchi qidirish</b>\n\n"
        text += "User ID yozing:"
        await state.set_state(AdminState.waiting_for_user_search)
        await message.answer(text, reply_markup=admin_main_menu())
        return
    
    if message.text == "➕ Hammaga qo'shish":
        await state.update_data(balance_action="add_all")
        text = "➕ <b>Hammaga balans qo'shish</b>\n\n"
        text += "Qo'shiladigan miqdorni kiriting (so'm):"
        
        builder = ReplyKeyboardBuilder()
        builder.row(KeyboardButton(text="🔙 Bekor qilish"))
        
        await state.set_state(AdminState.waiting_for_global_balance_amount)
        await message.answer(text, reply_markup=builder.as_markup(resize_keyboard=True))
        return
    
    if message.text == "🗑 Hammasini tozalash":
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*), SUM(balance) FROM users WHERE balance > 0")
        stats = cursor.fetchone()
        count = stats[0] or 0
        total = stats[1] or 0
        conn.close()
        
        text = "⚠️ <b>Diqqat!</b>\n\n"
        text += f"👥 <b>{count}</b> ta foydalanuvchining\n"
        text += f"💰 <b>{total:,.0f}</b> so'm balansi tozalanadi!\n\n"
        text += "Tasdiqlash uchun <code>TOZALASH</code> yozing:"
        
        await state.update_data(balance_action="clear_all")
        
        builder = ReplyKeyboardBuilder()
        builder.row(KeyboardButton(text="🔙 Bekor qilish"))
        
        await state.set_state(AdminState.waiting_for_global_balance_amount)
        await message.answer(text, reply_markup=builder.as_markup(resize_keyboard=True))
        return


@router.message(AdminState.waiting_for_global_balance_amount)
async def process_global_balance_amount(message: Message, state: FSMContext):
    """Global balans miqdorini kiritish"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "🔙 Bekor qilish":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=admin_main_menu())
        return
    
    data = await state.get_data()
    action = data.get("balance_action")
    
    if action == "add_all":
        try:
            amount = int(message.text.strip().replace(",", "").replace(" ", ""))
        except ValueError:
            await message.answer("❌ Noto'g'ri format! Faqat raqam kiriting.")
            return
        
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET balance = balance + ?", (amount,))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        await state.clear()
        await message.answer(
            f"✅ <b>Balans qo'shildi!</b>\n\n"
            f"👥 Foydalanuvchilar: <b>{affected}</b> ta\n"
            f"💰 Qo'shildi: <b>+{amount:,}</b> so'm",
            reply_markup=admin_main_menu()
        )
        return
    
    if action == "clear_all":
        if message.text.strip() != "TOZALASH":
            await message.answer("❌ Tasdiqlash uchun <code>TOZALASH</code> yozing!")
            return
        
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET balance = 0")
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        await state.clear()
        await message.answer(
            f"✅ <b>Balanslar tozalandi!</b>\n\n"
            f"👥 Foydalanuvchilar: <b>{affected}</b> ta",
            reply_markup=admin_main_menu()
        )
        return


# ==================== SOZLAMALAR BO'LIMI ====================

from database import get_setting, set_setting, get_all_settings

@router.message(F.text == "⚙️ Sozlamalar")
async def admin_settings_btn(message: Message, state: FSMContext):
    """Sozlamalar menyusi"""
    if message.from_user.id != ADMIN_ID:
        return
    
    await state.clear()
    await show_settings_menu(message)


async def show_settings_menu(message: Message, edit: bool = False):
    """Sozlamalar menyusini ko'rsatish"""
    settings = get_all_settings()
    
    usd_rate = settings.get('usd_rate', '12900')
    rub_rate = settings.get('rub_rate', '140')
    markup = settings.get('markup_percent', '20')
    min_deposit = settings.get('min_deposit', '5000')
    ref_bonus = settings.get('referral_bonus', '500')
    
    # Karta ma'lumotlarini config.py dan olish (agar settings da bo'lmasa)
    card = settings.get('card_number', '')
    card_holder = settings.get('card_holder', '')
    
    if not card or card == '9860 **** **** ****':
        try:
            from config import PAYMENT_CARDS
            # Birinchi kartani olish
            first_card = list(PAYMENT_CARDS.values())[0]
            card = first_card.get('card', '9860 **** **** ****')
            card_holder = first_card.get('name', 'ADMIN')
        except:
            card = '9860 **** **** ****'
            card_holder = 'ADMIN'
    
    text = "⚙️ <b>SOZLAMALAR</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    text += "💱 <b>Valyuta kurslari:</b>\n"
    text += f"┣ 🇺🇸 USD: <b>{int(usd_rate):,}</b> so'm\n"
    text += f"┗ 🇷🇺 RUB: <b>{int(rub_rate):,}</b> so'm\n\n"
    
    text += "💰 <b>Narxlash:</b>\n"
    text += f"┣ 📈 Ustama foiz: <b>{markup}%</b> (bizning foyda)\n"
    text += f"┗ 💵 Min. to'lov: <b>{int(min_deposit):,}</b> so'm\n\n"
    
    text += "💳 <b>To'lov:</b>\n"
    # Karta raqamni to'liq ko'rsatish
    text += f"┣ 💳 Karta: <code>{card}</code>\n"
    text += f"┗ 👤 Egasi: <b>{card_holder}</b>\n\n"
    
    text += "🎁 <b>Referal:</b>\n"
    text += f"┗ 💰 Bonus: <b>{int(ref_bonus):,}</b> so'm\n\n"
    
    text += "🤖 <b>Bot:</b>\n"
    text += f"┣ Admin ID: <code>{ADMIN_ID}</code>\n"
    text += f"┗ Database: smm_bot.db"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇸 USD kurs", callback_data="settings_usd"),
            InlineKeyboardButton(text="🇷🇺 RUB kurs", callback_data="settings_rub")
        ],
        [
            InlineKeyboardButton(text="📈 Ustama %", callback_data="settings_markup"),
            InlineKeyboardButton(text="💵 Min. to'lov", callback_data="settings_min_deposit")
        ],
        [
            InlineKeyboardButton(text="💳 Karta raqam", callback_data="settings_card"),
            InlineKeyboardButton(text="👤 Karta egasi", callback_data="settings_card_holder")
        ],
        [
            InlineKeyboardButton(text="🎁 Referal bonus", callback_data="settings_ref_bonus"),
            InlineKeyboardButton(text="👑 Admin", callback_data="settings_admin")
        ],
        [InlineKeyboardButton(text="📊 API balans", callback_data="settings_api_balance")],
        [InlineKeyboardButton(text="📸 Botni qayta ishga tushirish", callback_data="settings_restart_bot")],
        [InlineKeyboardButton(text="📸🔙 Orqaga", callback_data="admin_back_main")]
    ])
    
    if edit:
        await message.edit_text(text, reply_markup=keyboard)
    else:
        await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data == "settings_usd")
async def settings_usd_callback(callback: CallbackQuery, state: FSMContext):
    """USD kursini o'zgartirish"""
    if callback.from_user.id != ADMIN_ID:
        return
    
    current = get_setting('usd_rate', '12900')
    
    text = "🇺🇸 <b>DOLLAR KURSI</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += f"📊 Joriy kurs: <b>{int(current):,}</b> so'm\n\n"
    text += "💵 Yangi kursni kiriting:\n"
    text += "<i>Masalan: 12900</i>"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="settings_cancel")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await state.set_state(AdminState.waiting_for_usd_rate)


@router.message(AdminState.waiting_for_usd_rate)
async def process_usd_rate(message: Message, state: FSMContext):
    """USD kursini saqlash"""
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        new_rate = int(message.text.strip().replace(",", "").replace(" ", ""))
        if new_rate < 1000 or new_rate > 50000:
            await message.answer("❌ Kurs 1,000 - 50,000 oralig'ida bo'lishi kerak!")
            return
        
        set_setting('usd_rate', str(new_rate))
        await state.clear()
        await message.answer(f"✅ USD kursi o'zgartirildi: <b>{new_rate:,}</b> so'm")
        await show_settings_menu(message)
        
    except ValueError:
        await message.answer("❌ Noto'g'ri format! Faqat raqam kiriting.")


@router.callback_query(F.data == "settings_rub")
async def settings_rub_callback(callback: CallbackQuery, state: FSMContext):
    """RUB kursini o'zgartirish"""
    if callback.from_user.id != ADMIN_ID:
        return
    
    current = get_setting('rub_rate', '140')
    
    text = "🇷🇺 <b>RUBL KURSI</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += f"📊 Joriy kurs: <b>{int(current):,}</b> so'm\n\n"
    text += "💵 Yangi kursni kiriting:\n"
    text += "<i>Masalan: 140</i>"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="settings_cancel")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await state.set_state(AdminState.waiting_for_rub_rate)


@router.message(AdminState.waiting_for_rub_rate)
async def process_rub_rate(message: Message, state: FSMContext):
    """RUB kursini saqlash"""
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        new_rate = int(message.text.strip().replace(",", "").replace(" ", ""))
        if new_rate < 50 or new_rate > 500:
            await message.answer("❌ Kurs 50 - 500 oralig'ida bo'lishi kerak!")
            return
        
        set_setting('rub_rate', str(new_rate))
        await state.clear()
        await message.answer(f"✅ RUB kursi o'zgartirildi: <b>{new_rate:,}</b> so'm")
        await show_settings_menu(message)
        
    except ValueError:
        await message.answer("❌ Noto'g'ri format! Faqat raqam kiriting.")


@router.callback_query(F.data == "settings_markup")
async def settings_markup_callback(callback: CallbackQuery, state: FSMContext):
    """Ustama foizni o'zgartirish"""
    if callback.from_user.id != ADMIN_ID:
        return
    
    current = get_setting('markup_percent', '20')
    
    text = "📈 <b>USTAMA FOIZ (FOYDA)</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += f"📊 Joriy ustama: <b>{current}%</b>\n\n"
    text += "💡 <b>Qanday ishlaydi:</b>\n"
    text += "API narxi × (1 + ustama%) = Sotish narxi\n\n"
    text += "📌 <b>Misol:</b>\n"
    text += f"API: 10,000 so'm × {int(current)+100}% = "
    text += f"<b>{10000 * (100 + int(current)) // 100:,}</b> so'm\n\n"
    text += "💵 Yangi foizni kiriting (0-100):\n"
    text += "<i>Masalan: 25</i>"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="settings_cancel")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await state.set_state(AdminState.waiting_for_markup)


@router.message(AdminState.waiting_for_markup)
async def process_markup(message: Message, state: FSMContext):
    """Ustama foizni saqlash"""
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        new_markup = int(message.text.strip().replace("%", ""))
        if new_markup < 0 or new_markup > 100:
            await message.answer("❌ Foiz 0 - 100 oralig'ida bo'lishi kerak!")
            return
        
        set_setting('markup_percent', str(new_markup))
        await state.clear()
        await message.answer(f"✅ Ustama foiz o'zgartirildi: <b>{new_markup}%</b>")
        await show_settings_menu(message)
        
    except ValueError:
        await message.answer("❌ Noto'g'ri format! Faqat raqam kiriting.")


@router.callback_query(F.data == "settings_min_deposit")
async def settings_min_deposit_callback(callback: CallbackQuery, state: FSMContext):
    """Minimal to'lovni o'zgartirish"""
    if callback.from_user.id != ADMIN_ID:
        return
    
    current = get_setting('min_deposit', '5000')
    
    text = "💵 <b>MINIMAL TO'LOV</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += f"📊 Joriy minimal: <b>{int(current):,}</b> so'm\n\n"
    text += "💵 Yangi minimal miqdorni kiriting:\n"
    text += "<i>Masalan: 10000</i>"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="settings_cancel")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await state.set_state(AdminState.waiting_for_min_deposit)


@router.message(AdminState.waiting_for_min_deposit)
async def process_min_deposit(message: Message, state: FSMContext):
    """Minimal to'lovni saqlash"""
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        new_min = int(message.text.strip().replace(",", "").replace(" ", ""))
        if new_min < 1000 or new_min > 1000000:
            await message.answer("❌ Miqdor 1,000 - 1,000,000 oralig'ida bo'lishi kerak!")
            return
        
        set_setting('min_deposit', str(new_min))
        await state.clear()
        await message.answer(f"✅ Minimal to'lov o'zgartirildi: <b>{new_min:,}</b> so'm")
        await show_settings_menu(message)
        
    except ValueError:
        await message.answer("❌ Noto'g'ri format! Faqat raqam kiriting.")


@router.callback_query(F.data == "settings_card")
async def settings_card_callback(callback: CallbackQuery, state: FSMContext):
    """Karta raqamni o'zgartirish"""
    if callback.from_user.id != ADMIN_ID:
        return
    
    current = get_setting('card_number', '9860 **** **** ****')
    
    text = "💳 <b>KARTA RAQAM</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += f"📊 Joriy karta: <code>{current}</code>\n\n"
    text += "💳 Yangi karta raqamini kiriting:\n"
    text += "<i>Masalan: 9860 1234 5678 9012</i>"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="settings_cancel")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await state.set_state(AdminState.waiting_for_card_number)


@router.message(AdminState.waiting_for_card_number)
async def process_card_number(message: Message, state: FSMContext):
    """Karta raqamni saqlash"""
    if message.from_user.id != ADMIN_ID:
        return
    
    card = message.text.strip().replace("-", " ")
    # Raqamlarni tekshirish
    digits_only = card.replace(" ", "")
    
    if not digits_only.isdigit() or len(digits_only) != 16:
        await message.answer("❌ Noto'g'ri karta raqam! 16 ta raqam kiriting.")
        return
    
    # Formatlash: 1234 5678 9012 3456
    formatted = " ".join([digits_only[i:i+4] for i in range(0, 16, 4)])
    
    set_setting('card_number', formatted)
    await state.clear()
    await message.answer(f"✅ Karta raqam o'zgartirildi: <code>{formatted}</code>")
    await show_settings_menu(message)


@router.callback_query(F.data == "settings_card_holder")
async def settings_card_holder_callback(callback: CallbackQuery, state: FSMContext):
    """Karta egasini o'zgartirish"""
    if callback.from_user.id != ADMIN_ID:
        return
    
    current = get_setting('card_holder', 'ADMIN')
    
    text = "👤 <b>KARTA EGASI</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += f"📊 Joriy: <b>{current}</b>\n\n"
    text += "👤 Karta egasi ismini kiriting:\n"
    text += "<i>Masalan: ABDULLAYEV JAMSHID</i>"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="settings_cancel")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await state.set_state(AdminState.waiting_for_card_holder)


@router.message(AdminState.waiting_for_card_holder)
async def process_card_holder(message: Message, state: FSMContext):
    """Karta egasini saqlash"""
    if message.from_user.id != ADMIN_ID:
        return
    
    name = message.text.strip().upper()
    
    if len(name) < 3 or len(name) > 50:
        await message.answer("❌ Ism 3-50 belgi oralig'ida bo'lishi kerak!")
        return
    
    set_setting('card_holder', name)
    await state.clear()
    await message.answer(f"✅ Karta egasi o'zgartirildi: <b>{name}</b>")
    await show_settings_menu(message)


@router.callback_query(F.data == "settings_ref_bonus")
async def settings_ref_bonus_callback(callback: CallbackQuery, state: FSMContext):
    """Referal bonusni o'zgartirish"""
    if callback.from_user.id != ADMIN_ID:
        return
    
    current = get_setting('referral_bonus', '500')
    
    text = "🎁 <b>REFERAL BONUS</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += f"📊 Joriy bonus: <b>{int(current):,}</b> so'm\n\n"
    text += "💡 Bu - har bir taklif qilingan do'st uchun bonus\n\n"
    text += "💵 Yangi bonus miqdorini kiriting:\n"
    text += "<i>Masalan: 300 yoki 1000</i>"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="settings_cancel")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await state.set_state(AdminState.waiting_for_ref_bonus)


@router.message(AdminState.waiting_for_ref_bonus)
async def process_ref_bonus(message: Message, state: FSMContext):
    """Referal bonusni saqlash"""
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        new_bonus = int(message.text.strip().replace(",", "").replace(" ", ""))
        if new_bonus < 0 or new_bonus > 100000:
            await message.answer("❌ Bonus 0 - 100,000 oralig'ida bo'lishi kerak!")
            return
        
        set_setting('referral_bonus', str(new_bonus))
        await state.clear()
        await message.answer(f"✅ Referal bonus o'zgartirildi: <b>{new_bonus:,}</b> so'm")
        await show_settings_menu(message)
        
    except ValueError:
        await message.answer("❌ Noto'g'ri format! Faqat raqam kiriting.")


@router.callback_query(F.data == "settings_admin")
async def settings_admin_callback(callback: CallbackQuery, state: FSMContext):
    """Adminni o'zgartirish"""
    if callback.from_user.id != ADMIN_ID:
        return
    
    text = "👑 <b>ADMIN O'ZGARTIRISH</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += f"📊 Joriy admin: <code>{ADMIN_ID}</code>\n\n"
    text += "⚠️ <b>DIQQAT!</b>\n"
    text += "Admin ID ni o'zgartirish uchun .env faylini tahrirlang:\n\n"
    text += "<code>ADMIN_ID=yangi_id</code>\n\n"
    text += "💡 Yangi admin ID sini olish:\n"
    text += "1. @userinfobot ga /start yozing\n"
    text += "2. U sizga ID ko'rsatadi"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="settings_cancel")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)


@router.callback_query(F.data == "settings_api_balance")
async def settings_api_balance_callback(callback: CallbackQuery):
    """API balanslarini ko'rsatish - barcha 5 ta API"""
    if callback.from_user.id != ADMIN_ID:
        return
    
    await callback.answer("⏳ Tekshirilmoqda...")
    
    text = "📊 <b>API BALANSLAR</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    text += "🛒 <b>SMM Panellar:</b>\n"
    
    # 1. Peakerr SMM Panel
    try:
        import requests
        from config import SMM_API_KEY, SMM_API_URL
        response = requests.post(SMM_API_URL, data={'key': SMM_API_KEY, 'action': 'balance'}, timeout=10)
        data = response.json()
        balance = float(data.get('balance', 0))
        text += f"┣ ✅ Peakerr: <b>${balance:.2f}</b>\n"
    except Exception as e:
        text += f"┣ ❌ Peakerr: Xatolik\n"
    
    # 2. SMMMain Panel
    try:
        import requests
        from config import SMMMAIN_API_KEY, SMMMAIN_API_URL
        response = requests.post(SMMMAIN_API_URL, data={'key': SMMMAIN_API_KEY, 'action': 'balance'}, timeout=10)
        data = response.json()
        balance = float(data.get('balance', 0))
        text += f"┗ ✅ SMMMain: <b>${balance:.2f}</b>\n"
    except Exception as e:
        text += f"┗ ❌ SMMMain: Xatolik\n"
    
    text += "\n📱 <b>SMS API:</b>\n"
    
    # 3. 5SIM
    try:
        import requests
        from config import FIVESIM_API_KEY
        headers = {'Authorization': f'Bearer {FIVESIM_API_KEY}'}
        response = requests.get('https://5sim.net/v1/user/profile', headers=headers, timeout=10)
        data = response.json()
        balance = float(data.get('balance', 0))
        text += f"┣ ✅ 5SIM: <b>${balance:.2f}</b>\n"
    except Exception as e:
        text += f"┣ ❌ 5SIM: Xatolik\n"
    
    # 4. VakSMS
    try:
        import requests
        from config import SMS_API_KEY
        response = requests.get(f'https://vak-sms.com/api/getBalance/?apiKey={SMS_API_KEY}', timeout=10)
        data = response.json()
        balance = float(data.get('balance', 0))
        text += f"┣ ✅ VakSMS: <b>{balance:.2f} ₽</b>\n"
    except Exception as e:
        text += f"┣ ❌ VakSMS: Xatolik\n"
    
    # 5. SMSPVA
    try:
        import requests
        from config import SMSPVA_API_KEY
        response = requests.get(f'https://smspva.com/priemnik.php?metod=get_balance&apikey={SMSPVA_API_KEY}', timeout=10)
        data = response.json()
        balance = float(data.get('balance', 0))
        text += f"┗ ✅ SMSPVA: <b>${balance:.2f}</b>\n"
    except Exception as e:
        text += f"┗ ❌ SMSPVA: Xatolik\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Yangilash", callback_data="settings_api_balance")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="settings_cancel")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)


@router.callback_query(F.data == "settings_cancel")
async def settings_cancel_callback(callback: CallbackQuery, state: FSMContext):
    """Sozlamalar - orqaga"""
    if callback.from_user.id != ADMIN_ID:
        return
    
    await state.clear()
    await show_settings_menu(callback.message, edit=True)


@router.callback_query(F.data == "settings_restart_bot")
async def settings_restart_bot_callback(callback: CallbackQuery):
    """Botni qayta ishga tushirish"""
    if callback.from_user.id != ADMIN_ID:
        return
    
    await callback.answer("🔄 Bot qayta ishga tushirilmoqda...", show_alert=True)
    
    await callback.message.edit_text(
        "🔄 <b>Bot qayta ishga tushirilmoqda...</b>\n\n"
        "⏳ Iltimos, 5-10 soniya kuting va /start bosing."
    )
    
    # Botni qayta ishga tushirish
    import sys
    import os
    os.execv(sys.executable, ['python'] + sys.argv)


@router.callback_query(F.data == "ref_copy_link")
async def ref_copy_link_callback(call: CallbackQuery):
    """Referal havolasini nusxalash tugmasi"""
    await call.answer("📋 Havolani nusxalash uchun ustiga bosing va ushlab turing!", show_alert=True)


@router.message(F.text.in_(["🏠 Bosh menyu", "⬅️ Orqaga"]))
async def main_menu_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("👇 Quyidagi tugmalardan birini tanlang:", reply_markup=main_menu())


@router.message(F.text == "📱 Virtual raqamlar")
async def sms_menu(message: Message):
    user_id = message.from_user.id
    balance = get_balance(user_id)
    
    text = "📱 <b>VIRTUAL TELEFON RAQAMLAR</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += "🎯 <b>Qanday ishlaydi?</b>\n"
    text += "1️⃣ Platformani tanlang (Telegram, Instagram...)\n"
    text += "2️⃣ Davlatni tanlang\n"
    text += "3️⃣ Raqam oling va platformaga kiriting\n"
    text += "4️⃣ SMS kod kelganini tekshiring\n\n"
    text += f"💳 <b>Balansingiz:</b> {balance:,.0f} so'm\n\n"
    text += "👇 Platformani tanlang:"
    
    await message.answer(text, reply_markup=sms_platforms_inline())


# SMS callback handlerlar sms_handler.py da


# ==================== PAYMENT HANDLERS ====================

@router.message(F.text.in_(["💳 Click", "💳 Payme", "💳 Uzum"]))
async def payment_coming_soon(message: Message):
    """Click, Payme, Uzum - tez orada qo'shiladi"""
    await message.answer(
        "🚧 <b>Tez orada qo'shiladi!</b>\n\n"
        "Ushbu to'lov usuli hozircha ishlab chiqish jarayonida.\n"
        "Iltimos, <b>💳 Karta orqali</b> to'lov usulidan foydalaning.",
        reply_markup=payment_methods()
    )


@router.message(F.text == "💳 Karta orqali")
async def payment_method_selected(message: Message, state: FSMContext):
    method = "Visa/MasterCard"
    await state.update_data(payment_method=method)
    
    await message.answer(
        f"💳 <b>{method}</b> orqali to'lov\n\nTo'lov summasini tanlang:",
        reply_markup=payment_amounts()
    )
    await state.set_state(PaymentState.waiting_for_amount)


@router.callback_query(F.data.startswith('amount_'))
async def amount_selected(call: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state != PaymentState.waiting_for_amount:
        await call.answer()
        return
    
    amount_str = call.data.replace("amount_", "")
    
    if amount_str == "custom":
        min_dep = get_min_deposit()
        await call.message.edit_text(
            f"✏️ <b>Summa kiriting</b>\n\nMinimal: {min_dep:,} so'm\nMaksimal: 10,000,000 so'm\n\nSummani yozing (faqat raqam):"
        )
        await call.answer()
        # Holatni o'zgartirmaymiz - waiting_for_amount da qoladi
        return
    
    amount = int(amount_str)
    data = await state.get_data()
    method = data.get("payment_method", "Click")
    
    await state.update_data(payment_amount=amount)
    
    payment_info = get_payment_info(method, amount)
    
    await call.message.edit_text(
        f"💳 <b>To'lov ma'lumotlari</b>\n\n"
        f"📍 To'lov usuli: {method}\n"
        f"💰 Summa: {amount:,} so'm\n\n"
        f"📋 <b>To'lov qilish uchun:</b>\n"
        f"{payment_info}\n\n"
        f"✅ To'lov qilganingizdan so'ng chekni/screenshot'ni yuboring:",
        reply_markup=cancel_payment_inline()
    )
    await state.set_state(PaymentState.waiting_for_screenshot)
    await call.answer()


@router.message(PaymentState.waiting_for_amount, F.text)
async def custom_amount_entered(message: Message, state: FSMContext):
    """Foydalanuvchi o'zi summa kiritganda"""
    try:
        amount = int(message.text.replace(" ", "").replace(",", "").replace("'", ""))
    except ValueError:
        await message.answer("❌ Noto'g'ri summa! Faqat raqam kiriting (masalan: 50000):")
        return
    
    min_dep = get_min_deposit()
    if amount < min_dep:
        await message.answer(f"❌ Minimal summa {min_dep:,} so'm!")
        return
    
    if amount > 10000000:
        await message.answer("❌ Maksimal summa 10,000,000 so'm!")
        return
    
    data = await state.get_data()
    method = data.get("payment_method", "Click")
    
    await state.update_data(payment_amount=amount)
    
    payment_info = get_payment_info(method, amount)
    
    await message.answer(
        f"💳 <b>To'lov ma'lumotlari</b>\n\n"
        f"📍 To'lov usuli: {method}\n"
        f"💰 Summa: {amount:,} so'm\n\n"
        f"📋 <b>To'lov qilish uchun:</b>\n"
        f"{payment_info}\n\n"
        f"✅ To'lov qilganingizdan so'ng chekni/screenshot'ni yuboring:",
        reply_markup=cancel_payment_inline()
    )
    await state.set_state(PaymentState.waiting_for_screenshot)


@router.message(PaymentState.waiting_for_screenshot, F.photo)
async def payment_screenshot_photo(message: Message, state: FSMContext):
    """Rasm orqali chek qabul qilish"""
    user_id = message.from_user.id
    data = await state.get_data()
    amount = data.get("payment_amount", 0)
    method = data.get("payment_method", "Click")
    
    photo = message.photo[-1].file_id
    
    admin_text = f"💳 <b>Yangi to'lov!</b>\n\n"
    admin_text += f"👤 Foydalanuvchi: {message.from_user.full_name}\n"
    admin_text += f"🆔 ID: {user_id}\n"
    admin_text += f"📍 Usul: {method}\n"
    admin_text += f"💰 Summa: {amount:,} so'm\n"
    
    await bot.send_photo(ADMIN_ID, photo, caption=admin_text, reply_markup=payment_approve_inline(user_id, amount))
    
    await message.answer(
        "✅ <b>To'lov cheki yuborildi!</b>\n\nAdmin tekshirib, balansingizni to'ldiradi.\nOdatda 5-30 daqiqa ichida.",
        reply_markup=main_menu()
    )
    await state.clear()


@router.message(PaymentState.waiting_for_screenshot, F.document)
async def payment_screenshot_document(message: Message, state: FSMContext):
    """PDF yoki boshqa fayl orqali chek qabul qilish"""
    user_id = message.from_user.id
    data = await state.get_data()
    amount = data.get("payment_amount", 0)
    method = data.get("payment_method", "Click")
    
    document = message.document
    file_id = document.file_id
    file_name = document.file_name or "fayl"
    
    admin_text = f"💳 <b>Yangi to'lov!</b>\n\n"
    admin_text += f"👤 Foydalanuvchi: {message.from_user.full_name}\n"
    admin_text += f"🆔 ID: {user_id}\n"
    admin_text += f"📍 Usul: {method}\n"
    admin_text += f"💰 Summa: {amount:,} so'm\n"
    admin_text += f"📎 Fayl: {file_name}\n"
    
    await bot.send_document(ADMIN_ID, file_id, caption=admin_text, reply_markup=payment_approve_inline(user_id, amount))
    
    await message.answer(
        "✅ <b>To'lov cheki yuborildi!</b>\n\nAdmin tekshirib, balansingizni to'ldiradi.\nOdatda 5-30 daqiqa ichida.",
        reply_markup=main_menu()
    )
    await state.clear()


# ==================== CALLBACK HANDLERS ====================

@router.callback_query(F.data.startswith('section_'))
async def section_callback(call: CallbackQuery):
    """Bo'lim bosildganda - hech narsa qilmaydi, faqat bo'lim nomi"""
    await call.answer()


# ==================== PREMIUM OBUNA HANDLERS ====================

# Premium obuna narxlari
PREMIUM_PLANS = {
    1: {"name": "1 oylik", "price": 52000, "months": 1, "emoji": "📅"},
    3: {"name": "3 oylik", "price": 156000, "months": 3, "emoji": "📅"},
    6: {"name": "6 oylik", "price": 270000, "months": 6, "emoji": "🔥"},
    12: {"name": "1 yillik", "price": 415000, "months": 12, "emoji": "💎"}
}

@router.callback_query(F.data == "buy_premium_menu")
async def buy_premium_menu(call: CallbackQuery):
    """Premium obuna olish menyusi"""
    from database import check_premium_status, get_premium_remaining_days
    from keyboards_v3 import buy_premium_inline
    
    user_id = call.from_user.id
    is_premium = check_premium_status(user_id)
    remaining = get_premium_remaining_days(user_id)
    
    text = "⭐ <b>TELEGRAM PREMIUM OBUNA</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    if is_premium:
        text += f"✅ <b>Sizda premium obuna mavjud!</b>\n"
        text += f"📅 Qolgan kunlar: <b>{remaining} kun</b>\n\n"
    
    text += "🎁 <b>Premium obuna nima beradi?</b>\n\n"
    text += "✈️ Telegram akkauntingizga <b>Premium</b> obuna\n"
    text += "⭐ Premium emojilar va stikerlarga kirish\n"
    text += "📁 4GB gacha fayl yuklash\n"
    text += "🔊 Ovozli xabarlarni matnga aylantirish\n"
    text += "📌 Maxsus Premium badge\n"
    text += "📌 Reklamasiz Telegram\n"
    text += "⚡ Tez yuklab olish\n\n"
    
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "📌 <b>TARIFLAR:</b>\n\n"
    text += "📌📅 1 oylik — <b>52,000 so'm</b>\n"
    text += "📅 3 oylik — <b>156,000 so'm</b> <i>(oyiga 52K)</i>\n"
    text += "📌 6 oylik — <b>270,000 so'm</b> <i>(oyiga 45K)</i>\n"
    text += "📌 1 yillik — <b>415,000 so'm</b> <i>(oyiga 35K)</i>\n\n"
    
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "✅ <b>100% kafolat</b> | 📌 <b>Xavfsiz</b>\n"
    text += "📌👇 Tarifni tanlang:"
    
    await call.message.edit_text(text, reply_markup=buy_premium_inline())
    await call.answer()


@router.callback_query(F.data == "premium_info")
async def premium_info(call: CallbackQuery):
    """Premium haqida ma'lumot"""
    text = "❓ <b>PREMIUM OBUNA QANDAY ISHLAYDI?</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    text += "1️⃣ <b>Tarif tanlaysiz</b>\n"
    text += "   └ 1 oy, 3 oy, 6 oy yoki 1 yil\n\n"
    
    text += "2️⃣ <b>Telefon raqamingizni yuborasiz</b>\n"
    text += "   └ Telegram akkauntingiz raqami\n\n"
    
    text += "3️⃣ <b>To'lov qilasiz</b>\n"
    text += "   └ Bot balansidan yoki karta orqali\n\n"
    
    text += "4️⃣ <b>Admin premium olib beradi</b>\n"
    text += "   └ 1-24 soat ichida faollashtiriladi\n\n"
    
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "🔒 <b>KAFOLAT:</b>\n"
    text += "• Agar premium faollashtirilmasa - pullar qaytariladi\n"
    text += "• Muammo bo'lsa - admin bilan bog'laning\n\n"
    
    text += "💬 <b>Savollar uchun:</b> @islomh"
    
    await call.answer()
    await call.message.edit_text(text, reply_markup=buy_premium_inline())


@router.callback_query(F.data.startswith("select_premium_"))
async def select_premium_plan(call: CallbackQuery, state: FSMContext):
    """Tarif tanlash - telefon raqam so'rash"""
    from database import get_balance
    from keyboards_v3 import phone_request_keyboard
    
    months = int(call.data.replace("select_premium_", ""))
    if months not in PREMIUM_PLANS:
        await call.answer("❌ Xato tarif!", show_alert=True)
        return
    
    plan = PREMIUM_PLANS[months]
    user_id = call.from_user.id
    balance = get_balance(user_id)
    
    # Balansni tekshirish
    if balance < plan["price"]:
        await call.answer(
            f"❌ Balansingiz yetarli emas!\n\n"
            f"💰 Narx: {plan['price']:,} so'm\n"
            f"👛 Balans: {balance:,.0f} so'm\n\n"
            f"📌 Avval balansni to'ldiring!",
            show_alert=True
        )
        return
    
    # State'ga tarif ma'lumotini saqlash
    await state.update_data(premium_months=months, premium_price=plan["price"], premium_name=plan["name"])
    
    text = f"⭐ <b>PREMIUM OBUNA - {plan['name'].upper()}</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    text += f"{plan['emoji']} Tarif: <b>{plan['name']}</b>\n"
    text += f"💰 Narx: <b>{plan['price']:,} so'm</b>\n"
    text += f"👛 Balansingiz: <b>{balance:,.0f} so'm</b>\n\n"
    
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "📱 <b>TELEFON RAQAMINGIZNI YUBORING</b>\n\n"
    
    text += "Premium olinadigan Telegram akkauntingiz\n"
    text += "telefon raqamini yuboring.\n\n"
    
    text += "👇 Quyidagi tugmani bosing yoki qo'lda yozing:\n"
    text += "<i>Masalan: +998901234567</i>"
    
    await call.message.delete()
    await call.message.answer(text, reply_markup=phone_request_keyboard())
    await state.set_state(PremiumState.waiting_for_phone)
    await call.answer()


@router.message(PremiumState.waiting_for_phone, F.contact)
async def process_premium_phone_contact(message: Message, state: FSMContext):
    """Telefon raqam - kontakt orqali"""
    phone = message.contact.phone_number
    if not phone.startswith("+"):
        phone = "+" + phone
    
    await process_premium_phone(message, state, phone)


@router.message(PremiumState.waiting_for_phone, F.text)
async def process_premium_phone_text(message: Message, state: FSMContext):
    """Telefon raqam - matn orqali"""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Premium obuna bekor qilindi.", reply_markup=main_menu())
        return
    
    # Telefon raqamni tekshirish
    phone = message.text.strip()
    
    # Oddiy validatsiya
    phone_clean = phone.replace("+", "").replace(" ", "").replace("-", "")
    if not phone_clean.isdigit() or len(phone_clean) < 9:
        await message.answer(
            "❌ <b>Noto'g'ri telefon raqam!</b>\n\n"
            "Telefon raqamni to'g'ri formatda yuboring:\n"
            "<code>+998901234567</code>"
        )
        return
    
    if not phone.startswith("+"):
        phone = "+" + phone
    
    await process_premium_phone(message, state, phone)


async def process_premium_phone(message: Message, state: FSMContext, phone: str):
    """Telefon raqamni qayta ishlash va so'rov yaratish"""
    from database import get_balance, update_balance, add_premium_request
    from keyboards_v3 import premium_admin_inline
    
    data = await state.get_data()
    months = data.get("premium_months")
    price = data.get("premium_price")
    plan_name = data.get("premium_name")
    user_id = message.from_user.id
    
    # Balansni qayta tekshirish
    balance = get_balance(user_id)
    if balance < price:
        await message.answer(
            f"❌ <b>Balansingiz yetarli emas!</b>\n\n"
            f"💰 Kerak: {price:,} so'm\n"
            f"👛 Balans: {balance:,.0f} so'm",
            reply_markup=main_menu()
        )
        await state.clear()
        return
    
    # Balansdan yechish
    update_balance(user_id, -price)
    
    # So'rov yaratish
    request_id = add_premium_request(user_id, phone, months, price)
    
    # Foydalanuvchiga tasdiqlash
    success_text = "✅ <b>SO'ROV QABUL QILINDI!</b>\n"
    success_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    success_text += f"📱 Telefon: <code>{phone}</code>\n"
    success_text += f"📦 Tarif: <b>{plan_name}</b>\n"
    success_text += f"💰 To'lov: <b>{price:,} so'm</b>\n"
    success_text += f"🆔 So'rov ID: <code>#{request_id}</code>\n\n"
    
    success_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    success_text += "⏳ <b>Admin 1-24 soat ichida</b>\n"
    success_text += "<b>premium obunani faollashtiradi.</b>\n\n"
    
    success_text += "📲 Telegram'dan <b>kod</b> keladi.\n"
    success_text += "Kodni hech kimga bermang!\n\n"
    
    success_text += "✅ Faollashtirilganda xabar beriladi."
    
    await message.answer(success_text, reply_markup=main_menu())
    
    # Adminga xabar
    admin_text = "⭐ <b>YANGI PREMIUM SO'ROV!</b>\n"
    admin_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    admin_text += f"🆔 So'rov: <code>#{request_id}</code>\n"
    admin_text += f"👤 Foydalanuvchi: {message.from_user.full_name}\n"
    admin_text += f"📱 Username: @{message.from_user.username or 'yoq'}\n"
    admin_text += f"🆔 User ID: <code>{user_id}</code>\n\n"
    
    admin_text += f"📱 <b>Telefon: <code>{phone}</code></b>\n"
    admin_text += f"📅 Tarif: <b>{plan_name}</b>\n"
    admin_text += f"💰 To'lov: <b>{price:,} so'm</b>\n\n"
    
    admin_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    admin_text += "👆 Premium olib bergandan keyin\n"
    admin_text += "✅ Tasdiqlash tugmasini bosing."
    
    try:
        admin_msg = await bot.send_message(
            ADMIN_ID, 
            admin_text, 
            reply_markup=premium_admin_inline(user_id, months, price, request_id)
        )
        # Admin message ID ni saqlash
        from database import update_premium_request_status
        update_premium_request_status(request_id, 'pending', admin_msg.message_id)
    except Exception as e:
        logger.error(f"Admin ga xabar yuborishda xato: {e}")
    
    await state.clear()


@router.callback_query(F.data.startswith("approve_premium_"))
async def approve_premium_request(call: CallbackQuery):
    """Admin premium so'rovni tasdiqlash"""
    if call.from_user.id != ADMIN_ID:
        await call.answer("❌ Sizda ruxsat yo'q!", show_alert=True)
        return
    
    request_id = int(call.data.replace("approve_premium_", ""))
    
    from database import get_premium_request, update_premium_request_status, add_premium_subscription, get_premium_remaining_days
    
    request = get_premium_request(request_id)
    if not request:
        await call.answer("❌ So'rov topilmadi!", show_alert=True)
        return
    
    # request: (id, user_id, phone, months, price, status, admin_message_id, created_at, processed_at)
    req_id, user_id, phone, months, price, status, admin_msg_id, created_at, processed_at = request
    
    if status != 'pending':
        await call.answer("❌ Bu so'rov allaqachon ko'rib chiqilgan!", show_alert=True)
        return
    
    # Premium qo'shish
    plan_name = PREMIUM_PLANS.get(months, {}).get("name", f"{months} oylik")
    add_premium_subscription(user_id, plan_name, months, price)
    
    # So'rov holatini yangilash
    update_premium_request_status(request_id, 'approved')
    
    remaining = get_premium_remaining_days(user_id)
    
    # Foydalanuvchiga xabar
    user_text = "🎉 <b>TABRIKLAYMIZ!</b>\n"
    user_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    user_text += "⭐ <b>PREMIUM OBUNA FAOLLASHTIRILDI!</b>\n\n"
    user_text += f"📱 Telefon: <code>{phone}</code>\n"
    user_text += f"📅 Tarif: <b>{plan_name}</b>\n"
    user_text += f"⏰ Muddat: <b>{remaining} kun</b>\n\n"
    user_text += "✨ Premium obunangiz bilan zavqlaning!\n"
    user_text += "Telegram ilovasini qayta ishga tushiring."
    
    try:
        await bot.send_message(user_id, user_text)
    except:
        pass
    
    # Admin xabarini yangilash
    updated_text = call.message.text + "\n\n✅ <b>TASDIQLANDI!</b>"
    await call.message.edit_text(updated_text, reply_markup=None)
    await call.answer("✅ Premium faollashtirildi!")


@router.callback_query(F.data.startswith("reject_premium_"))
async def reject_premium_request(call: CallbackQuery):
    """Admin premium so'rovni rad etish"""
    if call.from_user.id != ADMIN_ID:
        await call.answer("❌ Sizda ruxsat yo'q!", show_alert=True)
        return
    
    request_id = int(call.data.replace("reject_premium_", ""))
    
    from database import get_premium_request, update_premium_request_status, update_balance
    
    request = get_premium_request(request_id)
    if not request:
        await call.answer("❌ So'rov topilmadi!", show_alert=True)
        return
    
    req_id, user_id, phone, months, price, status, admin_msg_id, created_at, processed_at = request
    
    if status != 'pending':
        await call.answer("❌ Bu so'rov allaqachon ko'rib chiqilgan!", show_alert=True)
        return
    
    # Pulni qaytarish
    update_balance(user_id, price)
    
    # So'rov holatini yangilash
    update_premium_request_status(request_id, 'rejected')
    
    # Foydalanuvchiga xabar
    user_text = "❌ <b>PREMIUM SO'ROV RAD ETILDI</b>\n"
    user_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    user_text += f"📌 Telefon: <code>{phone}</code>\n"
    user_text += f"💰 Qaytarilgan summa: <b>{price:,} so'm</b>\n\n"
    user_text += "Pullaringiz balansingizga qaytarildi.\n"
    user_text += "Muammo bo'lsa admin bilan bog'laning."
    
    try:
        await bot.send_message(user_id, user_text)
    except:
        pass
    
    # Admin xabarini yangilash
    updated_text = call.message.text + "\n\n❌ <b>RAD ETILDI!</b> (Pul qaytarildi)"
    await call.message.edit_text(updated_text, reply_markup=None)
    await call.answer("❌ So'rov rad etildi, pul qaytarildi!")


# ========== TELEGRAM MENU CALLBACKS ==========
@router.callback_query(F.data == "tg_members_menu")
async def telegram_members_menu(call: CallbackQuery):
    """Telegram obunachi turlari"""
    text = "👥 <b>TELEGRAM OBUNACHI</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += "📌 <b>Obunachi turlari mavjud</b>\n"
    text += "⏰ Kafolat: 30 kundan umrbodgacha\n"
    text += "⚡ Tezlik: 500 - 10,000/kun\n\n"
    text += "👇 Obunachi turini tanlang:"
    await call.message.edit_text(text, reply_markup=telegram_members_dynamic())
    await call.answer()


@router.callback_query(F.data == "tg_subscriber_premium")
async def telegram_premium_members_menu(call: CallbackQuery):
    """Telegram Premium obunachi turlari"""
    text = "⭐ <b>TELEGRAM PREMIUM OBUNACHI</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += "⭐ Telegram Premium hisoblar\n"
    text += "⏰ Kafolat: 7-30 kun\n"
    text += "⚡ Tezlik: 100 - 500/kun\n\n"
    text += "👇 Premium obunachi turini tanlang:"
    await call.message.edit_text(text, reply_markup=telegram_premium_members_dynamic())
    await call.answer()


@router.callback_query(F.data == "tg_views_menu")
async def telegram_views_menu(call: CallbackQuery):
    """Telegram ko'rish turlari"""
    text = "👁 <b>TELEGRAM KO'RISH</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += "📌 <b>Ko'rish turlari mavjud</b>\n"
    text += "⚡ Tezlik: 20K - 1M/soat\n\n"
    text += "👇 Ko'rish turini tanlang:"
    await call.message.edit_text(text, reply_markup=telegram_views_dynamic())
    await call.answer()


@router.callback_query(F.data == "tg_reactions_menu")
async def telegram_reactions_menu(call: CallbackQuery):
    """Telegram reaksiya turlari"""
    text = "👍 <b>TELEGRAM REAKSIYA</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += "📌 <b>Reaksiya turlari mavjud</b>\n"
    text += "⚡ Tezlik: 30K - 100K/soat\n\n"
    text += "👇 Reaksiya turini tanlang:"
    await call.message.edit_text(text, reply_markup=telegram_reactions_dynamic())
    await call.answer()


@router.callback_query(F.data == "tg_other_menu")
async def telegram_other_menu(call: CallbackQuery):
    """Telegram boshqa xizmatlar"""
    text = "📦 <b>TELEGRAM BOSHQA XIZMATLAR</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += "📌 <b>Share, Vote va boshqalar</b>\n\n"
    text += "👇 Xizmatni tanlang:"
    await call.message.edit_text(text, reply_markup=telegram_other_inline())
    await call.answer()


@router.callback_query(F.data == "tg_other_services")
async def telegram_other_services_callback(call: CallbackQuery):
    """Telegram boshqa xizmatlari"""
    text = "📦 <b>TELEGRAM - BOSHQA XIZMATLAR</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += "👇 Xizmatni tanlang:"
    await call.message.edit_text(text, reply_markup=telegram_other_services_inline())
    await call.answer()


@router.callback_query(F.data == "back_to_telegram")
async def back_to_telegram_callback(call: CallbackQuery):
    """Telegram menyusiga qaytish"""
    text = "🔵 <b>TELEGRAM XIZMATLARI</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += "📌 <b>Narxlar 1000 dona uchun</b>\n"
    text += "⚡ <b>Tez va sifatli yetkazib berish</b>\n"
    text += "✅ <b>Kafolat beriladi</b>\n\n"
    text += "👇 Xizmat turini tanlang:"
    await call.message.edit_text(text, reply_markup=telegram_services_inline())
    await call.answer()


# Menu callback larini exclude qilish
MENU_CALLBACKS = ['tg_members_menu', 'tg_views_menu', 'tg_reactions_menu', 'tg_other_menu', 
                  'tg_other_services', 'tg_subscriber_premium', 'ig_followers', 'ig_likes',
                  'ig_views', 'ig_comments', 'yt_subscribers', 'yt_views', 'yt_likes',
                  'tt_followers', 'tt_likes', 'tt_views', 'tt_comments']

@router.callback_query(F.data.startswith(('tg_', 'ig_', 'yt_', 'tt_')))
async def service_callback(call: CallbackQuery, state: FSMContext):
    service_key = call.data
    
    # Menu callback larini o'tkazib yuborish
    if service_key in MENU_CALLBACKS:
        return
    
    # Section callback larini o'tkazib yuborish
    if service_key.startswith('section_'):
        await call.answer()
        return
    
    if service_key not in SERVICES_MAP:
        await call.answer("Bu xizmat hozircha mavjud emas", show_alert=True)
        return
    
    info = SERVICES_MAP[service_key]
    details_text, price, min_qty, max_qty = get_service_details_text(service_key)
    
    await state.update_data(
        service_name=info["name"],
        service_key=service_key,
        price_per_1000=price,
        min_qty=min_qty,
        max_qty=max_qty
    )
    
    await call.message.delete()
    await call.message.answer(
        f"{details_text}\n🔗 Havola yoki username yuboring:",
        reply_markup=cancel_button()
    )
    await state.set_state(OrderState.waiting_for_link)
    await call.answer()


@router.callback_query(F.data == "back_to_services")
async def back_to_services_callback(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer(
        "✅ <b>Bizning xizmatlarimizni tanlaganingizdan xursandmiz!</b>\n\n👇 Quyidagi Ijtimoiy tarmoqlardan birini tanlang.",
        reply_markup=social_networks_menu()
    )


@router.callback_query(F.data.startswith('approve_'))
async def approve_payment(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        await call.answer("Sizga ruxsat yo'q!", show_alert=True)
        return
    
    parts = call.data.split("_")
    user_id = int(parts[1])
    amount = int(parts[2])
    
    update_balance(user_id, amount)
    
    await call.message.edit_caption(call.message.caption + f"\n\n✅ <b>TASDIQLANDI</b>")
    
    await bot.send_message(
        user_id,
        f"✅ <b>To'lov tasdiqlandi!</b>\n\n💰 {amount:,} so'm balansingizga qo'shildi.\n\nYangi balans: {get_balance(user_id):,} so'm"
    )
    await call.answer("Tasdiqlandi!")


@router.callback_query(F.data.startswith('reject_'))
async def reject_payment(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        await call.answer("Sizga ruxsat yo'q!", show_alert=True)
        return
    
    parts = call.data.split("_")
    user_id = int(parts[1])
    
    await call.message.edit_caption(call.message.caption + f"\n\n❌ <b>BEKOR QILINDI</b>")
    
    await bot.send_message(
        user_id,
        "❌ <b>To'lov bekor qilindi!</b>\n\n"
        "Sabab: Noto'g'ri chek yoki to'lov topilmadi.\n"
        "Iltimos, qaytadan to'g'ri chek yuboring yoki admin bilan bog'laning.",
        reply_markup=contact_admin_inline()
    )
    await call.answer("Bekor qilindi!")


@router.callback_query(F.data.startswith('partial_'))
async def partial_payment(call: CallbackQuery, state: FSMContext):
    """To'liq emas - admin haqiqiy summani kiritadi"""
    if call.from_user.id != ADMIN_ID:
        await call.answer("Sizga ruxsat yo'q!", show_alert=True)
        return
    
    parts = call.data.split("_")
    user_id = int(parts[1])
    original_amount = int(parts[2])
    
    await state.update_data(
        partial_user_id=user_id,
        partial_original_amount=original_amount,
        partial_message_id=call.message.message_id
    )
    
    await call.message.answer(
        f"⚠️ <b>To'liq emas</b>\n\n"
        f"👤 Foydalanuvchi ID: {user_id}\n"
        f"💰 Aytilgan summa: {original_amount:,} so'm\n\n"
        f"✏️ Foydalanuvchi qancha pul tashlagan? (faqat raqam yozing):"
    )
    await state.set_state(AdminState.waiting_for_partial_amount)
    await call.answer()


@router.message(AdminState.waiting_for_partial_amount)
async def process_partial_amount(message: Message, state: FSMContext):
    """Admin kiritgan summa foydalanuvchiga qo'shiladi"""
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        actual_amount = int(message.text.replace(" ", "").replace(",", ""))
    except ValueError:
        await message.answer("❌ Noto'g'ri summa! Faqat raqam kiriting:")
        return
    
    if actual_amount <= 0:
        await message.answer("❌ Summa 0 dan katta bo'lishi kerak!")
        return
    
    data = await state.get_data()
    user_id = data.get("partial_user_id")
    original_amount = data.get("partial_original_amount")
    
    # Balansga qo'shish
    update_balance(user_id, actual_amount)
    
    await message.answer(
        f"✅ <b>To'lov qisman tasdiqlandi!</b>\n\n"
        f"👤 Foydalanuvchi ID: {user_id}\n"
        f"💰 Aytilgan: {original_amount:,} so'm\n"
        f"✅ Tasdiqlangan: {actual_amount:,} so'm"
    )
    
    # Foydalanuvchiga xabar
    await bot.send_message(
        user_id,
        f"⚠️ <b>To'lov qisman tasdiqlandi!</b>\n\n"
        f"💰 Siz aytgan summa: {original_amount:,} so'm\n"
        f"✅ Haqiqiy summa: {actual_amount:,} so'm\n\n"
        f"💳 {actual_amount:,} so'm balansingizga qo'shildi.\n"
        f"📊 Yangi balans: {get_balance(user_id):,} so'm"
    )
    
    await state.clear()


# ==================== ORDER STATE HANDLERS ====================

@router.message(OrderState.waiting_for_link)
async def process_link(message: Message, state: FSMContext):
    link = message.text.strip()
    
    if "Bekor" in link or "bekor" in link:
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=main_menu())
        return
    
    if not link.startswith(("http://", "https://", "t.me/", "@")):
        await message.answer("❌ Noto'g'ri format. Havola yoki @username yuboring:")
        return
    
    data = await state.get_data()
    min_qty = data.get("min_qty", 100)
    max_qty = data.get("max_qty", 1000000)
    
    await state.update_data(link=link)
    await message.answer(
        f"🔢 Miqdorni kiriting:\n📊 Min: {min_qty:,} | Max: {max_qty:,}",
        reply_markup=cancel_button()
    )
    await state.set_state(OrderState.waiting_for_quantity)


@router.message(OrderState.waiting_for_quantity)
async def process_quantity(message: Message, state: FSMContext):
    text = message.text.strip()
    
    if "Bekor" in text or "bekor" in text:
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=main_menu())
        return
    
    data = await state.get_data()
    min_qty = data.get("min_qty", 100)
    max_qty = data.get("max_qty", 1000000)
    
    try:
        quantity = int(text)
        if quantity < min_qty:
            await message.answer(f"❌ Minimum {min_qty:,} ta. Qayta kiriting:")
            return
        if quantity > max_qty:
            await message.answer(f"❌ Maximum {max_qty:,} ta. Qayta kiriting:")
            return
    except ValueError:
        await message.answer("❌ Raqam kiriting:")
        return
    
    price_per_1000 = data.get("price_per_1000", 0)
    total_price = int((quantity / 1000) * price_per_1000)
    
    await state.update_data(quantity=quantity, total_price=total_price)
    
    await message.answer(
        f"📋 <b>Buyurtma tafsilotlari:</b>\n\n"
        f"📦 Xizmat: {data.get('service_name')}\n"
        f"🔗 Havola: {data.get('link')}\n"
        f"🔢 Miqdor: {quantity:,} ta\n"
        f"💰 Narx: {total_price:,} so'm\n\n"
        f"Tasdiqlaysizmi?",
        reply_markup=confirm_order_inline()
    )
    await state.set_state(OrderState.confirm_order)


@router.callback_query(F.data == "confirm_order")
async def confirm_order_callback(call: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state != OrderState.confirm_order:
        await call.answer()
        return
    
    user_id = call.from_user.id
    balance = get_balance(user_id)
    
    data = await state.get_data()
    total_price = data.get("total_price", 0)
    
    if balance < total_price:
        await call.message.edit_text(
            f"❌ Balans yetarli emas!\n\nSizning balansingiz: {balance:,} so'm\nKerak: {total_price:,} so'm\n\nBalansni to'ldiring: /balance"
        )
        await state.clear()
        return
    
    service_key = data.get("service_key")
    link = data.get("link")
    quantity = data.get("quantity")
    
    # Balansdan yechish
    update_balance(user_id, -total_price)
    
    # Bazaga qo'shish
    order_id = add_order(user_id, service_key, link, quantity, total_price)
    
    await call.message.edit_text(
        f"✅ <b>Buyurtma muvaffaqiyatli qabul qilindi!</b>\n\n"
        f"📦 Xizmat: {data.get('service_name')}\n"
        f"📊 Miqdor: {quantity:,} ta\n"
        f"💰 Narx: {total_price:,} so'm\n"
        f"🆔 Buyurtma raqami: #{order_id}\n\n"
        f"📋 Buyurtma holati: /orders"
    )
    
    await state.clear()
    await call.answer()


@router.callback_query(F.data == "cancel_order")
async def cancel_order_callback(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("❌ Buyurtma bekor qilindi.")
    await call.message.answer("👇 Quyidagi tugmalardan birini tanlang:", reply_markup=main_menu())
    await call.answer()


@router.callback_query(F.data == "cancel_payment")
async def cancel_payment_callback(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("To'lov bekor qilindi.")
    await call.message.answer("Quyidagi tugmalardan birini tanlang:", reply_markup=main_menu())
    await call.answer()


# ==================== MAIN ====================

# SMS Handler - alohida router
from sms_handler import sms_router

dp.include_router(sms_router)  # SMS router birinchi - prioritet
dp.include_router(router)


# ==================== AVTOMATIK ZAXIRA SCHEDULER ====================
async def auto_backup_scheduler(bot_instance):
    """Har kuni soat 03:00 da avtomatik zaxira"""
    import asyncio
    from datetime import datetime, timedelta
    
    while True:
        now = datetime.now()
        # Keyingi soat 03:00 ni hisoblash
        next_run = now.replace(hour=3, minute=0, second=0, microsecond=0)
        if now >= next_run:
            next_run += timedelta(days=1)
        
        # Keyingi zaxiragacha kutish
        wait_seconds = (next_run - now).total_seconds()
        
        try:
            await asyncio.sleep(wait_seconds)
            await auto_backup_job(bot_instance)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Avtomatik zaxira xatolik: {e}")
            await asyncio.sleep(60)  # Xatolikdan keyin 1 daqiqa kutish


async def main():
    # Database init
    init_db()
    
    # Bot komandalarini sozlash (umumiy)
    from aiogram.types import BotCommand, BotCommandScopeChat
    commands = [
        BotCommand(command="start", description="Botni ishga tushirish")
    ]
    await bot.set_my_commands(commands)
    
    # Admin uchun qo'shimcha komandalar
    admin_commands = [
        BotCommand(command="start", description="Botni ishga tushirish"),
        BotCommand(command="admin", description="Admin panel")
    ]
    try:
        await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=ADMIN_ID))
    except Exception as e:
        logger.warning(f"Admin komandalarini sozlashda xato: {e}")
    
    # Bot profil rasmini olish va cache'lash
    global BOT_PHOTO_URL
    try:
        photos = await bot.get_user_profile_photos(bot.id, limit=1)
        if photos.total_count > 0:
            file = await bot.get_file(photos.photos[0][0].file_id)
            BOT_PHOTO_URL = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"
            logger.info(f"Bot profil rasmi yuklandi: {BOT_PHOTO_URL[:50]}...")
    except Exception as e:
        logger.warning(f"Bot profil rasmini olishda xato: {e}")
        BOT_PHOTO_URL = None
    
    # Avtomatik zaxira scheduler ni boshlash
    backup_task = asyncio.create_task(auto_backup_scheduler(bot))
    logger.info("Avtomatik zaxira scheduler ishga tushirildi")
    
    logger.info("Bot ishga tushirilmoqda...")
    
    try:
        await dp.start_polling(bot)
    finally:
        backup_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
