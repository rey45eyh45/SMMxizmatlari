# -*- coding: utf-8 -*-
"""
KEYBOARDS - Aiogram 3.x uchun klaviaturalar
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

# Mini App URL - deploy qilgandan so'ng o'zgartiring
MINI_APP_URL = "https://hearty-curiosity-production.up.railway.app"


# ==================== REPLY KEYBOARDS ====================

def main_menu():
    """Asosiy menyu"""
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="📁 Xizmatlar"))
    builder.row(
        KeyboardButton(text="🔍 Buyurtmalarim"),
        KeyboardButton(text="🗣 Referal")
    )
    builder.row(
        KeyboardButton(text="💰 Mening hisobim"),
        KeyboardButton(text="💵 Hisob to'ldirish")
    )
    # Mini App tugmasi
    builder.row(KeyboardButton(
        text="📱 Mini App ochish", 
        web_app=WebAppInfo(url=MINI_APP_URL)
    ))
    return builder.as_markup(resize_keyboard=True)


def social_networks_menu():
    """Ijtimoiy tarmoqlar"""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="✈️ Telegram"),
        KeyboardButton(text="📸 Instagram")
    )
    builder.row(
        KeyboardButton(text="▶️ Youtube"),
        KeyboardButton(text="🎵 Tik-Tok")
    )
    builder.row(KeyboardButton(text="📱 Virtual raqamlar"))
    builder.row(KeyboardButton(text="⬅️ Orqaga"))
    return builder.as_markup(resize_keyboard=True)


def cancel_button():
    """Bekor qilish"""
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="❌ Bekor qilish"))
    return builder.as_markup(resize_keyboard=True)


def payment_methods():
    """To'lov usullari"""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="💳 Karta orqali"),
        KeyboardButton(text="💳 Click")
    )
    builder.row(
        KeyboardButton(text="💳 Payme"),
        KeyboardButton(text="💳 Uzum")
    )
    builder.row(KeyboardButton(text="⬅️ Orqaga"))
    return builder.as_markup(resize_keyboard=True)


def admin_main_menu():
    """Admin panel - Professional menyu"""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="📊 Statistika"),
        KeyboardButton(text="📋 Buyurtmalar")
    )
    builder.row(
        KeyboardButton(text="👥 Foydalanuvchilar"),
        KeyboardButton(text="💳 To'lovlar")
    )
    builder.row(
        KeyboardButton(text="📢 Xabar yuborish"),
        KeyboardButton(text="💰 Balans boshqarish")
    )
    builder.row(
        KeyboardButton(text="💾 Zaxira nusxa"),
        KeyboardButton(text="⚙️ Sozlamalar")
    )
    return builder.as_markup(resize_keyboard=True)


# ==================== INLINE KEYBOARDS ====================

def telegram_services_inline():
    """Telegram xizmatlari - Asosiy menyu"""
    builder = InlineKeyboardBuilder()
    # 1-qator: Premium obuna olish
    builder.row(InlineKeyboardButton(text="⭐ Premium obuna olish", callback_data="buy_premium_menu"))
    # 2-qator: Obunachi turlari
    builder.row(
        InlineKeyboardButton(text="👥 Obunachi", callback_data="tg_members_menu"),
        InlineKeyboardButton(text="💎 Premium obunachi", callback_data="tg_subscriber_premium")
    )
    # 3-qator: Ko'rish va Reaksiya
    builder.row(
        InlineKeyboardButton(text="👁 Ko'rish", callback_data="tg_views_menu"),
        InlineKeyboardButton(text="👍 Reaksiya", callback_data="tg_reactions_menu")
    )
    # 4-qator: Boshqa xizmatlar
    builder.row(InlineKeyboardButton(text="🗂️ Boshqa xizmatlar", callback_data="tg_other_menu"))
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_services"))
    return builder.as_markup()


