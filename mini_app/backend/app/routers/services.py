# -*- coding: utf-8 -*-
"""
Xizmatlar endpointlari
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List

from ..services import (
    PLATFORMS, 
    ALL_SERVICES,
    SMS_PLATFORMS,
    SMS_COUNTRIES,
    PREMIUM_PLANS,
    get_service_info,
    get_services_by_platform,
    get_categories_by_platform
)

router = APIRouter(prefix="/services", tags=["services"])


@router.get("/platforms")
async def get_platforms() -> List[Dict[str, Any]]:
    """
    Barcha platformalarni olish
    """
    return [
        {
            "id": p["id"],
            "name": p["name"],
            "emoji": p["emoji"],
            "color": p.get("color", "#000000")
        }
        for p in PLATFORMS.values()
    ]


@router.get("/platform/{platform_id}")
async def get_platform_services(platform_id: str) -> Dict[str, Any]:
    """
    Platforma bo'yicha xizmatlarni olish
    """
    if platform_id not in PLATFORMS:
        raise HTTPException(status_code=404, detail="Platforma topilmadi")
    
    platform = PLATFORMS[platform_id]
    categories = get_categories_by_platform(platform_id)
    services = get_services_by_platform(platform_id)
    
    return {
        "platform": platform,
        "categories": categories,
        "services": services
    }


@router.get("/platform/{platform_id}/category/{category_id}")
async def get_category_services(platform_id: str, category_id: str) -> List[Dict[str, Any]]:
    """
    Kategoriya bo'yicha xizmatlarni olish
    """
    services = get_services_by_platform(platform_id)
    return [s for s in services if s.get("category") == category_id]


@router.get("/service/{service_id}")
async def get_service_details(service_id: str) -> Dict[str, Any]:
    """
    Xizmat haqida to'liq ma'lumot
    """
    info = get_service_info(service_id)
    if not info:
        raise HTTPException(status_code=404, detail="Xizmat topilmadi")
    return info


@router.get("/sms/platforms")
async def get_sms_platforms() -> List[Dict[str, Any]]:
    """
    SMS platformalarini olish
    """
    return [
        {"code": code, "name": data["name"], "emoji": data["emoji"]}
        for code, data in SMS_PLATFORMS.items()
    ]


@router.get("/sms/countries")
async def get_sms_countries() -> List[Dict[str, Any]]:
    """
    SMS davlatlarini olish
    """
    return [
        {"code": code, "name": data["name"], "flag": data["flag"]}
        for code, data in SMS_COUNTRIES.items()
    ]


@router.get("/premium/plans")
async def get_premium_plans() -> List[Dict[str, Any]]:
    """
    Premium tariflarini olish
    """
    plans = []
    for months, data in PREMIUM_PLANS.items():
        discount = 0
        if data.get("original_price") and data["original_price"] > data["price"]:
            discount = int((1 - data["price"] / data["original_price"]) * 100)
        
        plans.append({
            "months": months,
            "price": data["price"],
            "original_price": data.get("original_price"),
            "discount_percent": discount,
            "popular": data.get("popular", False),
            "best_value": data.get("best_value", False),
            "features": [
                "✅ Telegram Premium obuna",
                "✅ Premium emoji va sticker",
                "✅ 4GB fayl yuklash",
                "✅ Reklama yo'q",
                "✅ Tez yuklab olish"
            ]
        })
    
    return plans
