# -*- coding: utf-8 -*-
"""
Mini App Backend konfiguratsiyasi
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# .env faylni yuklash (parent directory'dan)
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(env_path)

# Bot konfiguratsiyasi
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
BOT_API_URL = os.getenv("BOT_API_URL", "http://localhost:8000")  # Bot API URL (Railway yoki local)

# Admin ID'lar ro'yxati (bir nechta admin qo'shish uchun)
ADMIN_IDS = [ADMIN_ID]  # Qo'shimcha adminlar qo'shish uchun ro'yxatga qo'shing

# Ma'lumotlar bazasi
DATABASE_PATH = Path(__file__).parent.parent.parent.parent / "smm_bot.db"
DATABASE_NAME = str(DATABASE_PATH)

# SMM Panel API sozlamalari
SMM_API_URL = os.getenv("SMM_API_URL", "https://peakerr.com/api/v2")
SMM_API_KEY = os.getenv("SMM_API_KEY", "")
SMMMAIN_API_URL = os.getenv("SMMMAIN_API_URL", "https://smmmain.com/api/v2")
SMMMAIN_API_KEY = os.getenv("SMMMAIN_API_KEY", "")

# SMS API
SMS_API_KEY = os.getenv("SMS_API_KEY", "")
FIVESIM_API_KEY = os.getenv("FIVESIM_API_KEY", "")
SMSPVA_API_KEY = os.getenv("SMSPVA_API_KEY", "")

# Click to'lov tizimi
# Click merchant kabinetdan olish: https://merchant.click.uz
CLICK_MERCHANT_ID = os.getenv("CLICK_MERCHANT_ID", "")
CLICK_SERVICE_ID = os.getenv("CLICK_SERVICE_ID", "")
CLICK_SECRET_KEY = os.getenv("CLICK_SECRET_KEY", "")

# CORS origins
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://web.telegram.org",
    "https://*.telegram.org",
    FRONTEND_URL,
]

# JWT sozlamalari
SECRET_KEY = os.getenv("SECRET_KEY", BOT_TOKEN[:32] if BOT_TOKEN else "secret-key-for-jwt")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 soat

# To'lov kartalari
PAYMENT_CARDS = {
    "Click": {
        "card": os.getenv("CLICK_CARD", "9860 1901 0198 2212"),
        "name": os.getenv("CLICK_NAME", "IDEAL SMM")
    },
    "Payme": {
        "card": os.getenv("PAYME_CARD", "9860 1901 0198 2212"),
        "name": os.getenv("PAYME_NAME", "IDEAL SMM")
    },
    "Uzum": {
        "card": os.getenv("UZUM_CARD", "9860 1901 0198 2212"),
        "name": os.getenv("UZUM_NAME", "IDEAL SMM")
    }
}
