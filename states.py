# -*- coding: utf-8 -*-
"""
STATES - Bot holatlari (FSM States)
"""
from aiogram.dispatcher.filters.state import State, StatesGroup


class OrderState(StatesGroup):
    """SMM Buyurtma holatlari"""
    waiting_for_link = State()
    waiting_for_quantity = State()
    confirm_order = State()


class PaymentState(StatesGroup):
    """To'lov holatlari"""
    waiting_for_amount = State()
    waiting_for_screenshot = State()


class SMSState(StatesGroup):
    """SMS holatlari"""
    waiting_for_sms = State()


class AdminState(StatesGroup):
    """Admin holatlari"""
    waiting_for_broadcast = State()
    waiting_for_user_id = State()
    waiting_for_balance_amount = State()
    waiting_for_ban_reason = State()


class PhoneAuthState(StatesGroup):
    """Telefon raqam orqali autentifikatsiya"""
    waiting_for_phone = State()
