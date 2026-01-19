# -*- coding: utf-8 -*-
"""
ADMIN PANEL API
Foydalanuvchilar, buyurtmalar, to'lovlar va statistikani boshqarish
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import sqlite3
import hashlib
import os

from ..config import DATABASE_PATH, ADMIN_IDS
from ..database import get_db_connection

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ==================== SCHEMAS ====================

class AdminLogin(BaseModel):
    user_id: int
    hash: str

class UserUpdate(BaseModel):
    balance: Optional[float] = None
    is_blocked: Optional[bool] = None

class BalanceChange(BaseModel):
    user_id: int
    amount: float
    reason: str = ""

class OrderUpdate(BaseModel):
    status: str
    note: Optional[str] = None


# ==================== AUTH MIDDLEWARE ====================

async def verify_admin(user_id: int = Query(...), admin_hash: str = Query(...)):
    """Admin tekshirish"""
    # Admin ID tekshirish
    if user_id not in ADMIN_IDS:
        raise HTTPException(status_code=403, detail="Admin emas")
    
    # Hash tekshirish (sodda versiya - ishlab chiqishda)
    expected_hash = hashlib.md5(f"{user_id}:admin_secret_key".encode()).hexdigest()[:16]
    
    # Development rejimda har qanday hash qabul qilinadi
    if os.getenv("DEBUG", "true").lower() == "true":
        return user_id
    
    if admin_hash != expected_hash:
        raise HTTPException(status_code=403, detail="Noto'g'ri hash")
    
    return user_id


# ==================== DASHBOARD ====================

@router.get("/dashboard")
async def get_dashboard(admin_id: int = Depends(verify_admin)):
    """Asosiy dashboard statistikasi"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Foydalanuvchilar
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        # Bugungi yangi foydalanuvchilar
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("SELECT COUNT(*) FROM users WHERE created_at LIKE ?", (f"{today}%",))
        today_users = cursor.fetchone()[0]
        
        # Buyurtmalar
        cursor.execute("SELECT COUNT(*) FROM orders")
        total_orders = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders WHERE created_at LIKE ?", (f"{today}%",))
        today_orders = cursor.fetchone()[0]
        
        # Umumiy daromad
        cursor.execute("SELECT COALESCE(SUM(price), 0) FROM orders WHERE status = 'completed'")
        total_revenue = cursor.fetchone()[0]
        
        cursor.execute("SELECT COALESCE(SUM(price), 0) FROM orders WHERE status = 'completed' AND created_at LIKE ?", (f"{today}%",))
        today_revenue = cursor.fetchone()[0]
        
        # To'lovlar
        cursor.execute("SELECT COUNT(*) FROM payments WHERE status = 'pending'")
        pending_payments = cursor.fetchone()[0]
        
        cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM payments WHERE status = 'approved'")
        total_deposits = cursor.fetchone()[0]
        
        # Buyurtma statuslari
        cursor.execute("""
            SELECT status, COUNT(*) 
            FROM orders 
            GROUP BY status
        """)
        order_stats = dict(cursor.fetchall())
        
        # Oxirgi 7 kunlik statistika
        weekly_stats = []
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            cursor.execute("""
                SELECT COUNT(*), COALESCE(SUM(price), 0) 
                FROM orders 
                WHERE created_at LIKE ?
            """, (f"{date}%",))
            row = cursor.fetchone()
            weekly_stats.append({
                "date": date,
                "orders": row[0],
                "revenue": row[1]
            })
        
        return {
            "success": True,
            "data": {
                "users": {
                    "total": total_users,
                    "today": today_users
                },
                "orders": {
                    "total": total_orders,
                    "today": today_orders,
                    "pending": order_stats.get("pending", 0),
                    "processing": order_stats.get("processing", 0),
                    "completed": order_stats.get("completed", 0),
                    "canceled": order_stats.get("canceled", 0)
                },
                "revenue": {
                    "total": total_revenue,
                    "today": today_revenue
                },
                "payments": {
                    "pending": pending_payments,
                    "total_deposits": total_deposits
                },
                "weekly_stats": weekly_stats
            }
        }
        
    finally:
        conn.close()


# ==================== USERS ====================

