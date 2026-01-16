# -*- coding: utf-8 -*-
"""
Foydalanuvchi endpointlari
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List

from ..auth import get_current_user
from ..database import Database
from ..models import UserResponse, BalanceResponse, ReferralStatsResponse
from ..config import BOT_TOKEN

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user: Dict[str, Any] = Depends(get_current_user)):
    """
    Joriy foydalanuvchi ma'lumotlarini olish
    """
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
async def get_balance(user: Dict[str, Any] = Depends(get_current_user)):
    """
    Foydalanuvchi balansini olish
    """
    balance = Database.get_balance(user["user_id"])
    return BalanceResponse(
        balance=balance,
        formatted=f"{balance:,.0f} so'm"
    )


@router.get("/referral", response_model=ReferralStatsResponse)
async def get_referral_stats(user: Dict[str, Any] = Depends(get_current_user)):
    """
    Referal statistikasini olish
    """
    count, earnings = Database.get_referral_stats(user["user_id"])
    referrals = Database.get_referrals(user["user_id"])
    
    # Bot username olish
    bot_username = "idealsmm_bot"  # Default
    
    return ReferralStatsResponse(
        referral_count=count,
        referral_earnings=earnings,
        referral_link=f"https://t.me/{bot_username}?start=ref{user['user_id']}",
        referrals=referrals
    )


@router.get("/orders")
async def get_user_orders(
    limit: int = 20,
    user: Dict[str, Any] = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    Foydalanuvchi buyurtmalarini olish
    """
    orders = Database.get_user_orders(user["user_id"], limit)
    return orders


@router.get("/payments")
async def get_user_payments(
    limit: int = 20,
    user: Dict[str, Any] = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    Foydalanuvchi to'lovlarini olish
    """
    payments = Database.get_user_payments(user["user_id"], limit)
    return payments


@router.get("/premium")
async def get_premium_status(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Premium obuna holatini olish
    """
    premium = Database.get_user_premium(user["user_id"])
    
    if premium:
        from datetime import datetime
        end_date = datetime.strptime(premium["end_date"], "%Y-%m-%d %H:%M:%S")
        days_left = (end_date - datetime.now()).days
        
        return {
            "is_premium": True,
            "plan_type": premium.get("plan_type"),
            "start_date": premium.get("start_date"),
            "end_date": premium.get("end_date"),
            "days_left": max(0, days_left)
        }
    
    return {
        "is_premium": False,
        "plan_type": None,
        "start_date": None,
        "end_date": None,
        "days_left": None
    }
