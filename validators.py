"""
Input Validation Module
=======================
Barcha foydalanuvchi kiritgan ma'lumotlarni tekshirish uchun funksiyalar.
"""

import re
import logging
from typing import Tuple, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# ==================== URL VALIDATION ====================

# Platform URL patternlari
URL_PATTERNS = {
    'instagram': [
        r'^https?://(www\.)?instagram\.com/[a-zA-Z0-9_.]+/?$',  # Profile
        r'^https?://(www\.)?instagram\.com/p/[a-zA-Z0-9_-]+/?$',  # Post
        r'^https?://(www\.)?instagram\.com/reel/[a-zA-Z0-9_-]+/?$',  # Reel
        r'^https?://(www\.)?instagram\.com/stories/[a-zA-Z0-9_.]+/[0-9]+/?$',  # Story
    ],
    'telegram': [
        r'^https?://(t\.me|telegram\.me)/[a-zA-Z0-9_]+/?$',  # Channel/Group
        r'^https?://(t\.me|telegram\.me)/[a-zA-Z0-9_]+/[0-9]+/?$',  # Post
        r'^@[a-zA-Z0-9_]{5,}$',  # Username
    ],
    'youtube': [
        r'^https?://(www\.)?youtube\.com/watch\?v=[a-zA-Z0-9_-]+',  # Video
        r'^https?://(www\.)?youtube\.com/shorts/[a-zA-Z0-9_-]+',  # Shorts
        r'^https?://(www\.)?youtube\.com/(c/|channel/|@)[a-zA-Z0-9_-]+',  # Channel
        r'^https?://youtu\.be/[a-zA-Z0-9_-]+',  # Short URL
    ],
    'tiktok': [
        r'^https?://(www\.)?tiktok\.com/@[a-zA-Z0-9_.]+/?$',  # Profile
        r'^https?://(www\.)?tiktok\.com/@[a-zA-Z0-9_.]+/video/[0-9]+',  # Video
        r'^https?://(vm\.)?tiktok\.com/[a-zA-Z0-9]+/?$',  # Short URL
    ],
    'twitter': [
        r'^https?://(www\.)?(twitter\.com|x\.com)/[a-zA-Z0-9_]+/?$',  # Profile
        r'^https?://(www\.)?(twitter\.com|x\.com)/[a-zA-Z0-9_]+/status/[0-9]+',  # Tweet
    ],
    'facebook': [
        r'^https?://(www\.)?facebook\.com/[a-zA-Z0-9.]+/?$',  # Profile/Page
        r'^https?://(www\.)?facebook\.com/[a-zA-Z0-9.]+/posts/[0-9]+',  # Post
        r'^https?://(www\.)?facebook\.com/photo',  # Photo
        r'^https?://(www\.)?facebook\.com/watch',  # Video
    ],
    'spotify': [
        r'^https?://open\.spotify\.com/(track|album|artist|playlist)/[a-zA-Z0-9]+',
    ],
    'threads': [
        r'^https?://(www\.)?threads\.net/@[a-zA-Z0-9_.]+',
    ],
}


def validate_url(url: str, platform: Optional[str] = None) -> Tuple[bool, str]:
    """
    URL ni tekshirish
    
    Args:
        url: Tekshiriladigan URL
        platform: Platforma nomi (ixtiyoriy)
    
    Returns:
        Tuple[bool, str]: (valid, error_message)
    """
    if not url:
        return False, "URL kiritilmagan"
    
    url = url.strip()
    
    # Asosiy URL validatsiyasi
    try:
        parsed = urlparse(url)
        if not parsed.scheme and not url.startswith('@'):
            # https:// qo'shib ko'ramiz
            url = 'https://' + url
            parsed = urlparse(url)
        
        # Username bo'lishi mumkin (Telegram uchun)
        if url.startswith('@'):
            if platform and platform.lower() == 'telegram':
                if re.match(r'^@[a-zA-Z0-9_]{5,}$', url):
                    return True, ""
            return False, "Noto'g'ri username formati"
        
        # URL sxemasi tekshirish
        if parsed.scheme not in ['http', 'https']:
            return False, "URL http:// yoki https:// bilan boshlanishi kerak"
        
        # Domain mavjudligini tekshirish
        if not parsed.netloc:
            return False, "Noto'g'ri URL formati"
            
    except Exception as e:
        logger.error(f"URL parse error: {e}")
        return False, "Noto'g'ri URL formati"
    
    # Platform-specific validatsiya
    if platform:
        platform_key = platform.lower()
        if platform_key in URL_PATTERNS:
            patterns = URL_PATTERNS[platform_key]
            for pattern in patterns:
                if re.match(pattern, url, re.IGNORECASE):
                    return True, ""
            return False, f"Bu {platform} uchun to'g'ri link emas"
    
    return True, ""