@router.get("/users")
async def get_users(
    admin_id: int = Depends(verify_admin),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    sort_by: str = Query("created_at", regex="^(created_at|balance|orders_count)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$")
):
    """Foydalanuvchilar ro'yxati"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        offset = (page - 1) * limit
        
        # Base query
        base_query = """
            SELECT u.user_id, u.username, u.full_name, u.balance, u.created_at,
                   u.is_blocked, u.phone_number,
                   (SELECT COUNT(*) FROM orders WHERE user_id = u.user_id) as orders_count,
                   (SELECT COALESCE(SUM(price), 0) FROM orders WHERE user_id = u.user_id AND status = 'completed') as total_spent
            FROM users u
        """
        
        count_query = "SELECT COUNT(*) FROM users u"
        params = []
        
        if search:
            where = " WHERE u.user_id LIKE ? OR u.username LIKE ? OR u.full_name LIKE ? OR u.phone_number LIKE ?"
            search_param = f"%{search}%"
            params = [search_param, search_param, search_param, search_param]
            base_query += where
            count_query += where
        
        # Count
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        # Order and limit
        base_query += f" ORDER BY {sort_by} {sort_order} LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(base_query, params)
        users = []
        for row in cursor.fetchall():
            users.append({
                "user_id": row[0],
                "username": row[1],
                "full_name": row[2],
                "balance": row[3],
                "created_at": row[4],
                "is_blocked": bool(row[5]) if row[5] else False,
                "phone_number": row[6],
                "orders_count": row[7],
                "total_spent": row[8]
            })
        
        return {
            "success": True,
            "data": {
                "users": users,
                "total": total,
                "page": page,
                "pages": (total + limit - 1) // limit
            }
        }
        
    finally:
        conn.close()


@router.get("/users/{user_id}")
async def get_user_detail(user_id: int, admin_id: int = Depends(verify_admin)):
    """Foydalanuvchi batafsil ma'lumoti"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT user_id, username, full_name, balance, created_at, 
                   is_blocked, phone_number, referrer_id
            FROM users WHERE user_id = ?
        """, (user_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
        
        # Buyurtmalar
        cursor.execute("""
            SELECT id, service_type, quantity, price, status, created_at
            FROM orders WHERE user_id = ?
            ORDER BY created_at DESC LIMIT 10
        """, (user_id,))
        orders = [
            {
                "id": o[0],
                "service": o[1],
                "quantity": o[2],
                "price": o[3],
                "status": o[4],
                "created_at": o[5]
            } for o in cursor.fetchall()
        ]
        
        # To'lovlar
        cursor.execute("""
            SELECT id, amount, method, status, created_at
            FROM payments WHERE user_id = ?
            ORDER BY created_at DESC LIMIT 10
        """, (user_id,))
        payments = [
            {
                "id": p[0],
                "amount": p[1],
                "method": p[2],
                "status": p[3],
                "created_at": p[4]
            } for p in cursor.fetchall()
        ]
        
        # Referallar
        cursor.execute("""
            SELECT user_id, username, full_name, created_at
            FROM users WHERE referrer_id = ?
        """, (user_id,))
        referrals = [
            {
                "user_id": r[0],
                "username": r[1],
                "full_name": r[2],
                "created_at": r[3]
            } for r in cursor.fetchall()
        ]
        
        return {
            "success": True,
            "data": {
                "user": {
                    "user_id": row[0],
                    "username": row[1],
                    "full_name": row[2],
                    "balance": row[3],
                    "created_at": row[4],
                    "is_blocked": bool(row[5]) if row[5] else False,
                    "phone_number": row[6],
                    "referrer_id": row[7]
                },
                "orders": orders,
                "payments": payments,
                "referrals": referrals,
                "stats": {
                    "total_orders": len(orders),
                    "total_referrals": len(referrals)
                }
            }
        }
        
    finally:
        conn.close()


@router.put("/users/{user_id}")
async def update_user(user_id: int, data: UserUpdate, admin_id: int = Depends(verify_admin)):
    """Foydalanuvchi ma'lumotlarini yangilash"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        updates = []
        params = []
        
        if data.balance is not None:
            updates.append("balance = ?")
            params.append(data.balance)
        
        if data.is_blocked is not None:
            updates.append("is_blocked = ?")
            params.append(1 if data.is_blocked else 0)
        
        if not updates:
            raise HTTPException(status_code=400, detail="Hech narsa yangilanmadi")
        
        params.append(user_id)
        cursor.execute(f"UPDATE users SET {', '.join(updates)} WHERE user_id = ?", params)
        conn.commit()
        
        return {"success": True, "message": "Foydalanuvchi yangilandi"}
        
    finally:
        conn.close()