def telegram_members_inline():
    """Telegram Obunachi xizmatlari - faqat oddiy obunachi (16 ta)"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="━━━ 👥 OBUNACHI (Arzondan qimmatga) ━━━", callback_data="section_tg"))
    builder.row(InlineKeyboardButton(text="👥 Eng arzon | 1,201 so'm 🔥", callback_data="tg_member_1"))
    builder.row(InlineKeyboardButton(text="👥 Mix 700K | 6,824 so'm", callback_data="tg_member_2"))
    builder.row(InlineKeyboardButton(text="👥 No Limit | 7,328 so'm", callback_data="tg_member_3"))
    builder.row(InlineKeyboardButton(text="👥 30 kun R30 | 7,878 so'm", callback_data="tg_member_4"))
    builder.row(InlineKeyboardButton(text="👥 30 kun kafolat | 8,752 so'm", callback_data="tg_member_5"))
    builder.row(InlineKeyboardButton(text="👥 60 kun kafolat | 9,494 so'm", callback_data="tg_member_6"))
    builder.row(InlineKeyboardButton(text="👥 50K NonDrop | 9,494 so'm", callback_data="tg_member_7"))
    builder.row(InlineKeyboardButton(text="👥 Real R60 | 10,236 so'm", callback_data="tg_member_8"))
    builder.row(InlineKeyboardButton(text="👥 90 kun kafolat | 10,236 so'm", callback_data="tg_member_9"))
    builder.row(InlineKeyboardButton(text="👥 NonDrop 50K | 13,203 so'm", callback_data="tg_member_10"))
    builder.row(InlineKeyboardButton(text="👥 High Quality | 14,686 so'm", callback_data="tg_member_11"))
    builder.row(InlineKeyboardButton(text="👥 No Drop 100K | 17,453 so'm", callback_data="tg_member_12"))
    builder.row(InlineKeyboardButton(text="👥 Non Drop 100K | 18,138 so'm", callback_data="tg_member_13"))
    builder.row(InlineKeyboardButton(text="👥 Zero Drop 60 kun | 18,988 so'm", callback_data="tg_member_14"))
    builder.row(InlineKeyboardButton(text="👥 100% Real | 20,027 so'm", callback_data="tg_member_16"))
    builder.row(InlineKeyboardButton(text="👥 270 kun kafolat | 20,211 so'm", callback_data="tg_member_15"))
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_telegram"))
    return builder.as_markup()


def buy_premium_inline():
    """Premium obuna sotib olish menyusi"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="━━━━ ⭐ PREMIUM TARIFLAR ━━━━", callback_data="section_premium"))
    builder.row(InlineKeyboardButton(text="📅 1 oylik — 52,000 so'm", callback_data="select_premium_1"))
    builder.row(InlineKeyboardButton(text="📅 3 oylik — 156,000 so'm", callback_data="select_premium_3"))
    builder.row(InlineKeyboardButton(text="📅 6 oylik — 270,000 so'm 🔥", callback_data="select_premium_6"))
    builder.row(InlineKeyboardButton(text="📅 1 yillik — 415,000 so'm 💎", callback_data="select_premium_12"))
    builder.row(InlineKeyboardButton(text="━━━━━━━━━━━━━━━━━━━━━", callback_data="section_premium"))
    builder.row(InlineKeyboardButton(text="❓ Premium nima?", callback_data="premium_info"))
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_telegram"))
    return builder.as_markup()


