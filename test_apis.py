# -*- coding: utf-8 -*-
"""
API TEKSHIRISH SKRIPTI
Barcha SMM va SMS API'larni tekshiradi
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("🔍 API XIZMATLARI TEKSHIRUVI")
print("=" * 60)

# ==================== 1. SMM PANEL - PEAKERR ====================
print("\n📦 1. PEAKERR SMM PANEL")
print("-" * 40)

SMM_API_URL = os.getenv("SMM_API_URL", "https://peakerr.com/api/v2")
SMM_API_KEY = os.getenv("SMM_API_KEY", "")

if SMM_API_KEY:
    import requests
    try:
        # Balansni tekshirish
        response = requests.post(SMM_API_URL, data={
            'key': SMM_API_KEY,
            'action': 'balance'
        }, timeout=10)
        result = response.json()
        
        if 'balance' in result:
            print(f"✅ Peakerr ishlayapti!")
            print(f"   💰 Balans: ${result['balance']}")
            print(f"   💵 Valyuta: {result.get('currency', 'USD')}")
        elif 'error' in result:
            print(f"❌ Xatolik: {result['error']}")
        else:
            print(f"⚠️ Noma'lum javob: {result}")
            
        # Xizmatlar sonini tekshirish
        response = requests.post(SMM_API_URL, data={
            'key': SMM_API_KEY,
            'action': 'services'
        }, timeout=15)
        services = response.json()
        if isinstance(services, list):
            print(f"   📊 Xizmatlar soni: {len(services)}")
        
    except Exception as e:
        print(f"❌ Peakerr xatolik: {e}")
else:
    print("⚠️ SMM_API_KEY sozlanmagan")


# ==================== 2. SMM PANEL - SMMMAIN ====================
print("\n📦 2. SMMMAIN SMM PANEL")
print("-" * 40)

SMMMAIN_API_URL = os.getenv("SMMMAIN_API_URL", "https://smmmain.com/api/v2")
SMMMAIN_API_KEY = os.getenv("SMMMAIN_API_KEY", "")

if SMMMAIN_API_KEY:
    try:
        response = requests.post(SMMMAIN_API_URL, data={
            'key': SMMMAIN_API_KEY,
            'action': 'balance'
        }, timeout=10)
        result = response.json()
        
        if 'balance' in result:
            print(f"✅ SMMMain ishlayapti!")
            print(f"   💰 Balans: ${result['balance']}")
            print(f"   💵 Valyuta: {result.get('currency', 'USD')}")
        elif 'error' in result:
            print(f"❌ Xatolik: {result['error']}")
        else:
            print(f"⚠️ Noma'lum javob: {result}")
            
        # Xizmatlar sonini tekshirish
        response = requests.post(SMMMAIN_API_URL, data={
            'key': SMMMAIN_API_KEY,
            'action': 'services'
        }, timeout=15)
        services = response.json()
        if isinstance(services, list):
            print(f"   📊 Xizmatlar soni: {len(services)}")
            
    except Exception as e:
        print(f"❌ SMMMain xatolik: {e}")
else:
    print("⚠️ SMMMAIN_API_KEY sozlanmagan")


# ==================== 3. SMS - VAK-SMS.COM ====================
print("\n📱 3. VAK-SMS.COM (Virtual raqamlar)")
print("-" * 40)

SMS_API_KEY = os.getenv("SMS_API_KEY", "")

if SMS_API_KEY:
    try:
        response = requests.get(
            f"https://vak-sms.com/api/getBalance/?apiKey={SMS_API_KEY}",
            timeout=10
        )
        result = response.json()
        
        if 'balance' in result:
            print(f"✅ VAK-SMS ishlayapti!")
            print(f"   💰 Balans: {result['balance']} RUB")
        elif 'error' in result:
            print(f"❌ Xatolik: {result['error']}")
        else:
            print(f"⚠️ Noma'lum javob: {result}")
            
    except Exception as e:
        print(f"❌ VAK-SMS xatolik: {e}")
else:
    print("⚠️ SMS_API_KEY sozlanmagan")


# ==================== 4. SMS - 5SIM.NET ====================
print("\n📱 4. 5SIM.NET (Virtual raqamlar)")
print("-" * 40)

FIVESIM_API_KEY = os.getenv("FIVESIM_API_KEY", "")

if FIVESIM_API_KEY:
    try:
        response = requests.get(
            "https://5sim.net/v1/user/profile",
            headers={"Authorization": f"Bearer {FIVESIM_API_KEY}"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 5SIM ishlayapti!")
            print(f"   💰 Balans: {result.get('balance', 0)} RUB")
            print(f"   📧 Email: {result.get('email', 'N/A')}")
        elif response.status_code == 401:
            print(f"❌ API key noto'g'ri yoki muddati o'tgan")
        else:
            print(f"❌ Xatolik: Status {response.status_code}")
            
    except Exception as e:
        print(f"❌ 5SIM xatolik: {e}")
else:
    print("⚠️ FIVESIM_API_KEY sozlanmagan")


# ==================== 5. SMS - SMSPVA.COM ====================
print("\n📱 5. SMSPVA.COM (Virtual raqamlar - eng arzon)")
print("-" * 40)

SMSPVA_API_KEY = os.getenv("SMSPVA_API_KEY", "")

if SMSPVA_API_KEY:
    try:
        response = requests.get(
            f"https://smspva.com/priemnik.php?metod=get_balance&apikey={SMSPVA_API_KEY}",
            timeout=10
        )
        result = response.json()
        
        if result.get('response') == '1':
            print(f"✅ SMSPVA ishlayapti!")
            print(f"   💰 Balans: {result.get('balance', 0)} RUB")
        elif result.get('response') == '2':
            print(f"❌ API key noto'g'ri")
        else:
            print(f"⚠️ Javob: {result}")
            
    except Exception as e:
        print(f"❌ SMSPVA xatolik: {e}")
else:
    print("⚠️ SMSPVA_API_KEY sozlanmagan")


# ==================== 6. CLICK TO'LOV ====================
print("\n💳 6. CLICK TO'LOV TIZIMI")
print("-" * 40)

CLICK_MERCHANT_ID = os.getenv("CLICK_MERCHANT_ID", "")
CLICK_SERVICE_ID = os.getenv("CLICK_SERVICE_ID", "")
CLICK_SECRET_KEY = os.getenv("CLICK_SECRET_KEY", "")

if CLICK_MERCHANT_ID and CLICK_SERVICE_ID and CLICK_SECRET_KEY:
    print(f"✅ Click sozlangan!")
    print(f"   🏪 Merchant ID: {CLICK_MERCHANT_ID}")
    print(f"   🔧 Service ID: {CLICK_SERVICE_ID}")
    print(f"   🔑 Secret Key: {'*' * 10}")
else:
    print("⚠️ Click to'liq sozlanmagan:")
    if not CLICK_MERCHANT_ID:
        print("   ❌ CLICK_MERCHANT_ID yo'q")
    if not CLICK_SERVICE_ID:
        print("   ❌ CLICK_SERVICE_ID yo'q")
    if not CLICK_SECRET_KEY:
        print("   ❌ CLICK_SECRET_KEY yo'q")


# ==================== XULOSA ====================
print("\n" + "=" * 60)
print("📋 XULOSA")
print("=" * 60)

api_status = {
    "Peakerr SMM": bool(SMM_API_KEY),
    "SMMMain SMM": bool(SMMMAIN_API_KEY),
    "VAK-SMS": bool(SMS_API_KEY),
    "5SIM": bool(FIVESIM_API_KEY),
    "SMSPVA": bool(SMSPVA_API_KEY),
    "Click": bool(CLICK_MERCHANT_ID and CLICK_SERVICE_ID and CLICK_SECRET_KEY),
}

active = sum(1 for v in api_status.values() if v)
total = len(api_status)

print(f"\n✅ Faol API'lar: {active}/{total}")
print()
for name, status in api_status.items():
    icon = "✅" if status else "❌"
    print(f"   {icon} {name}")

print("\n" + "=" * 60)
