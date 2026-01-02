import os
from dotenv import load_dotenv

load_dotenv()

# Bot konfiguratsiyasi
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Admin ID
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# Kanal username
CHANNEL_USERNAME = "@ideaLsmm_uzb"

# Ma'lumotlar bazasi (SQLite)
DATABASE_NAME = "smm_bot.db"

# SMM Panel API sozlamalari - Peakerr (Asosiy)
SMM_API_URL = os.getenv("SMM_API_URL", "https://peakerr.com/api/v2")
SMM_API_KEY = os.getenv("SMM_API_KEY", "")

# SMMMain API (Ikkinchi panel - O'zbekiston/Rossiya targetli xizmatlar)
SMMMAIN_API_URL = os.getenv("SMMMAIN_API_URL", "https://smmmain.com/api/v2")
SMMMAIN_API_KEY = os.getenv("SMMMAIN_API_KEY", "")

# SMS-Activate API (Virtual telefon raqamlar) - VAK-SMS
SMS_API_KEY = os.getenv("SMS_API_KEY", "")

# 5SIM.NET API (Virtual telefon raqamlar - arzon)
FIVESIM_API_KEY = os.getenv("FIVESIM_API_KEY", "")

# SMSPVA.COM API (Virtual telefon raqamlar - eng arzon!)
SMSPVA_API_KEY = os.getenv("SMSPVA_API_KEY", "")

# To'lov karta raqamlari
# Shu yerga o'zingizning haqiqiy karta raqamlaringizni kiriting!
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
    },
    "Visa/MasterCard": {
        "card": os.getenv("VISA_CARD", "9860 1901 0198 2212"),
        "name": os.getenv("VISA_NAME", "IDEAL SMM")
    }
}