def premium_confirm_inline(months: int, price: int):
    """Premium sotib olishni tasdiqlash"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=f"✅ Ha, {price:,} so'm to'layman", callback_data=f"confirm_premium_{months}"))
    builder.row(InlineKeyboardButton(text="❌ Bekor qilish", callback_data="buy_premium_menu"))
    return builder.as_markup()


def phone_request_keyboard():
    """Telefon raqam so'rash tugmasi"""
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Telefon raqamimni ulashish", request_contact=True)],
            [KeyboardButton(text="❌ Bekor qilish")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


def premium_admin_inline(user_id: int, months: int, price: int, request_id: int):
    """Admin uchun premium so'rovni tasdiqlash"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"approve_premium_{request_id}"),
        InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_premium_{request_id}")
    )
    return builder.as_markup()


def telegram_premium_members_inline():
    """Telegram Premium Obunachi xizmatlari - alohida (4 ta)"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="━━━ ⭐ PREMIUM OBUNACHI ━━━", callback_data="section_tg"))
    builder.row(InlineKeyboardButton(text="⭐ Premium 7-14 kun | 44,356 so'm", callback_data="tg_member_premium_1"))
    builder.row(InlineKeyboardButton(text="⭐ Premium 15-30 kun | 88,861 so'm", callback_data="tg_member_premium_2"))
    builder.row(InlineKeyboardButton(text="⭐ Premium New | 136,927 so'm", callback_data="tg_member_premium_3"))
    builder.row(InlineKeyboardButton(text="⭐ Premium ZeroDrop | 136,927 so'm", callback_data="tg_member_premium_4"))
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_telegram"))
    return builder.as_markup()


def telegram_views_inline():
    """Telegram Ko'rish xizmatlari - 11 ta xizmat"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="━━━ 👁 KO'RISH (Arzondan qimmatga) ━━━", callback_data="section_tg"))
    builder.row(InlineKeyboardButton(text="👁 1 Post Eng arzon | 38 so'm 🔥", callback_data="tg_view_1"))
    builder.row(InlineKeyboardButton(text="👁 Super Fast 50M | 59 so'm", callback_data="tg_view_2"))
    builder.row(InlineKeyboardButton(text="👁 Instant 100M | 59 so'm", callback_data="tg_view_3"))
    builder.row(InlineKeyboardButton(text="👁 Speed 20K/soat | 59 so'm", callback_data="tg_view_4"))
    builder.row(InlineKeyboardButton(text="👁 Last 1 Post 500K | 59 so'm", callback_data="tg_view_5"))
    builder.row(InlineKeyboardButton(text="👁 USA Lifetime | 59 so'm", callback_data="tg_view_6"))
    builder.row(InlineKeyboardButton(text="👁 Story | 1,349 so'm", callback_data="tg_view_7"))
    builder.row(InlineKeyboardButton(text="👁 Last 20 Post | 1,832 so'm", callback_data="tg_view_8"))
    builder.row(InlineKeyboardButton(text="👁 Last 50 Post | 2,170 so'm", callback_data="tg_view_9"))
    builder.row(InlineKeyboardButton(text="👁 Last 20 Post v2 | 2,189 so'm", callback_data="tg_view_10"))
    builder.row(InlineKeyboardButton(text="⭐ Premium Story | 1,349 so'm", callback_data="tg_view_11"))
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_telegram"))
    return builder.as_markup()


def telegram_reactions_inline():
    """Telegram Reaksiya xizmatlari - 19 ta xizmat"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="━━━ 👍 REAKSIYA (Arzondan qimmatga) ━━━", callback_data="section_tg"))
    builder.row(InlineKeyboardButton(text="👍 Auto Pozitiv | 250 so'm 🔥", callback_data="tg_react_1"))
    builder.row(InlineKeyboardButton(text="👍 Pozitiv + Views | 578 so'm", callback_data="tg_react_2"))
    builder.row(InlineKeyboardButton(text="👍 Pozitiv + Views v2 | 916 so'm", callback_data="tg_react_3"))
    builder.row(InlineKeyboardButton(text="🐳 Premium Whale | 1,302 so'm", callback_data="tg_react_4"))
    builder.row(InlineKeyboardButton(text="🍓 Premium Strawberry | 1,302 so'm", callback_data="tg_react_5"))
    builder.row(InlineKeyboardButton(text="━━━ 🎭 EMOJI REAKSIYALAR ━━━", callback_data="section_tg"))
    builder.row(InlineKeyboardButton(text="👍 Like | 1,483 so'm", callback_data="tg_react_7"))
    builder.row(InlineKeyboardButton(text="❤️ Heart | 1,483 so'm", callback_data="tg_react_8"))
    builder.row(InlineKeyboardButton(text="🔥 Fire | 1,483 so'm", callback_data="tg_react_9"))
    builder.row(InlineKeyboardButton(text="🎉 Party | 1,483 so'm", callback_data="tg_react_10"))
    builder.row(InlineKeyboardButton(text="🤩 Star-Struck | 1,483 so'm", callback_data="tg_react_11"))
    builder.row(InlineKeyboardButton(text="👎 Dislike | 1,483 so'm", callback_data="tg_react_12"))
    builder.row(InlineKeyboardButton(text="😢 Cry | 1,483 so'm", callback_data="tg_react_13"))
    builder.row(InlineKeyboardButton(text="💩 Poo | 1,483 so'm", callback_data="tg_react_14"))
    builder.row(InlineKeyboardButton(text="😱 Scream | 1,483 so'm", callback_data="tg_react_15"))
    builder.row(InlineKeyboardButton(text="😁 Smile | 1,483 so'm", callback_data="tg_react_16"))
    builder.row(InlineKeyboardButton(text="🤮 Vomit | 1,483 so'm", callback_data="tg_react_17"))
    builder.row(InlineKeyboardButton(text="🙏 Pray | 1,483 so'm", callback_data="tg_react_18"))
    builder.row(InlineKeyboardButton(text="🤬 Angry | 1,483 so'm", callback_data="tg_react_19"))
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_telegram"))
    return builder.as_markup()


def telegram_other_inline():
    """Telegram Boshqa xizmatlari - 5 ta xizmat"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="━━━ 🗂️ BOSHQA XIZMATLAR ━━━", callback_data="section_tg"))
    builder.row(InlineKeyboardButton(text="🔄 Share Real | 231 so'm 🔥", callback_data="tg_share_1"))
    builder.row(InlineKeyboardButton(text="🔄 Share Static | 899 so'm", callback_data="tg_share_2"))
    builder.row(InlineKeyboardButton(text="🔄 Share USA | 899 so'm", callback_data="tg_share_3"))
    builder.row(InlineKeyboardButton(text="🔄 Share India | 899 so'm", callback_data="tg_share_4"))
    builder.row(InlineKeyboardButton(text="📊 Vote/So'rovnoma | 5,029 so'm", callback_data="tg_vote_1"))
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_telegram"))
    return builder.as_markup()


def telegram_other_services_inline():
    """Telegram boshqa xizmatlari (eski)"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🇺🇿 O'zbek Obunachi | 3,704 so'm", callback_data="tg_subscriber_uzbek"))
    builder.row(InlineKeyboardButton(text="👁 So'nggi 10 Post Ko'rish | 44 so'm", callback_data="tg_view_last10"))
    builder.row(InlineKeyboardButton(text="🎭 Custom Reaksiya | 1,778 so'm", callback_data="tg_reaction_custom"))
    builder.row(InlineKeyboardButton(text="🔄 Share/Ulashish | 2,967 so'm", callback_data="tg_share"))
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_telegram"))
    return builder.as_markup()


