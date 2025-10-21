#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки запуска бота
"""

import logging
import os
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_bot_startup():
    """Тестирует запуск бота"""
    print("🔍 Тестирование запуска бота...")
    
    # Проверяем .env файл
    load_dotenv()
    bot_token = os.getenv('BOT_TOKEN')
    
    if not bot_token:
        print("❌ BOT_TOKEN не найден в .env файле!")
        return False
    
    print(f"✅ BOT_TOKEN найден: {bot_token[:10]}...")
    
    # Проверяем импорты
    try:
        from bot import main
        print("✅ Импорт bot.py успешен")
    except Exception as e:
        print(f"❌ Ошибка импорта bot.py: {e}")
        return False
    
    try:
        from simple_scheduler import SimpleScheduler
        print("✅ Импорт SimpleScheduler успешен")
    except Exception as e:
        print(f"❌ Ошибка импорта SimpleScheduler: {e}")
        return False
    
    # Проверяем создание приложения
    try:
        from telegram.ext import ApplicationBuilder
        from telegram import Bot
        
        bot = Bot(token=bot_token)
        application = ApplicationBuilder().token(bot_token).job_queue(None).build()
        print("✅ Создание Application успешно")
        
        # Проверяем SimpleScheduler
        scheduler = SimpleScheduler(application.bot, None)
        print("✅ Создание SimpleScheduler успешно")
        
    except Exception as e:
        print(f"❌ Ошибка создания приложения: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("🎉 Все тесты прошли успешно! Бот готов к запуску.")
    return True

if __name__ == "__main__":
    test_bot_startup()
