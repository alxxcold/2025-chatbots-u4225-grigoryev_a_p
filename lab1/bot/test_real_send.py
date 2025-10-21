#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для тестирования отправки сообщений реальному пользователю
"""

import asyncio
import logging
import os
from telegram import Bot
from telegram.error import TelegramError
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)

async def test_real_send():
    """Тестирует отправку сообщения реальному пользователю"""
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        print("❌ BOT_TOKEN не найден в .env файле!")
        return
    
    # Замените на ваш реальный user_id
    test_user_id = input("Введите ваш Telegram user_id (или нажмите Enter для пропуска): ").strip()
    
    if not test_user_id:
        print("⚠️ Пропуск теста отправки реальному пользователю")
        return
    
    try:
        test_user_id = int(test_user_id)
    except ValueError:
        print("❌ Неверный формат user_id. Должно быть число.")
        return
    
    bot = Bot(token=bot_token)
    
    try:
        # Тест простого сообщения
        print(f"📤 Отправка тестового сообщения пользователю {test_user_id}...")
        await bot.send_message(
            chat_id=test_user_id,
            text="🤖 Тестовое сообщение от бота!\n\nЕсли вы получили это сообщение, значит бот работает правильно!"
        )
        print("✅ Сообщение успешно отправлено!")
        
        # Тест с эмодзи
        print("📤 Отправка сообщения с эмодзи...")
        await bot.send_message(
            chat_id=test_user_id,
            text="💫 Мотивация дня:\n\n🚀 Код — это поэзия, написанная на языке логики!"
        )
        print("✅ Сообщение с эмодзи успешно отправлено!")
        
        # Тест длинного сообщения
        print("📤 Отправка длинного сообщения...")
        await bot.send_message(
            chat_id=test_user_id,
            text="""📅 Напоминание о встрече!

Завтра (среда) в 18:50 начинается встреча по проекту! 

⏰ Время подготовки: сегодня в 19:05
🎯 Не забудьте подготовить отчеты и вопросы!

Удачи! 🚀"""
        )
        print("✅ Длинное сообщение успешно отправлено!")
        
        print("\n🎉 Все тесты прошли успешно! Бот работает правильно.")
        
    except TelegramError as e:
        print(f"❌ Ошибка Telegram API: {e}")
        if "chat not found" in str(e).lower():
            print("💡 Возможные причины:")
            print("   - Пользователь не запускал бота командой /start")
            print("   - Неверный user_id")
            print("   - Пользователь заблокировал бота")
        elif "bot was blocked" in str(e).lower():
            print("💡 Пользователь заблокировал бота")
        elif "forbidden" in str(e).lower():
            print("💡 У бота нет прав для отправки сообщений этому пользователю")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(test_real_send())