def instagram_services_inline():
    """Instagram xizmatlari - Professional"""
    builder = InlineKeyboardBuilder()
    # Bo'lim: Follower
    builder.row(InlineKeyboardButton(text="━━━ 👥 FOLLOWER ━━━", callback_data="section_ig_fol"))
    builder.row(InlineKeyboardButton(text="👥 Follower | 6,968 so'm", callback_data="ig_follower"))
    builder.row(InlineKeyboardButton(text="⭐ Premium Follower | 11,856 so'm", callback_data="ig_follower_premium"))
    builder.row(InlineKeyboardButton(text="💎 Real Follower | 22,230 so'm", callback_data="ig_follower_real"))
    # Bo'lim: Like
    builder.row(InlineKeyboardButton(text="━━━ ❤️ LIKE ━━━", callback_data="section_ig_like"))
    builder.row(InlineKeyboardButton(text="❤️ Like | 2,030 so'm", callback_data="ig_like"))
    builder.row(InlineKeyboardButton(text="⭐ Premium Like | 3,704 so'm", callback_data="ig_like_premium"))
    # Bo'lim: Ko'rish
    builder.row(InlineKeyboardButton(text="━━━ 👁 KO'RISH ━━━", callback_data="section_ig_view"))
    builder.row(InlineKeyboardButton(text="👁 Video Ko'rish | 16 so'm", callback_data="ig_view"))
    builder.row(InlineKeyboardButton(text="🎬 Reels Ko'rish | 12 so'm", callback_data="ig_reel_view"))
    builder.row(InlineKeyboardButton(text="📱 Story Ko'rish | 44 so'm", callback_data="ig_story_view"))
    # Bo'lim: Comment
    builder.row(InlineKeyboardButton(text="━━━ 💬 COMMENT ━━━", callback_data="section_ig_com"))
    builder.row(InlineKeyboardButton(text="💬 Comment | 7,412 so'm", callback_data="ig_comment"))
    builder.row(InlineKeyboardButton(text="✏️ Custom Comment | 14,823 so'm", callback_data="ig_comment_custom"))
    # Bo'lim: Boshqa
    builder.row(InlineKeyboardButton(text="━━━ 📥 BOSHQA ━━━", callback_data="section_ig_other"))
    builder.row(InlineKeyboardButton(text="📥 Save/Saqlash | 2,967 so'm", callback_data="ig_save"))
    builder.row(InlineKeyboardButton(text="🔄 Share/Ulashish | 2,223 so'm", callback_data="ig_share"))
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_services"))
    return builder.as_markup()


