# Ideal SMM Xizmatlari Telegram Bot

Bu bot ijtimoiy tarmoqlar uchun SMM xizmatlarini taqdim etadi.

## Xususiyatlar

- 📁 **Xizmatlar** - Telegram, Instagram, YouTube, TikTok uchun xizmatlar
- 🔍 **Buyurtmalarim** - Buyurtmalar tarixini ko'rish
- 🗣 **Referal** - Do'stlarni taklif qilish va bonus olish
- 💰 **Mening hisobim** - Balans va statistika
- 💵 **Hisob to'ldirish** - Click, Payme, Uzum Bank orqali
- 📕 **Qo'llanma** - Bot qo'llanmasi
- 🏛 **Qo'llab-quvvatlash** - Yordam olish

## O'rnatish

1. Python 3.8+ o'rnating

2. Kerakli kutubxonalarni o'rnating:

   ```bash
   pip install -r requirements.txt
   ```

3. `config.py` faylida sozlamalarni o'zgartiring:
   - `BOT_TOKEN` - @BotFather dan olingan token
   - `ADMIN_ID` - Sizning Telegram ID raqamingiz
   - `CHANNEL_USERNAME` - Kanal username

4. Botni ishga tushiring:

   ```bash
   python bot.py
   ```

## Admin buyruqlari

- `/confirm_<payment_id>_<user_id>_<amount>` - To'lovni tasdiqlash
- `/broadcast <xabar>` - Barcha foydalanuvchilarga xabar yuborish

## Fayl tuzilishi

```text
smm xizmatlari/
├── bot.py          # Asosiy bot kodi
├── config.py       # Sozlamalar
├── database.py     # Ma'lumotlar bazasi
├── keyboards.py    # Klaviaturalar
├── requirements.txt
└── README.md
```

## Sozlash

1. @BotFather dan yangi bot yarating
2. Bot tokenini `config.py` ga qo'shing
3. @userinfobot dan o'z ID raqamingizni oling
4. Kanal yarating va bot ni admin qiling
5. Botni ishga tushiring

## Xizmat narxlari (1000 ta uchun)

| Platform  | Xizmat     | Narx         |
| --------- | ---------- | ------------ |
| Telegram  | Obunachi   | 15,000 so'm  |
| Telegram  | Ko'rish    | 1,000 so'm   |
| Instagram | Follower   | 20,000 so'm  |
| Instagram | Like       | 5,000 so'm   |
| YouTube   | Subscriber | 50,000 so'm  |
| YouTube   | View       | 10,000 so'm  |
| TikTok    | Follower   | 25,000 so'm  |
| TikTok    | Like       | 5,000 so'm   |

---
Ideal SMM © 2024
