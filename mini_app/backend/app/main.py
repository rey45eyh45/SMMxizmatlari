# -*- coding: utf-8 -*-
"""
SMM Mini App - FastAPI Backend
Asosiy kirish nuqtasi
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import CORS_ORIGINS
from .routers import auth, user, services, orders, payments, sms
from .routers import click as click_router
from .database import Database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle"""
    # Startup
    print("🚀 SMM Mini App Backend ishga tushmoqda...")
    # Click to'lovlar jadvalini yaratish
    Database.init_click_payments_table()
    yield
    # Shutdown
    print("👋 SMM Mini App Backend to'xtatilmoqda...")


# FastAPI ilovasi
app = FastAPI(
    title="SMM Mini App API",
    description="Telegram Mini App uchun SMM xizmatlari API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da CORS_ORIGINS ishlatiladi
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routerlar
app.include_router(auth.router, prefix="/api")
app.include_router(user.router, prefix="/api")
app.include_router(services.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(payments.router, prefix="/api")
app.include_router(sms.router, prefix="/api")
app.include_router(click_router.router, prefix="/api")

# Admin panel router
from .routers import admin as admin_router
app.include_router(admin_router.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "SMM Mini App API",
        "version": "1.0.0",
        "status": "active",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/api/settings")
async def get_public_settings():
    """Umumiy sozlamalarni olish"""
    from .database import Database
    
    return {
        "usd_rate": int(Database.get_setting("usd_rate", "12900")),
        "rub_rate": int(Database.get_setting("rub_rate", "140")),
        "min_deposit": int(Database.get_setting("min_deposit", "5000")),
        "referral_bonus": int(Database.get_setting("referral_bonus", "500"))
    }