def youtube_services_inline():
    """YouTube xizmatlari - Professional"""
    builder = InlineKeyboardBuilder()
    # Bo'lim: Subscriber
    builder.row(InlineKeyboardButton(text="━━━ 👥 SUBSCRIBER ━━━", callback_data="section_yt_sub"))
    builder.row(InlineKeyboardButton(text="👥 Subscriber | 2,223 so'm", callback_data="yt_subscriber"))
    builder.row(InlineKeyboardButton(text="⭐ Premium Subscriber | 5,189 so'm", callback_data="yt_subscriber_premium"))
    # Bo'lim: Ko'rish
    builder.row(InlineKeyboardButton(text="━━━ 👁 KO'RISH ━━━", callback_data="section_yt_view"))
    builder.row(InlineKeyboardButton(text="👁 Ko'rish | 623 so'm", callback_data="yt_view"))
    builder.row(InlineKeyboardButton(text="⚡ Tez Ko'rish | 1,186 so'm", callback_data="yt_view_fast"))
    builder.row(InlineKeyboardButton(text="⏱ 4000 Soat Ko'rish | 1,482 so'm", callback_data="yt_view_4000h"))
    # Bo'lim: Like
    builder.row(InlineKeyboardButton(text="━━━ 👍 LIKE ━━━", callback_data="section_yt_like"))
    builder.row(InlineKeyboardButton(text="👍 Like | 1,157 so'm", callback_data="yt_like"))
    builder.row(InlineKeyboardButton(text="⭐ Premium Like | 2,223 so'm", callback_data="yt_like_premium"))
    # Bo'lim: Comment
    builder.row(InlineKeyboardButton(text="━━━ 💬 COMMENT ━━━", callback_data="section_yt_com"))
    builder.row(InlineKeyboardButton(text="💬 Comment | 11,856 so'm", callback_data="yt_comment"))
    builder.row(InlineKeyboardButton(text="✏️ Custom Comment | 22,230 so'm", callback_data="yt_comment_custom"))
    # Bo'lim: Boshqa
    builder.row(InlineKeyboardButton(text="🔄 Share/Ulashish | 741 so'm", callback_data="yt_share"))
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_services"))
    return builder.as_markup()


def tiktok_services_inline():
    """TikTok xizmatlari - Professional"""
    builder = InlineKeyboardBuilder()
    # Bo'lim: Follower
    builder.row(InlineKeyboardButton(text="━━━ 👥 FOLLOWER ━━━", callback_data="section_tt_fol"))
    builder.row(InlineKeyboardButton(text="👥 Follower | 3,262 so'm", callback_data="tt_follower"))
    builder.row(InlineKeyboardButton(text="⭐ Premium Follower | 6,672 so'm", callback_data="tt_follower_premium"))
    # Bo'lim: Ko'rish
    builder.row(InlineKeyboardButton(text="━━━ 👁 KO'RISH ━━━", callback_data="section_tt_view"))
    builder.row(InlineKeyboardButton(text="👁 Ko'rish 🔥 | 3 so'm", callback_data="tt_view"))
    builder.row(InlineKeyboardButton(text="📺 Live Ko'rish | 297 so'm", callback_data="tt_view_live"))
    # Bo'lim: Like
    builder.row(InlineKeyboardButton(text="━━━ ❤️ LIKE ━━━", callback_data="section_tt_like"))
    builder.row(InlineKeyboardButton(text="❤️ Like | 326 so'm", callback_data="tt_like"))
    builder.row(InlineKeyboardButton(text="⭐ Premium Like | 741 so'm", callback_data="tt_like_premium"))
    # Bo'lim: Comment
    builder.row(InlineKeyboardButton(text="━━━ 💬 COMMENT ━━━", callback_data="section_tt_com"))
    builder.row(InlineKeyboardButton(text="💬 Comment | 8,895 so'm", callback_data="tt_comment"))
    builder.row(InlineKeyboardButton(text="✏️ Custom Comment | 17,790 so'm", callback_data="tt_comment_custom"))
    # Bo'lim: Boshqa
    builder.row(InlineKeyboardButton(text="━━━ 📥 BOSHQA ━━━", callback_data="section_tt_other"))
    builder.row(InlineKeyboardButton(text="🔄 Share/Ulashish | 445 so'm", callback_data="tt_share"))
    builder.row(InlineKeyboardButton(text="📥 Save/Saqlash | 593 so'm", callback_data="tt_save"))
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_services"))
    return builder.as_markup()


