# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException, Response
from typing import Dict, Any, Optional
from pydantic import BaseModel
import httpx
import logging

from ..auth import get_current_user
from ..models import UserResponse, BalanceResponse, ReferralStatsResponse
from ..config import BOT_API_URL

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/user", tags=["user"])

class CreateUserRequest(BaseModel):
    user_id: int
    username: Optional[str] = None
    full_name: str

async def fetch_from_bot_api(endpoint: str, method: str = "GET", data: dict = None) -> dict:
    url = f"{BOT_API_URL}{endpoint}"
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            if method == "GET":
                response = await client.get(url)
            else:
                response = await client.post(url, json=data)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Bot API request error: {e}")
        raise HTTPException(status_code=503, detail="Bot API ga ulanib bolmadi")
    except Exception as e:
        logger.error(f"Bot API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user: Dict[str, Any] = Depends(get_current_user)):
    return UserResponse(
        user_id=user["user_id"],
        username=user.get("username"),
        full_name=user.get("full_name"),
        balance=user.get("balance", 0),
        referral_count=user.get("referral_count", 0),
        referral_earnings=user.get("referral_earnings", 0),
        is_banned=bool(user.get("is_banned", 0)),
        created_at=user.get("created_at")
    )

@router.get("/balance", response_model=BalanceResponse)
async def get_balance(response: Response, user: Dict[str, Any] = Depends(get_current_user)):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    result = await fetch_from_bot_api(f"/api/user/{user['user_id']}")
    if not result or not result.get("user"):
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    balance = result["user"].get("balance", 0)
    return BalanceResponse(balance=balance, formatted=f"{balance:,.0f} som")

@router.get("/{user_id}")
async def get_user_by_id(user_id: int, response: Response) -> Dict[str, Any]:
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    result = await fetch_from_bot_api(f"/api/user/{user_id}")
    if not result:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    return result

@router.post("/create")
async def create_or_get_user(request: CreateUserRequest) -> Dict[str, Any]:
    result = await fetch_from_bot_api(
        "/api/user/create",
        method="POST",
        data={"user_id": request.user_id, "username": request.username or "", "full_name": request.full_name}
    )
    if not result:
        raise HTTPException(status_code=500, detail="Foydalanuvchi yaratishda xatolik")
    return result

@router.get("/by-phone/{phone}")
async def get_user_by_phone(phone: str, response: Response) -> Dict[str, Any]:
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    result = await fetch_from_bot_api(f"/api/user/by-phone/{phone}")
    if not result:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    return result

@router.get("/referral", response_model=ReferralStatsResponse)
async def get_referral_stats(user: Dict[str, Any] = Depends(get_current_user)):
    result = await fetch_from_bot_api(f"/api/user/{user['user_id']}")
    if not result or not result.get("user"):
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    user_data = result["user"]
    return ReferralStatsResponse(
        referral_count=user_data.get("referral_count", 0),
        referral_earnings=user_data.get("referral_earnings", 0),
        referral_link=f"https://t.me/idealsmm_bot?start=ref{user['user_id']}",
        referrals=[]
    )

@router.get("/orders")
async def get_user_orders(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    result = await fetch_from_bot_api(f"/api/user/{user['user_id']}/orders")
    if not result:
        return {"orders": []}
    return result

@router.get("/payments")
async def get_user_payments(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    result = await fetch_from_bot_api(f"/api/user/{user['user_id']}/payments")
    if not result:
        return {"payments": []}
    return result

@router.get("/premium")
async def get_premium_status(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    result = await fetch_from_bot_api(f"/api/user/{user['user_id']}/premium")
    if not result:
        return {"is_premium": False, "plan_type": None, "days_left": 0, "end_date": None}
    return result