def detect_platform_from_url(url: str) -> Optional[str]:
    """
    URL dan platformani aniqlash
    """
    url = url.strip().lower()
    
    platform_domains = {
        'instagram': ['instagram.com'],
        'telegram': ['t.me', 'telegram.me'],
        'youtube': ['youtube.com', 'youtu.be'],
        'tiktok': ['tiktok.com', 'vm.tiktok.com'],
        'twitter': ['twitter.com', 'x.com'],
        'facebook': ['facebook.com', 'fb.com'],
        'spotify': ['spotify.com', 'open.spotify.com'],
        'threads': ['threads.net'],
    }
    
    for platform, domains in platform_domains.items():
        for domain in domains:
            if domain in url:
                return platform
    
    return None


# ==================== QUANTITY VALIDATION ====================

# Service limitlari
SERVICE_LIMITS = {
    'default': {'min': 10, 'max': 100000},
    'followers': {'min': 50, 'max': 100000},
    'likes': {'min': 10, 'max': 50000},
    'views': {'min': 100, 'max': 1000000},
    'comments': {'min': 5, 'max': 1000},
    'premium': {'min': 1, 'max': 1},
}


def validate_quantity(quantity: int, service_type: str = 'default') -> Tuple[bool, str]:
    """
    Miqdorni tekshirish
    
    Args:
        quantity: Kiritilgan miqdor
        service_type: Xizmat turi
    
    Returns:
        Tuple[bool, str]: (valid, error_message)
    """
    if not isinstance(quantity, int):
        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            return False, "Miqdor butun son bo'lishi kerak"
    
    if quantity <= 0:
        return False, "Miqdor 0 dan katta bo'lishi kerak"
    
    # Service-specific limitlar
    limits = SERVICE_LIMITS.get(service_type, SERVICE_LIMITS['default'])
    min_qty = limits['min']
    max_qty = limits['max']
    
    if quantity < min_qty:
        return False, f"Minimal miqdor: {min_qty:,}"
    
    if quantity > max_qty:
        return False, f"Maksimal miqdor: {max_qty:,}"
    
    return True, ""


# ==================== PHONE VALIDATION ====================

def validate_phone(phone: str) -> Tuple[bool, str]:
    """
    Telefon raqamni tekshirish (O'zbekiston)
    """
    phone = phone.strip().replace(' ', '').replace('-', '')
    
    # +998 bilan boshlanishi kerak
    if not phone.startswith('+998') and not phone.startswith('998'):
        if phone.startswith('9') and len(phone) == 9:
            phone = '+998' + phone
        else:
            return False, "Telefon raqam +998 bilan boshlanishi kerak"
    
    if phone.startswith('998'):
        phone = '+' + phone
    
    # Uzunlik tekshirish
    if len(phone) != 13:  # +998901234567
        return False, "Noto'g'ri telefon raqam formati"
    
    # Faqat raqamlar (+dan keyin)
    if not phone[1:].isdigit():
        return False, "Telefon raqamda faqat raqamlar bo'lishi kerak"
    
    return True, phone  # Formatlangan telefon raqam qaytaramiz