def payment_amounts():
    """To'lov summalari"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="5,000 so'm", callback_data="amount_5000"),
        InlineKeyboardButton(text="10,000 so'm", callback_data="amount_10000")
    )
    builder.row(
        InlineKeyboardButton(text="25,000 so'm", callback_data="amount_25000"),
        InlineKeyboardButton(text="50,000 so'm", callback_data="amount_50000")
    )
    builder.row(
        InlineKeyboardButton(text="100,000 so'm", callback_data="amount_100000"),
        InlineKeyboardButton(text="200,000 so'm", callback_data="amount_200000")
    )
    builder.row(InlineKeyboardButton(text="✏️ Boshqa summa", callback_data="amount_custom"))
    return builder.as_markup()


def confirm_order_inline():
    """Buyurtmani tasdiqlash"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm_order"),
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_order")
    )
    return builder.as_markup()


def cancel_payment_inline():
    """To'lovni bekor qilish"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_payment"))
    return builder.as_markup()


def payment_approve_inline(user_id, amount):
    """Admin to'lovni tasdiqlash"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"approve_{user_id}_{amount}")
    )
    builder.row(
        InlineKeyboardButton(text="⚠️ To'liq emas", callback_data=f"partial_{user_id}_{amount}"),
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"reject_{user_id}_{amount}")
    )
    return builder.as_markup()


def contact_admin_inline():
    """Admin bilan bog'lanish"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="👨‍💼 Admin bilan bog'lanish", url="https://t.me/manager_komilov")
    )
    return builder.as_markup()


def referral_share_inline(ref_link: str, bot_username: str):
    """Referal ulashish tugmasi"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="📤 Do'stlarga ulashish", 
            switch_inline_query=""
        )
    )
    return builder.as_markup()