@router.post("/users/balance")
async def change_user_balance(data: BalanceChange, admin_id: int = Depends(verify_admin)):
    """Foydalanuvchi balansini o'zgartirish"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Joriy balans
        cursor.execute("SELECT balance FROM users WHERE user_id = ?", (data.user_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
        
        current_balance = row[0]
        new_balance = current_balance + data.amount
        
        if new_balance < 0:
            raise HTTPException(status_code=400, detail="Balans manfiy bo'lishi mumkin emas")
        
        cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, data.user_id))
        
        # Log
        cursor.execute("""
            INSERT INTO balance_logs (user_id, amount, balance_before, balance_after, reason, admin_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (data.user_id, data.amount, current_balance, new_balance, data.reason, admin_id, datetime.now().isoformat()))
        
        conn.commit()
        
        return {
            "success": True,
            "message": f"Balans o'zgartirildi: {current_balance:,.0f} → {new_balance:,.0f}",
            "data": {
                "old_balance": current_balance,
                "new_balance": new_balance,
                "change": data.amount
            }
        }
        
    except sqlite3.OperationalError:
        # balance_logs jadvali yo'q bo'lsa
        conn.commit()
        return {"success": True, "message": "Balans o'zgartirildi"}
        
    finally:
        conn.close()


# ==================== ORDERS ====================

@router.get("/orders")
async def get_orders(
    admin_id: int = Depends(verify_admin),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    user_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
):
    """Buyurtmalar ro'yxati"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        offset = (page - 1) * limit
        
        base_query = """
            SELECT o.id, o.user_id, o.service_type, o.link, o.quantity, 
                   o.price, o.status, o.created_at, o.api_order_id,
                   u.username, u.full_name
            FROM orders o
            LEFT JOIN users u ON o.user_id = u.user_id
        """
        
        count_query = "SELECT COUNT(*) FROM orders o"
        
        conditions = []
        params = []
        
        if status:
            conditions.append("o.status = ?")
            params.append(status)
        
        if user_id:
            conditions.append("o.user_id = ?")
            params.append(user_id)
        
        if date_from:
            conditions.append("o.created_at >= ?")
            params.append(date_from)
        
        if date_to:
            conditions.append("o.created_at <= ?")
            params.append(date_to + " 23:59:59")
        
        if conditions:
            where = " WHERE " + " AND ".join(conditions)
            base_query += where
            count_query += where
        
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        base_query += " ORDER BY o.id DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(base_query, params)
        orders = []
        for row in cursor.fetchall():
            orders.append({
                "id": row[0],
                "user_id": row[1],
                "service": row[2],
                "link": row[3],
                "quantity": row[4],
                "price": row[5],
                "status": row[6],
                "created_at": row[7],
                "api_order_id": row[8],
                "username": row[9],
                "full_name": row[10]
            })
        
        return {
            "success": True,
            "data": {
                "orders": orders,
                "total": total,
                "page": page,
                "pages": (total + limit - 1) // limit
            }
        }
        
    finally:
        conn.close()


@router.get("/orders/{order_id}")
async def get_order_detail(order_id: int, admin_id: int = Depends(verify_admin)):
    """Buyurtma batafsil"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT o.*, u.username, u.full_name, u.phone_number
            FROM orders o
            LEFT JOIN users u ON o.user_id = u.user_id
            WHERE o.id = ?
        """, (order_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Buyurtma topilmadi")
        
        columns = [desc[0] for desc in cursor.description]
        order = dict(zip(columns, row))
        
        return {"success": True, "data": order}
        
    finally:
        conn.close()


@router.put("/orders/{order_id}")
async def update_order(order_id: int, data: OrderUpdate, admin_id: int = Depends(verify_admin)):
    """Buyurtma statusini yangilash"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        valid_statuses = ["pending", "processing", "completed", "canceled", "partial"]
        if data.status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Noto'g'ri status. Ruxsat: {valid_statuses}")
        
        cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (data.status, order_id))
        conn.commit()
        
        return {"success": True, "message": "Buyurtma yangilandi"}
        
    finally:
        conn.close()


# ==================== PAYMENTS ====================