# ==================== AMOUNT VALIDATION ====================

def validate_amount(amount: int, min_amount: int = 1000, max_amount: int = 100000000) -> Tuple[bool, str]:
    """
    Pul miqdorini tekshirish
    """
    if not isinstance(amount, (int, float)):
        try:
            amount = int(amount)
        except (ValueError, TypeError):
            return False, "Summa raqam bo'lishi kerak"
    
    amount = int(amount)
    
    if amount < min_amount:
        return False, f"Minimal summa: {min_amount:,} so'm"
    
    if amount > max_amount:
        return False, f"Maksimal summa: {max_amount:,} so'm"
    
    return True, ""


# ==================== TEXT SANITIZATION ====================

def sanitize_text(text: str, max_length: int = 1000) -> str:
    """
    Matnni tozalash (XSS va injection oldini olish)
    """
    if not text:
        return ""
    
    # HTML teglarni olib tashlash
    text = re.sub(r'<[^>]+>', '', text)
    
    # Maxsus belgilarni escape qilish
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    
    # Uzunlikni cheklash
    if len(text) > max_length:
        text = text[:max_length]
    
    return text.strip()


def validate_username(username: str) -> Tuple[bool, str]:
    """
    Username validatsiyasi (Telegram, Instagram va boshqalar uchun)
    """
    if not username:
        return False, "Username kiritilmagan"
    
    username = username.strip()
    
    # @ belgisini olib tashlash
    if username.startswith('@'):
        username = username[1:]
    
    # Uzunlik tekshirish
    if len(username) < 3:
        return False, "Username kamida 3 ta belgi bo'lishi kerak"
    
    if len(username) > 32:
        return False, "Username 32 ta belgidan oshmasligi kerak"
    
    # Faqat harflar, raqamlar va pastki chiziq
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username faqat harflar, raqamlar va _ dan iborat bo'lishi kerak"
    
    return True, username


# ==================== COMBINED VALIDATION ====================

def validate_order_input(url: str, quantity: int, service_type: str, platform: str = None) -> Tuple[bool, str]:
    """
    Buyurtma uchun barcha inputlarni tekshirish
    """
    # URL validatsiyasi
    url_valid, url_error = validate_url(url, platform)
    if not url_valid:
        return False, f"❌ Link xatosi: {url_error}"
    
    # Quantity validatsiyasi
    qty_valid, qty_error = validate_quantity(quantity, service_type)
    if not qty_valid:
        return False, f"❌ Miqdor xatosi: {qty_error}"
    
    return True, ""


# ==================== RATE LIMITING HELPER ====================

class RateLimiter:
    """
    Foydalanuvchi harakatlarini cheklash
    """
    def __init__(self):
        self._requests = {}  # user_id: [(timestamp, action), ...]
    
    def is_allowed(self, user_id: int, action: str = 'default', 
                   max_requests: int = 10, window_seconds: int = 60) -> bool:
        """
        Foydalanuvchi so'rov yuborishi mumkinmi?
        """
        import time
        now = time.time()
        key = f"{user_id}:{action}"
        
        if key not in self._requests:
            self._requests[key] = []
        
        # Eski so'rovlarni tozalash
        self._requests[key] = [
            ts for ts in self._requests[key] 
            if now - ts < window_seconds
        ]
        
        # Limit tekshirish
        if len(self._requests[key]) >= max_requests:
            return False
        
        # Yangi so'rovni qo'shish
        self._requests[key].append(now)
        return True
    
    def get_remaining_time(self, user_id: int, action: str = 'default',
                          window_seconds: int = 60) -> int:
        """
        Qancha vaqt kutish kerak (sekundlarda)
        """
        import time
        now = time.time()
        key = f"{user_id}:{action}"
        
        if key not in self._requests or not self._requests[key]:
            return 0
        
        oldest = min(self._requests[key])
        remaining = window_seconds - (now - oldest)
        return max(0, int(remaining))


# Global rate limiter instance
rate_limiter = RateLimiter()
