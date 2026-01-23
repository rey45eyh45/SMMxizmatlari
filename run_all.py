#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SMM Bot + Mini App API - Combined Runner
Bot va API ni bitta process'da ishga tushiradi
"""
import asyncio
import logging
import os
import threading
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_api():
    """FastAPI serverni ishga tushirish"""
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    logger.info(f"🌐 API server port {port} da ishga tushmoqda...")
    
    config = uvicorn.Config(
        "api.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )
    server = uvicorn.Server(config)
    server.run()


def run_bot_polling():
    """Telegram bot'ni polling rejimida ishga tushirish"""
    try:
        # Bot modulini FAQAT shu yerda import qilish
        logger.info("🤖 Bot moduli import qilinmoqda...")
        from main import bot, dp, router
        
        logger.info("🤖 Bot polling boshlanmoqda...")
        
        # Router allaqachon main.py da ulangan, qayta ulamaslik kerak!
        # dp.include_router(router)  # BU KERAK EMAS!
        
        # Polling boshlash
        asyncio.run(dp.start_polling(bot))
    except Exception as e:
        logger.error(f"❌ Bot xatosi: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Asosiy funksiya - API va bot ni birga ishga tushirish"""
    logger.info("🚀 SMM Bot + API ishga tushmoqda...")
    
    port = os.getenv("PORT")
    logger.info(f"📌 PORT env: {port}")
    
    if port:
        # Railway rejimi
        logger.info(f"✅ Railway mode - PORT={port}")
        
        # 1. Bot'ni ALOHIDA thread'da ishga tushirish (daemon=True)
        bot_thread = threading.Thread(target=run_bot_polling, daemon=True)
        bot_thread.start()
        logger.info("✅ Bot thread boshlandi")
        
        # 2. Biroz kutish
        time.sleep(2)
        
        # 3. API ni ASOSIY thread'da ishga tushirish (Railway uchun MUHIM!)
        logger.info("✅ API server boshlanmoqda (asosiy thread)...")
        run_api()
        
    else:
        # Local rejim
        logger.info("✅ Local mode - PORT=8000")
        
        # API ni background'da
        api_thread = threading.Thread(target=run_api, daemon=True)
        api_thread.start()
        
        time.sleep(2)
        
        # Bot ni asosiy thread'da
        run_bot_polling()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("👋 Dastur to'xtatildi")