@router.get("/payments")
async def get_payments(
    admin_id: int = Depends(verify_admin),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None
):
    """To'lovlar ro'yxati"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        offset = (page - 1) * limit
        
        base_query = """
            SELECT p.id, p.user_id, p.amount, p.method, p.status, 
                   p.created_at, p.screenshot, p.approved_by, p.approved_at,
                   u.username, u.full_name
            FROM payments p
            LEFT JOIN users u ON p.user_id = u.user_id
        """
        
        count_query = "SELECT COUNT(*) FROM payments p"
        params = []
        
        if status:
            where = " WHERE p.status = ?"
            base_query += where
            count_query += where
            params.append(status)
        
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        base_query += " ORDER BY p.id DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(base_query, params)
        payments = []
        for row in cursor.fetchall():
            payments.append({
                "id": row[0],
                "user_id": row[1],
                "amount": row[2],
                "method": row[3],
                "status": row[4],
                "created_at": row[5],
                "screenshot": row[6],
                "approved_by": row[7],
                "approved_at": row[8],
                "username": row[9],
                "full_name": row[10]
            })
        
        return {
            "success": True,
            "data": {
                "payments": payments,
                "total": total,
                "page": page,
                "pages": (total + limit - 1) // limit
            }
        }
        
    finally:
        conn.close()


@router.post("/payments/{payment_id}/approve")
async def approve_payment(payment_id: int, admin_id: int = Depends(verify_admin)):
    """To'lovni tasdiqlash"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # To'lov ma'lumoti
        cursor.execute("SELECT user_id, amount, status FROM payments WHERE id = ?", (payment_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="To'lov topilmadi")
        
        user_id, amount, status = row
        
        if status != "pending":
            raise HTTPException(status_code=400, detail="Bu to'lov allaqachon ko'rib chiqilgan")
        
        # Balansni qo'shish
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
        
        # To'lov statusini yangilash
        cursor.execute("""
            UPDATE payments 
            SET status = 'approved', approved_by = ?, approved_at = ?
            WHERE id = ?
        """, (admin_id, datetime.now().isoformat(), payment_id))
        
        conn.commit()
        
        return {
            "success": True,
            "message": f"To'lov tasdiqlandi. {amount:,.0f} so'm qo'shildi."
        }
        
    finally:
        conn.close()


@router.post("/payments/{payment_id}/reject")
async def reject_payment(payment_id: int, admin_id: int = Depends(verify_admin)):
    """To'lovni rad etish"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT status FROM payments WHERE id = ?", (payment_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="To'lov topilmadi")
        
        if row[0] != "pending":
            raise HTTPException(status_code=400, detail="Bu to'lov allaqachon ko'rib chiqilgan")
        
        cursor.execute("""
            UPDATE payments 
            SET status = 'rejected', approved_by = ?, approved_at = ?
            WHERE id = ?
        """, (admin_id, datetime.now().isoformat(), payment_id))
        
        conn.commit()
        
        return {"success": True, "message": "To'lov rad etildi"}
        
    finally:
        conn.close()


# ==================== SETTINGS ====================

@router.get("/settings")
async def get_settings(admin_id: int = Depends(verify_admin)):
    """Sozlamalarni olish"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT key, value FROM settings")
        settings = dict(cursor.fetchall())
        
        return {
            "success": True,
            "data": settings
        }
        
    except sqlite3.OperationalError:
        return {"success": True, "data": {}}
        
    finally:
        conn.close()


@router.put("/settings")
async def update_settings(settings: dict, admin_id: int = Depends(verify_admin)):
    """Sozlamalarni yangilash"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        for key, value in settings.items():
            cursor.execute("""
                INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)
            """, (key, str(value)))
        
        conn.commit()
        
        return {"success": True, "message": "Sozlamalar saqlandi"}
        
    finally:
        conn.close()


# ==================== BROADCAST ====================

@router.post("/broadcast")
async def send_broadcast(
    message: str,
    admin_id: int = Depends(verify_admin)
):
    """Ommaviy xabar yuborish (faqat ma'lumot)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_blocked = 0 OR is_blocked IS NULL")
        active_users = cursor.fetchone()[0]
        
        return {
            "success": True,
            "message": "Ommaviy xabar botda yuboriladi",
            "data": {
                "active_users": active_users,
                "note": "Bot orqali /broadcast komandasidan foydalaning"
            }
        }
        
    finally:
        conn.close()
