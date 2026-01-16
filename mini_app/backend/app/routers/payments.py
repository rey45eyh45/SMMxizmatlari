# -*- coding: utf-8 -*-
"""
To'lov endpointlari
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Dict, Any, List

from ..auth import get_current_user
from ..database import Database
from ..config import PAYMENT_CARDS
from ..models import PaymentCreate, PaymentResponse, PaymentMethodResponse

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("/methods")
async def get_payment_methods() -> List[PaymentMethodResponse]:
    """
    To'lov usullarini olish
    """
    min_deposit = int(Database.get_setting("min_deposit", "5000"))
    
    methods = []
    for name, data in PAYMENT_CARDS.items():
        methods.append(PaymentMethodResponse(
            id=name.lower().replace("/", "_"),
            name=name,
            card_number=data["card"],
            card_holder=data["name"],
            min_amount=min_deposit
        ))
    
    return methods


@router.post("/create", response_model=PaymentResponse)
async def create_payment(
    payment: PaymentCreate,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Yangi to'lov yaratish
    """
    min_deposit = int(Database.get_setting("min_deposit", "5000"))
    
    if payment.amount < min_deposit:
        raise HTTPException(
            status_code=400,
            detail=f"Minimal to'lov: {min_deposit:,} so'm"
        )
    
    # Karta ma'lumotlarini olish
    card_data = None
    for name, data in PAYMENT_CARDS.items():
        if name.lower().replace("/", "_") == payment.method.lower():
            card_data = data
            break
    
    if not card_data:
        raise HTTPException(status_code=400, detail="To'lov usuli topilmadi")
    
    # To'lov yaratish
    payment_id = Database.add_payment(
        user_id=user["user_id"],
        amount=payment.amount,
        method=payment.method
    )
    
    return PaymentResponse(
        id=payment_id,
        amount=payment.amount,
        method=payment.method,
        status="kutilmoqda",
        created_at="",
        card_number=card_data["card"],
        card_holder=card_data["name"]
    )


@router.get("/my", response_model=List[PaymentResponse])
async def get_my_payments(
    limit: int = 20,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Mening to'lovlarim
    """
    payments = Database.get_user_payments(user["user_id"], limit)
    
    result = []
    for payment in payments:
        result.append(PaymentResponse(
            id=payment["id"],
            amount=payment.get("amount", 0),
            method=payment.get("method", ""),
            status=payment.get("status", "unknown"),
            created_at=payment.get("created_at", "")
        ))
    
    return result


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment_details(
    payment_id: int,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    To'lov tafsilotlari
    """
    payment = Database.get_payment(payment_id)
    
    if not payment:
        raise HTTPException(status_code=404, detail="To'lov topilmadi")
    
    if payment["user_id"] != user["user_id"]:
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")
    
    return PaymentResponse(
        id=payment["id"],
        amount=payment.get("amount", 0),
        method=payment.get("method", ""),
        status=payment.get("status", "unknown"),
        created_at=payment.get("created_at", "")
    )
