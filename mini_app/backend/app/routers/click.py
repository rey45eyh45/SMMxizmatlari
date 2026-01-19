# -*- coding: utf-8 -*-
"""
Click to'lov tizimi endpointlari

Click API webhook'lari bu yerga keladi:
- /api/click/prepare - To'lov tayyorlash
- /api/click/complete - To'lovni yakunlash

Shuningdek foydalanuvchi uchun:
- /api/click/create - Yangi Click to'lov yaratish
- /api/click/status/{payment_id} - To'lov holatini tekshirish
"""
from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from ..click_api import ClickAPI
from ..auth import get_current_user
from ..database import Database
from ..config import CLICK_MERCHANT_ID, CLICK_SERVICE_ID, CLICK_SECRET_KEY

router = APIRouter(prefix="/click", tags=["click"])


# ==================== Pydantic Models ====================

class ClickPaymentCreate(BaseModel):
    """Click to'lov yaratish so'rovi"""
    amount: float = Field(..., ge=1000, description="To'lov miqdori (min 1000 so'm)")


class ClickPaymentResponse(BaseModel):
    """Click to'lov javobi"""
    success: bool
    payment_id: Optional[int] = None
    payment_url: Optional[str] = None
    amount: Optional[float] = None
    error: Optional[str] = None


class ClickStatusResponse(BaseModel):
    """Click to'lov holati"""
    success: bool
    payment_id: Optional[int] = None
    amount: Optional[float] = None
    status: Optional[str] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None


# ==================== User Endpoints ====================

@router.post("/create", response_model=ClickPaymentResponse)
async def create_click_payment(
    payment: ClickPaymentCreate,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Click orqali yangi to'lov yaratish
    
    Foydalanuvchi bu endpointga so'rov yuboradi va
    payment_url oladi. Keyin shu URLga o'tib to'lov qiladi.
    """
    result = ClickAPI.create_payment(
        user_id=user["user_id"],
        amount=payment.amount
    )
    
    if result['success']:
        return ClickPaymentResponse(
            success=True,
            payment_id=result['payment_id'],
            payment_url=result['payment_url'],
            amount=result['amount']
        )
    else:
        return ClickPaymentResponse(
            success=False,
            error=result.get('error', "Noma'lum xatolik")
        )


@router.get("/status/{payment_id}", response_model=ClickStatusResponse)
async def get_click_payment_status(
    payment_id: int,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Click to'lov holatini tekshirish
    
    Foydalanuvchi to'lov qilgandan keyin shu endpoint orqali
    to'lov holatini tekshirishi mumkin.
    """
    result = ClickAPI.get_payment_status(payment_id)
    
    if result['success']:
        # Foydalanuvchi faqat o'z to'lovlarini ko'rishi mumkin
        payment = Database.get_click_payment(payment_id)
        if payment and payment['user_id'] != user['user_id']:
            raise HTTPException(status_code=403, detail="Ruxsat yo'q")
        
        return ClickStatusResponse(
            success=True,
            payment_id=result['payment_id'],
            amount=result['amount'],
            status=result['status'],
            created_at=result.get('created_at'),
            completed_at=result.get('completed_at')
        )
    else:
        return ClickStatusResponse(
            success=False,
            error=result.get('error')
        )


@router.get("/my-payments")
async def get_my_click_payments(
    limit: int = 20,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Mening Click to'lovlarim ro'yxati
    """
    payments = Database.get_user_click_payments(user["user_id"], limit)
    return {
        "success": True,
        "payments": payments
    }


# ==================== Click Webhook Endpoints ====================

@router.post("/prepare")
async def click_prepare(request: Request):
    """
    Click Prepare webhook
    
    Click to'lov boshlanganda shu endpointga so'rov yuboradi.
    Bu yerda to'lov ma'lumotlari tekshiriladi va tasdiqlanadi.
    
    Click yuboradigan parametrlar (form-data):
    - click_trans_id: Click tranzaksiya ID
    - service_id: Merchant service ID
    - click_paydoc_id: Click to'lov hujjati ID
    - merchant_trans_id: Bizning to'lov ID
    - amount: To'lov miqdori
    - action: 0 (Prepare uchun)
    - error: 0 (Xato yo'q)
    - error_note: Xato tavsifi
    - sign_time: Imzo vaqti
    - sign_string: MD5 imzo
    """
    try:
        # Form data olish
        form_data = await request.form()
        data = {key: form_data.get(key) for key in form_data.keys()}
        
        # JSON ham qabul qilish (test uchun)
        if not data:
            try:
                data = await request.json()
            except:
                pass
        
        print(f"Click Prepare so'rovi: {data}")
        
        # Click API orqali prepare
        result = ClickAPI.prepare(data)
        
        print(f"Click Prepare javobi: {result}")
        
        return JSONResponse(content=result)
        
    except Exception as e:
        print(f"Click Prepare xatolik: {e}")
        return JSONResponse(content={
            'error': -7,
            'error_note': f'Server xatoligi: {str(e)}'
        })


@router.post("/complete")
async def click_complete(request: Request):
    """
    Click Complete webhook
    
    Click to'lov muvaffaqiyatli bo'lganda shu endpointga so'rov yuboradi.
    Bu yerda to'lov yakunlanadi va foydalanuvchi balansiga qo'shiladi.
    
    Click yuboradigan parametrlar (form-data):
    - click_trans_id: Click tranzaksiya ID
    - service_id: Merchant service ID
    - click_paydoc_id: Click to'lov hujjati ID
    - merchant_trans_id: Bizning to'lov ID
    - merchant_prepare_id: Prepare da qaytargan ID
    - amount: To'lov miqdori
    - action: 1 (Complete uchun)
    - error: 0 (Xato yo'q) yoki xato kodi
    - error_note: Xato tavsifi
    - sign_time: Imzo vaqti
    - sign_string: MD5 imzo
    """
    try:
        # Form data olish
        form_data = await request.form()
        data = {key: form_data.get(key) for key in form_data.keys()}
        
        # JSON ham qabul qilish (test uchun)
        if not data:
            try:
                data = await request.json()
            except:
                pass
        
        print(f"Click Complete so'rovi: {data}")
        
        # Click API orqali complete
        result = ClickAPI.complete(data)
        
        print(f"Click Complete javobi: {result}")
        
        return JSONResponse(content=result)
        
    except Exception as e:
        print(f"Click Complete xatolik: {e}")
        return JSONResponse(content={
            'error': -7,
            'error_note': f'Server xatoligi: {str(e)}'
        })


# ==================== Test/Debug Endpoints ====================

@router.get("/test")
async def test_click_config():
    """
    Click konfiguratsiyasini tekshirish (faqat debug uchun)
    
    Production'da bu endpointni o'chirib qo'ying!
    """
    return {
        "merchant_id_configured": bool(CLICK_MERCHANT_ID),
        "service_id_configured": bool(CLICK_SERVICE_ID),
        "secret_key_configured": bool(CLICK_SECRET_KEY),
        "note": "Agar hamma qiymat True bo'lsa, Click tayyor"
    }
