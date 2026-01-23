# -*- coding: utf-8 -*-
"""
VIRTUAL RAQAMLAR - Professional SMS Handler
Barcha SMS xizmatlari uchun handlerlar
3 ta API: VAK-SMS, SMSPVA, 5SIM
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from keyboards_v3 import (
    sms_platforms_inline, 
    sms_telegram_countries_inline,
    sms_countries_inline,
    sms_waiting_inline,
    sms_received_inline,
    main_menu
)
from database import get_balance, update_balance, get_setting
from sms_prices import TELEGRAM_SMS_PRICES, get_cheapest_by_country
from sms_api import VakSMS
from smspva_api import SMSPVA
from fivesim_api import FiveSIM
from config import SMSPVA_API_KEY, SMS_API_KEY, FIVESIM_API_KEY

# Router
sms_router = Router()

# API instances
vaksms_api = VakSMS(SMS_API_KEY)
smspva_api = SMSPVA(SMSPVA_API_KEY)
fivesim_api = FiveSIM(FIVESIM_API_KEY)


# Sozlamalardan kurslarni oluvchi funksiyalar
def get_usd_rate():
    return int(get_setting('usd_rate', '12900'))

def get_rub_rate():
    return int(get_setting('rub_rate', '140'))

def get_markup_percent():
    return int(get_setting('markup_percent', '20'))


# ==================== ASOSIY MENYU ====================

@sms_router.callback_query(F.data == "sms_platforms")
async def sms_platforms_menu(call: CallbackQuery):
    """SMS platformalar asosiy menyusi"""
    user_id = call.from_user.id
    balance = get_balance(user_id)
    
    text = "VIRTUAL TELEFON RAQAMLAR\n"
    text += "=" * 30 + "\n\n"
    text += f"Balansingiz: {balance:,.0f} so'm\n\n"
    text += "Platformani tanlang:\n"
    text += "(qavsda eng arzon narx so'm da)"
    
    try:
        await call.message.edit_text(text, reply_markup=sms_platforms_inline())
    except TelegramBadRequest:
        pass
    await call.answer()


@sms_router.callback_query(F.data == "sms_back")
async def sms_back_to_menu(call: CallbackQuery):
    """Asosiy menyuga qaytish"""
    await call.message.delete()
    await call.message.answer("Asosiy menyu", reply_markup=main_menu(call.from_user.id))
    await call.answer()


# ==================== TELEGRAM ====================

@sms_router.callback_query(F.data == "sms_tg")
async def sms_telegram_menu(call: CallbackQuery, state: FSMContext):
    """Telegram davlatlar menyusi"""
    user_id = call.from_user.id
    balance = get_balance(user_id)
    
    text = "TELEGRAM VIRTUAL RAQAMLAR\n"
    text += "=" * 30 + "\n\n"
    text += f"Balansingiz: {balance:,.0f} so'm\n\n"
    text += "Davlatni tanlang:\n"
    text += "(eng arzon API avtomatik tanlanadi)\n\n"
    text += "Tugma ustida narx ko'rsatilgan (so'm)"
    
    await state.update_data(sms_platform="telegram")
    
    try:
        await call.message.edit_text(text, reply_markup=sms_telegram_countries_inline())
    except TelegramBadRequest:
        pass
    await call.answer()


@sms_router.callback_query(F.data.startswith("buy_sms_tg_"))
async def buy_telegram_number(call: CallbackQuery, state: FSMContext):
    """Telegram raqam sotib olish"""
    # Format: buy_sms_tg_smspva_vn
    parts = call.data.split("_")
    if len(parts) < 5:
        await call.answer("Xatolik yuz berdi", show_alert=True)
        return
    
    api_name = parts[3]  # smspva yoki vaksms
    country_code = parts[4]  # vn, uz, ru, etc
    
    # Narxni topish
    price_key = f"{api_name}_{country_code}"
    price_data = TELEGRAM_SMS_PRICES.get(price_key)
    
    if not price_data:
        await call.answer("Narx topilmadi", show_alert=True)
        return
    
    user_id = call.from_user.id
    balance = get_balance(user_id)
    price_som = price_data["price_som"]
    
    # Balans tekshirish
    if balance < price_som:
        await call.answer(
            f"Balansingiz yetarli emas!\n"
            f"Kerak: {price_som:,} so'm\n"
            f"Balans: {balance:,.0f} so'm", 
            show_alert=True
        )
        return
    
    await call.answer("Raqam olinmoqda...", show_alert=False)
    
    phone = None
    order_id = None
    
    # API ga qarab raqam olish
    if api_name == "smspva":
        try:
            result = smspva_api.get_number("opt1", price_data["country"])
            
            if "error" in result or result.get("response") == "2":
                error_msg = result.get("error", "Raqam mavjud emas")
                await call.message.edit_text(
                    f"Xatolik: {error_msg}\n\nBoshqa davlat tanlang.",
                    reply_markup=sms_telegram_countries_inline()
                )
                return
            
            phone = result.get("number", result.get("CountryCode", "") + result.get("number", ""))
            order_id = f"smspva_{result.get('id', '')}"
            
        except Exception as e:
            await call.message.edit_text(
                f"SMSPVA xatosi: {str(e)}\n\nBoshqa davlat tanlang.",
                reply_markup=sms_telegram_countries_inline()
            )
            return
    
    elif api_name == "fivesim":
        # 5SIM API
        try:
            result = fivesim_api.buy_number(price_data["country"], "telegram")
            
            if "error" in result:
                await call.message.edit_text(
                    f"Xatolik: {result['error']}\n\nBoshqa davlat tanlang.",
                    reply_markup=sms_telegram_countries_inline()
                )
                return
            
            phone = result.get("phone", "")
            order_id = f"fivesim_{result.get('id', '')}"
            
        except Exception as e:
            await call.message.edit_text(
                f"5SIM xatosi: {str(e)}\n\nBoshqa davlat tanlang.",
                reply_markup=sms_telegram_countries_inline()
            )
            return
    
    else:
        # VAK-SMS API
        try:
            result = vaksms_api.get_number("tg", country_code)
            
            if "error" in result:
                await call.message.edit_text(
                    f"Xatolik: {result['error']}\n\nBoshqa davlat tanlang.",
                    reply_markup=sms_telegram_countries_inline()
                )
                return
            
            phone = result.get("tel", result.get("number", ""))
            order_id = f"vaksms_{result.get('idNum', result.get('id', ''))}"
            
        except Exception as e:
            await call.message.edit_text(
                f"VAK-SMS xatosi: {str(e)}\n\nBoshqa davlat tanlang.",
                reply_markup=sms_telegram_countries_inline()
            )
            return
    
    if not phone or not order_id:
        await call.message.edit_text(
            "Raqam olishda xatolik. Keyinroq urinib ko'ring.",
            reply_markup=sms_telegram_countries_inline()
        )
        return
    
    # Balansdan yechish
    update_balance(user_id, -price_som)
    new_balance = get_balance(user_id)
    
    # Ma'lumotlarni saqlash
    await state.update_data(
        sms_order_id=order_id,
        sms_phone=phone,
        sms_price=price_som,
        sms_platform="telegram",
        sms_country=country_code,
        sms_api=api_name
    )
    
    country_name = price_data["country_name"]
    
    text = "RAQAM TAYYOR!\n"
    text += "=" * 30 + "\n\n"
    text += f"Raqam: +{phone}\n"
    text += f"Davlat: {country_name}\n"
    text += f"Platform: Telegram\n"
    text += f"Narxi: {price_som:,} so'm\n"
    text += f"Qoldi: {new_balance:,.0f} so'm\n\n"
    text += "-" * 30 + "\n"
    text += "SMS kutilmoqda...\n\n"
    text += "Raqamni Telegram'ga kiriting\n"
    text += "va SMS kod kelishini kuting."
    
    await call.message.edit_text(text, reply_markup=sms_waiting_inline(order_id))


# ==================== BOSHQA PLATFORMALAR ====================

@sms_router.callback_query(F.data.in_({"sms_ig", "sms_wa", "sms_go", "sms_tt", "sms_fb", "sms_tw", "sms_ds"}))
async def sms_other_platform(call: CallbackQuery, state: FSMContext):
    """Boshqa platformalar - davlatlar menyusi"""
    service_code = call.data.replace("sms_", "")
    
    platform_names = {
        "ig": "Instagram",
        "wa": "WhatsApp", 
        "go": "Google",
        "tt": "TikTok",
        "fb": "Facebook",
        "tw": "Twitter",
        "ds": "Discord"
    }
    
    platform_name = platform_names.get(service_code, service_code.upper())
    
    user_id = call.from_user.id
    balance = get_balance(user_id)
    
    text = f"{platform_name.upper()} VIRTUAL RAQAMLAR\n"
    text += "=" * 30 + "\n\n"
    text += f"Balansingiz: {balance:,.0f} so'm\n\n"
    text += "Davlatni tanlang:\n"
    
    await state.update_data(sms_platform=service_code, sms_platform_name=platform_name)
    
    try:
        await call.message.edit_text(text, reply_markup=sms_countries_inline(service_code))
    except TelegramBadRequest:
        pass
    await call.answer()


@sms_router.callback_query(F.data.startswith("country_"))
async def buy_other_number(call: CallbackQuery, state: FSMContext):
    """Boshqa platformalar uchun raqam sotib olish"""
    # Format: country_ig_ru
    parts = call.data.split("_")
    if len(parts) < 3:
        await call.answer("Xatolik", show_alert=True)
        return
    
    service_code = parts[1]
    country_code = parts[2]
    
    user_id = call.from_user.id
    balance = get_balance(user_id)
    
    # VAK-SMS dan narx olish
    price_rub = vaksms_api.get_price(service_code, country_code)
    
    if not price_rub or price_rub <= 0:
        await call.answer("Bu davlatda raqam mavjud emas", show_alert=True)
        return
    
    # Dinamik kurs va ustama
    rub_rate = get_rub_rate()
    markup = 1 + (get_markup_percent() / 100)
    price_som = int(price_rub * rub_rate * markup)
    
    # Balans tekshirish
    if balance < price_som:
        await call.answer(
            f"Balansingiz yetarli emas!\n"
            f"Kerak: {price_som:,} so'm\n"
            f"Balans: {balance:,.0f} so'm", 
            show_alert=True
        )
        return
    
    await call.answer("Raqam olinmoqda...", show_alert=False)
    
    # Raqam sotib olish
    result = vaksms_api.get_number(service_code, country_code)
    
    if "error" in result:
        await call.message.edit_text(
            f"Xatolik: {result['error']}\n\nBoshqa davlat tanlang.",
            reply_markup=sms_countries_inline(service_code)
        )
        return
    
    phone = result.get("tel", result.get("number", ""))
    order_id = f"vaksms_{result.get('idNum', result.get('id', ''))}"
    
    if not phone or not order_id:
        await call.message.edit_text(
            "Raqam olishda xatolik. Keyinroq urinib ko'ring.",
            reply_markup=sms_countries_inline(service_code)
        )
        return
    
    # Balansdan yechish
    update_balance(user_id, -price_som)
    new_balance = get_balance(user_id)
    
    # Ma'lumotlarni saqlash
    data = await state.get_data()
    platform_name = data.get("sms_platform_name", service_code.upper())
    
    await state.update_data(
        sms_order_id=order_id,
        sms_phone=phone,
        sms_price=price_som,
        sms_api="vaksms"
    )
    
    country_names = {
        "ru": "Rossiya",
        "uz": "O'zbekiston",
        "id": "Indoneziya",
        "ph": "Filippin",
        "vn": "Vetnam",
        "kz": "Qozog'iston"
    }
    country_name = country_names.get(country_code, country_code.upper())
    
    text = "RAQAM TAYYOR!\n"
    text += "=" * 30 + "\n\n"
    text += f"Raqam: +{phone}\n"
    text += f"Davlat: {country_name}\n"
    text += f"Platform: {platform_name}\n"
    text += f"Narxi: {price_som:,} so'm\n"
    text += f"Qoldi: {new_balance:,.0f} so'm\n\n"
    text += "-" * 30 + "\n"
    text += "SMS kutilmoqda...\n\n"
    text += f"Raqamni {platform_name}'ga kiriting\n"
    text += "va SMS kod kelishini kuting."
    
    await call.message.edit_text(text, reply_markup=sms_waiting_inline(order_id))


# ==================== SMS TEKSHIRISH ====================

@sms_router.callback_query(F.data.startswith("sms_check_"))
async def check_sms_code(call: CallbackQuery, state: FSMContext):
    """SMS kodini tekshirish"""
    order_id = call.data.replace("sms_check_", "")
    sms_code = None
    
    # API aniqlash
    if order_id.startswith("smspva_"):
        real_id = order_id.replace("smspva_", "")
        result = smspva_api.get_sms(real_id)
        
        if result.get("response") == "1":
            sms_code = result.get("sms", result.get("text", ""))
    
    elif order_id.startswith("fivesim_"):
        real_id = order_id.replace("fivesim_", "")
        result = fivesim_api.check_order(real_id)
        
        if result.get("sms"):
            sms_list = result.get("sms", [])
            if sms_list and len(sms_list) > 0:
                sms_code = sms_list[0].get("code", sms_list[0].get("text", ""))
    
    else:
        real_id = order_id.replace("vaksms_", "")
        result = vaksms_api.get_sms(real_id)
        sms_code = result.get("sms")
    
    if sms_code:
        # SMS olindi
        data = await state.get_data()
        phone = data.get("sms_phone", "")
        
        text = "SMS KOD OLINDI!\n"
        text += "=" * 30 + "\n\n"
        text += f"Raqam: +{phone}\n"
        text += f"Kod: {sms_code}\n\n"
        text += "-" * 30 + "\n"
        text += "Koddan foydalaning va\n"
        text += "'Yakunlash' tugmasini bosing."
        
        await call.message.edit_text(text, reply_markup=sms_received_inline(order_id))
    else:
        await call.answer("SMS hali kelmadi. Kuting...", show_alert=True)


# ==================== BEKOR QILISH ====================

@sms_router.callback_query(F.data.startswith("sms_cancel_"))
async def cancel_sms_order(call: CallbackQuery, state: FSMContext):
    """Raqamni bekor qilish"""
    order_id = call.data.replace("sms_cancel_", "")
    success = False
    
    # API aniqlash
    if order_id.startswith("smspva_"):
        real_id = order_id.replace("smspva_", "")
        result = smspva_api.cancel_number(real_id)
        success = result.get("response") == "1"
    
    elif order_id.startswith("fivesim_"):
        real_id = order_id.replace("fivesim_", "")
        result = fivesim_api.cancel_order(real_id)
        success = "error" not in result
    else:
        real_id = order_id.replace("vaksms_", "")
        result = vaksms_api.cancel_number(real_id)
        success = "error" not in result
    
    if success:
        # Pulni qaytarish
        data = await state.get_data()
        price = data.get("sms_price", 0)
        
        if price > 0:
            user_id = call.from_user.id
            update_balance(user_id, price)
            
            text = "BEKOR QILINDI\n"
            text += "=" * 30 + "\n\n"
            text += f"{price:,} so'm qaytarildi.\n"
            text += "Yangi raqam olishingiz mumkin."
        else:
            text = "Buyurtma bekor qilindi."
        
        await state.clear()
        await call.message.edit_text(text, reply_markup=sms_platforms_inline())
    else:
        await call.answer("Bekor qilishda xatolik", show_alert=True)


# ==================== YAKUNLASH ====================

@sms_router.callback_query(F.data.startswith("sms_finish_"))
async def finish_sms_order(call: CallbackQuery, state: FSMContext):
    """Raqamni yakunlash"""
    order_id = call.data.replace("sms_finish_", "")
    
    # API aniqlash
    if order_id.startswith("smspva_"):
        real_id = order_id.replace("smspva_", "")
        smspva_api.finish_number(real_id)
    elif order_id.startswith("fivesim_"):
        real_id = order_id.replace("fivesim_", "")
        fivesim_api.finish_order(real_id)
    else:
        real_id = order_id.replace("vaksms_", "")
        vaksms_api.finish_number(real_id)
    
    await state.clear()
    
    text = "BUYURTMA YAKUNLANDI\n"
    text += "=" * 30 + "\n\n"
    text += "Xizmatimizdan foydalanganingiz\n"
    text += "uchun rahmat!\n\n"
    text += "Yangi raqam kerakmi?"
    
    await call.message.edit_text(text, reply_markup=sms_platforms_inline())
    await call.answer("Yakunlandi!")


# ==================== YANA SMS ====================

@sms_router.callback_query(F.data.startswith("sms_resend_"))
async def resend_sms_request(call: CallbackQuery, state: FSMContext):
    """Yana SMS so'rash"""
    await call.answer("Platformada SMS ni qayta so'rang", show_alert=True)
