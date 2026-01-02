# -*- coding: utf-8 -*-
"""
PROFESSIONAL CACHE TIZIMI
Bot tezligini 10x oshirish uchun
"""

import time
import asyncio
from functools import wraps
from typing import Any, Optional, Dict, Callable


class SimpleCache:
    """
    Oddiy va samarali cache tizimi
    TTL (Time To Live) bilan ishlaydi
    """
    
    def __init__(self, default_ttl: int = 300):
        """
        Args:
            default_ttl: Default cache vaqti (sekundlarda), default 5 daqiqa
        """
        self._cache: Dict[str, tuple] = {}
        self.default_ttl = default_ttl
        self.hits = 0  # Cache dan olindi
        self.misses = 0  # Cache da yo'q edi
    
    def get(self, key: str) -> Optional[Any]:
        """
        Cache dan ma'lumot olish
        
        Args:
            key: Cache kaliti
            
        Returns:
            Ma'lumot yoki None (agar mavjud bo'lmasa yoki eskirgan bo'lsa)
        """
        if key in self._cache:
            data, timestamp, ttl = self._cache[key]
            if time.time() - timestamp < ttl:
                self.hits += 1
                return data
            else:
                # Eskirgan - o'chirish
                del self._cache[key]
        
        self.misses += 1
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Cache ga ma'lumot saqlash
        
        Args:
            key: Cache kaliti
            value: Saqlanadigan ma'lumot
            ttl: Cache vaqti (sekundlarda), default_ttl ishlatiladi agar berilmasa
        """
        if ttl is None:
            ttl = self.default_ttl
        self._cache[key] = (value, time.time(), ttl)
    
    def delete(self, key: str) -> bool:
        """
        Cache dan o'chirish
        
        Args:
            key: Cache kaliti
            
        Returns:
            True agar o'chirilsa, False agar mavjud bo'lmasa
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Barcha cache ni tozalash"""
        self._cache.clear()
        self.hits = 0
        self.misses = 0
    
    def clear_expired(self) -> int:
        """
        Eskirgan cache larni tozalash
        
        Returns:
            O'chirilgan elementlar soni
        """
        now = time.time()
        expired_keys = [
            key for key, (_, timestamp, ttl) in self._cache.items()
            if now - timestamp >= ttl
        ]
        for key in expired_keys:
            del self._cache[key]
        return len(expired_keys)
    
    def get_stats(self) -> dict:
        """Cache statistikasi"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            'size': len(self._cache),
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': f"{hit_rate:.1f}%"
        }
    
    def __len__(self) -> int:
        return len(self._cache)
    
    def __contains__(self, key: str) -> bool:
        return self.get(key) is not None


# ==================== GLOBAL CACHE INSTANCES ====================

# Xizmatlar uchun cache (1 soat)
services_cache = SimpleCache(default_ttl=3600)

# Narxlar uchun cache (30 daqiqa)
prices_cache = SimpleCache(default_ttl=1800)

# API balance uchun cache (1 daqiqa)
balance_cache = SimpleCache(default_ttl=60)

# SMS davlatlar/platformalar uchun cache (1 soat)
sms_cache = SimpleCache(default_ttl=3600)


# ==================== DECORATOR ====================

def cached(cache_instance: SimpleCache, key_prefix: str = "", ttl: Optional[int] = None):
    """
    Funksiyani cache qilish uchun decorator
    
    Args:
        cache_instance: Qaysi cache ishlatiladi
        key_prefix: Cache key prefiksi
        ttl: Cache vaqti
    
    Example:
        @cached(services_cache, "services", ttl=3600)
        def get_services():
            return api.get_services()
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Cache key yaratish
            key_parts = [key_prefix, func.__name__]
            if args:
                key_parts.extend(str(a) for a in args)
            if kwargs:
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)
            
            # Cache dan olishga harakat
            result = cache_instance.get(cache_key)
            if result is not None:
                return result
            
            # Cache da yo'q - funksiyani chaqirish
            result = func(*args, **kwargs)
            
            # Cache ga saqlash
            if result is not None:
                cache_instance.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


def async_cached(cache_instance: SimpleCache, key_prefix: str = "", ttl: Optional[int] = None):
    """Async funksiyalar uchun cache decorator"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Cache key yaratish
            key_parts = [key_prefix, func.__name__]
            if args:
                key_parts.extend(str(a) for a in args)
            if kwargs:
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)
            
            # Cache dan olishga harakat
            result = cache_instance.get(cache_key)
            if result is not None:
                return result
            
            # Cache da yo'q - funksiyani chaqirish
            result = await func(*args, **kwargs)
            
            # Cache ga saqlash
            if result is not None:
                cache_instance.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


# ==================== YORDAMCHI FUNKSIYALAR ====================

def get_all_cache_stats() -> dict:
    """Barcha cache statistikasi"""
    return {
        'services': services_cache.get_stats(),
        'prices': prices_cache.get_stats(),
        'balance': balance_cache.get_stats(),
        'sms': sms_cache.get_stats()
    }


def clear_all_caches() -> None:
    """Barcha cache larni tozalash"""
    services_cache.clear()
    prices_cache.clear()
    balance_cache.clear()
    sms_cache.clear()


def clear_expired_caches() -> dict:
    """Barcha eskirgan cache larni tozalash"""
    return {
        'services': services_cache.clear_expired(),
        'prices': prices_cache.clear_expired(),
        'balance': balance_cache.clear_expired(),
        'sms': sms_cache.clear_expired()
    }