def referral_join_inline(bot_username: str, ref_id: str):
    """Referal qo'shilish tugmasi - yuborilgan xabarga"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🟢 Qo'shilish", 
            url=f"https://t.me/{bot_username}?start=ref_{ref_id}"
        )
    )
    return builder.as_markup()


# ==================== SMS KEYBOARDS ====================

def sms_platforms_inline():
    """SMS platformalar - emojilar bilan"""
    builder = InlineKeyboardBuilder()
    # Narxlar: eng arzon narxdan
    builder.row(
        InlineKeyboardButton(text="✈️ Telegram (1,393+)", callback_data="sms_tg"),
        InlineKeyboardButton(text="📸 Instagram (155+)", callback_data="sms_ig")
    )
    builder.row(
        InlineKeyboardButton(text="💬 WhatsApp (3,192+)", callback_data="sms_wa"),
        InlineKeyboardButton(text="🔍 Google (500+)", callback_data="sms_go")
    )
    builder.row(
        InlineKeyboardButton(text="🎵 TikTok (1,000+)", callback_data="sms_tt"),
        InlineKeyboardButton(text="📘 Facebook (800+)", callback_data="sms_fb")
    )
    builder.row(
        InlineKeyboardButton(text="🐦 Twitter (600+)", callback_data="sms_tw"),
        InlineKeyboardButton(text="🎮 Discord (900+)", callback_data="sms_ds")
    )
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="sms_back"))
    return builder.as_markup()


def sms_telegram_countries_inline():
    """Telegram uchun davlatlar - haqiqiy narxlar bilan emojilar"""
    builder = InlineKeyboardBuilder()
    # SMSPVA - eng arzonlari
    builder.row(
        InlineKeyboardButton(text="🇻🇳 Vetnam - 1,393", callback_data="buy_sms_tg_smspva_vn"),
        InlineKeyboardButton(text="🇺🇿 O'zbekiston - 1,548", callback_data="buy_sms_tg_smspva_uz")
    )
    builder.row(
        InlineKeyboardButton(text="🇮🇩 Indoneziya - 2,016", callback_data="buy_sms_tg_vaksms_id"),
        InlineKeyboardButton(text="🇷🇺 Rossiya - 2,322", callback_data="buy_sms_tg_smspva_ru")
    )
    builder.row(
        InlineKeyboardButton(text="🇵🇭 Filippin - 2,688", callback_data="buy_sms_tg_vaksms_ph"),
        InlineKeyboardButton(text="🇨🇴 Kolumbiya - 3,405", callback_data="buy_sms_tg_smspva_co")
    )
    builder.row(
        InlineKeyboardButton(text="🇧🇩 Bangladesh - 4,644", callback_data="buy_sms_tg_smspva_bd"),
        InlineKeyboardButton(text="🇲🇾 Malayziya - 4,872", callback_data="buy_sms_tg_vaksms_my")
    )
    builder.row(
        InlineKeyboardButton(text="🇰🇿 Qozog'iston - 5,880", callback_data="buy_sms_tg_vaksms_kz"),
        InlineKeyboardButton(text="🇬🇧 Angliya - 8,359", callback_data="buy_sms_tg_smspva_gb")
    )
    # 5SIM variantlar
    builder.row(
        InlineKeyboardButton(text="🇮🇩 Indoneziya 5SIM - 8,400", callback_data="buy_sms_tg_fivesim_indonesia"),
        InlineKeyboardButton(text="🇵🇭 Filippin 5SIM - 15,679", callback_data="buy_sms_tg_fivesim_philippines")
    )
    builder.row(
        InlineKeyboardButton(text="🇬🇧 Angliya 5SIM - 18,480", callback_data="buy_sms_tg_fivesim_england"),
        InlineKeyboardButton(text="🇺🇿 O'zbekiston 5SIM - 20,160", callback_data="buy_sms_tg_fivesim_uzbekistan")
    )
    builder.row(
        InlineKeyboardButton(text="🇩🇪 Germaniya 5SIM - 57,120", callback_data="buy_sms_tg_fivesim_germany")
    )
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="sms_platforms"))
    return builder.as_markup()


def sms_countries_inline(service_code):
    """SMS davlatlar - emojilar bilan"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🇷🇺 Rossiya", callback_data=f"country_{service_code}_ru"),
        InlineKeyboardButton(text="🇺🇿 O'zbekiston", callback_data=f"country_{service_code}_uz")
    )
    builder.row(
        InlineKeyboardButton(text="🇮🇩 Indoneziya", callback_data=f"country_{service_code}_id"),
        InlineKeyboardButton(text="🇵🇭 Filippin", callback_data=f"country_{service_code}_ph")
    )
    builder.row(
        InlineKeyboardButton(text="🇻🇳 Vetnam", callback_data=f"country_{service_code}_vn"),
        InlineKeyboardButton(text="🇰🇿 Qozog'iston", callback_data=f"country_{service_code}_kz")
    )
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="sms_platforms"))
    return builder.as_markup()


def sms_waiting_inline(order_id):
    """SMS kutish"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔄 SMS tekshirish", callback_data=f"sms_check_{order_id}"))
    builder.row(
        InlineKeyboardButton(text="🔁 Yana SMS", callback_data=f"sms_resend_{order_id}"),
        InlineKeyboardButton(text="❌ Bekor", callback_data=f"sms_cancel_{order_id}")
    )
    return builder.as_markup()


def sms_received_inline(order_id):
    """SMS kod olindi"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="✅ Yakunlash", callback_data=f"sms_finish_{order_id}"))
    builder.row(InlineKeyboardButton(text="📱 Yangi raqam", callback_data="sms_platforms"))
    return builder.as_markup()
