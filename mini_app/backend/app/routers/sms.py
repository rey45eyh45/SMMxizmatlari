# -*- coding: utf-8 -*-
"""
SMS / Virtual raqam endpointlari
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List

from ..auth import get_current_user
from ..database import Database
from ..services import SMS_PLATFORMS, SMS_COUNTRIES
from ..sms_api import sms_api
from ..models import SMSOrderCreate, SMSOrderResponse, SMSPriceInfo

router = APIRouter(prefix="/sms", tags=["sms"])


@router.get("/platforms")
async def get_sms_platforms() -> List[Dict[str, Any]]:
    """
    SMS platformalarini olish
    """
    return [
        {"code": code, "name": data["name"], "emoji": data["emoji"]}
        for code, data in SMS_PLATFORMS.items()
    ]


@router.get("/countries")
async def get_sms_countries() -> List[Dict[str, Any]]:
    """
    SMS davlatlarini olish
    """
    return [
        {"code": code, "name": data["name"], "flag": data["flag"]}
        for code, data in SMS_COUNTRIES.items()
    ]


@router.get("/prices/{platform}/{country}")
async def get_sms_prices(
    platform: str,
    country: str,
    user: Dict[str, Any] = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    SMS narxlarini olish
    """
    if platform not in SMS_PLATFORMS:
        raise HTTPException(status_code=400, detail="Platforma topilmadi")
    
    if country not in SMS_COUNTRIES:
        raise HTTPException(status_code=400, detail="Davlat topilmadi")
    
    prices = await sms_api.get_prices(platform, country)
    return prices


@router.post("/buy")
async def buy_sms_number(
    order: SMSOrderCreate,
    user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Virtual raqam sotib olish
    """
    if order.platform not in SMS_PLATFORMS:
        raise HTTPException(status_code=400, detail="Platforma topilmadi")
    
    if order.country not in SMS_COUNTRIES:
        raise HTTPException(status_code=400, detail="Davlat topilmadi")
    
    # Narxlarni olish
    prices = await sms_api.get_prices(order.platform, order.country)
    
    if not prices:
        raise HTTPException(status_code=404, detail="Raqam mavjud emas")
    
    # Eng arzon variantni tanlash
    cheapest = prices[0]
    price_uzs = cheapest["price_uzs"]
    provider = cheapest["provider"]
    
    # Balansni tekshirish
    balance = Database.get_balance(user["user_id"])
    if balance < price_uzs:
        raise HTTPException(
            status_code=400,
            detail=f"Balans yetarli emas. Kerak: {price_uzs:,} so'm"
        )
    
    # Raqam sotib olish
    result = await sms_api.buy_number(provider, order.platform, order.country)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=500,
            detail=result.get("error", "Raqam olishda xatolik")
        )
    
    # Balansdan yechish
    Database.update_balance(user["user_id"], -price_uzs)
    
    return {
        "success": True,
        "order_id": result["order_id"],
        "phone_number": result["phone"],
        "provider": provider,
        "platform": order.platform,
        "country": order.country,
        "price": price_uzs,
        "status": "waiting"
    }


@router.get("/check/{provider}/{order_id}")
async def check_sms_code(
    provider: str,
    order_id: str,
    user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    SMS kodini tekshirish
    """
    result = await sms_api.get_sms(provider, order_id)
    
    return {
        "order_id": order_id,
        "status": result.get("status", "waiting"),
        "code": result.get("code")
    }


@router.post("/cancel/{provider}/{order_id}")
async def cancel_sms_order(
    provider: str,
    order_id: str,
    user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    SMS buyurtmani bekor qilish
    """
    result = await sms_api.cancel_order(provider, order_id)
    
    return {
        "order_id": order_id,
        "cancelled": True
    }
