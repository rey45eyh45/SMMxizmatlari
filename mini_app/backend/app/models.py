# -*- coding: utf-8 -*-
"""
Pydantic modellar - Request va Response schemalar
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ==================== TELEGRAM AUTH ====================

class TelegramUser(BaseModel):
    """Telegram foydalanuvchi ma'lumotlari"""
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    is_premium: Optional[bool] = False
    photo_url: Optional[str] = None


class TelegramInitData(BaseModel):
    """Telegram Mini App init data"""
    query_id: Optional[str] = None
    user: Optional[TelegramUser] = None
    auth_date: int
    hash: str


class AuthResponse(BaseModel):
    """Autentifikatsiya javobi"""
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


# ==================== USER ====================

class UserResponse(BaseModel):
    """Foydalanuvchi ma'lumotlari"""
    user_id: int
    username: Optional[str] = None
    full_name: Optional[str] = None
    balance: float = 0
    referral_count: int = 0
    referral_earnings: float = 0
    is_banned: bool = False
    created_at: Optional[str] = None


class BalanceResponse(BaseModel):
    """Balans javobi"""
    balance: float
    formatted: str


class ReferralStatsResponse(BaseModel):
    """Referal statistikasi"""
    referral_count: int
    referral_earnings: float
    referral_link: str
    referrals: List[Dict[str, Any]] = []


# ==================== SERVICES ====================

class ServiceInfo(BaseModel):
    """Xizmat ma'lumotlari"""
    id: str
    name: str
    description: str
    price_per_1000: int
    min_quantity: int
    max_quantity: int
    guarantee: str
    speed: str
    panel: str
    category: str
    platform: str


class ServiceCategory(BaseModel):
    """Xizmat kategoriyasi"""
    id: str
    name: str
    emoji: str
    services_count: int


class PlatformInfo(BaseModel):
    """Platforma ma'lumotlari"""
    id: str
    name: str
    emoji: str
    categories: List[ServiceCategory] = []


# ==================== ORDERS ====================

class OrderCreate(BaseModel):
    """Buyurtma yaratish"""
    service_id: str
    link: str
    quantity: int = Field(..., ge=1)


class OrderResponse(BaseModel):
    """Buyurtma javobi"""
    id: int
    service_type: str
    service_name: Optional[str] = None
    link: str
    quantity: int
    price: float
    status: str
    created_at: str
    api_order_id: Optional[int] = None
    panel_name: Optional[str] = None


class OrderStatusResponse(BaseModel):
    """Buyurtma holati"""
    order_id: int
    status: str
    charge: Optional[float] = None
    start_count: Optional[int] = None
    remains: Optional[int] = None


# ==================== PAYMENTS ====================

class PaymentCreate(BaseModel):
    """To'lov yaratish"""
    amount: float = Field(..., ge=1000)
    method: str


class PaymentResponse(BaseModel):
    """To'lov javobi"""
    id: int
    amount: float
    method: str
    status: str
    created_at: str
    card_number: Optional[str] = None
    card_holder: Optional[str] = None


class PaymentMethodResponse(BaseModel):
    """To'lov usuli"""
    id: str
    name: str
    card_number: str
    card_holder: str
    min_amount: int


# ==================== SMS/VIRTUAL NUMBERS ====================

class SMSPlatform(BaseModel):
    """SMS platforma"""
    code: str
    name: str
    emoji: str


class SMSCountry(BaseModel):
    """SMS davlat"""
    code: str
    name: str
    flag: str


class SMSPriceInfo(BaseModel):
    """SMS narx ma'lumotlari"""
    platform: str
    country: str
    price: float
    price_uzs: int
    available: int


class SMSOrderCreate(BaseModel):
    """SMS buyurtma yaratish"""
    platform: str
    country: str


class SMSOrderResponse(BaseModel):
    """SMS buyurtma javobi"""
    order_id: str
    phone_number: str
    platform: str
    country: str
    price: float
    status: str
    sms_code: Optional[str] = None
    expires_at: Optional[str] = None


# ==================== PREMIUM ====================

class PremiumPlan(BaseModel):
    """Premium tarif"""
    months: int
    price: int
    original_price: Optional[int] = None
    discount_percent: Optional[int] = None
    features: List[str] = []


class PremiumRequest(BaseModel):
    """Premium so'rov"""
    months: int
    phone: Optional[str] = None


class PremiumStatusResponse(BaseModel):
    """Premium holati"""
    is_premium: bool
    plan_type: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    days_left: Optional[int] = None


# ==================== SETTINGS ====================

class SettingsResponse(BaseModel):
    """Sozlamalar"""
    usd_rate: int
    rub_rate: int
    markup_percent: int
    min_deposit: int
    referral_bonus: int


# ==================== STATISTICS ====================

class StatisticsResponse(BaseModel):
    """Statistika"""
    total_users: int
    today_users: int
    total_orders: int
    today_orders: int
    total_revenue: float
    today_revenue: float
    pending_payments: int
