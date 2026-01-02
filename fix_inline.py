# -*- coding: utf-8 -*-
"""Inline query ni tuzatish"""

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Eski kodni topish va yangilash
old_code = '''    text += "💰 Ro'yxatdan o'ting va <b>BONUS</b> oling!\\n\\n"
    text += "👇 Quyidagi tugmani bosing va boshlang!"
    
    results = [
        InlineQueryResultArticle(
            id="referral_invite",
            title="🎁 Do'stni taklif qilish",
            description="Do'stingizga SMM Xizmatlari botini tavsiya qiling",
            thumbnail_url="https://i.imgur.com/YxKJH3M.png",
            input_message_content=InputTextMessageContent(
                message_text=text,
                parse_mode="HTML"
            ),
            reply_markup=referral_join_inline(bot_info.username, str(user_id))
        )
    ]
    
    await query.answer(results, cache_time=60, is_personal=True)'''

new_code = '''    text += "💰 Ro'yxatdan o'ting va <b>BONUS</b> oling!\\n\\n"
    text += "👇 Quyidagi tugmani bosing va boshlang!"
    
    # Bot profil rasmini olish
    try:
        photos = await bot.get_user_profile_photos(bot_info.id, limit=1)
        if photos.photos and len(photos.photos) > 0:
            photo = photos.photos[0][-1]
            file = await bot.get_file(photo.file_id)
            thumb_url = f"https://api.telegram.org/file/bot{bot.token}/{file.file_path}"
        else:
            thumb_url = "https://i.imgur.com/YxKJH3M.png"
    except:
        thumb_url = "https://i.imgur.com/YxKJH3M.png"
    
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
    
    await query.answer(results, cache_time=10, is_personal=True)'''

# Buzilgan emoji bilan ham qidirish
old_code_broken = old_code.replace('💰', '�')

if old_code in content:
    content = content.replace(old_code, new_code)
    print("Topildi va almashtirildi (normal emoji)")
elif old_code_broken in content:
    content = content.replace(old_code_broken, new_code)
    print("Topildi va almashtirildi (buzilgan emoji)")
else:
    print("Topilmadi! Qo'lda qidirish kerak")
    # Qatorlarni tekshirish
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'cache_time=60' in line and 'query.answer' in line:
            print(f"Line {i+1}: {line}")

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Tayyor!")
