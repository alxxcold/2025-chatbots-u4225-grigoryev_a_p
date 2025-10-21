#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки команд бота
"""

import asyncio
import logging
from bot import start, about, contacts, help_command

# Настройка логирования для тестов
logging.basicConfig(level=logging.INFO)

class MockMessage:
    def __init__(self):
        self.text = ""
    
    async def reply_text(self, text, parse_mode=None):
        print(f"\n{'='*50}")
        print(f"ОТПРАВЛЕНО СООБЩЕНИЕ:")
        print(f"{'='*50}")
        print(text)
        print(f"{'='*50}")
        return True

class MockUser:
    def __init__(self, user_id=123):
        self.id = user_id
        self.is_bot = False
        self.first_name = "Test"
        self.username = "testuser"

class MockUpdate:
    def __init__(self, user_id=123):
        self.message = MockMessage()
        self.effective_user = MockUser(user_id)

class MockContext:
    pass

async def test_all_commands():
    """Тестирует все команды бота"""
    print("🤖 Тестирование команд Telegram-бота...")
    
    context = MockContext()
    
    # Тест команды /start
    print("\n1. Тестирование команды /start:")
    update = MockUpdate(1)
    try:
        await start(update, context)
        print("✅ Команда /start работает")
    except Exception as e:
        print(f"❌ Ошибка в команде /start: {e}")
    
    # Тест команды /about
    print("\n2. Тестирование команды /about:")
    update = MockUpdate(2)
    try:
        await about(update, context)
        print("✅ Команда /about работает")
    except Exception as e:
        print(f"❌ Ошибка в команде /about: {e}")
    
    # Тест команды /contacts
    print("\n3. Тестирование команды /contacts:")
    update = MockUpdate(3)
    try:
        await contacts(update, context)
        print("✅ Команда /contacts работает")
    except Exception as e:
        print(f"❌ Ошибка в команде /contacts: {e}")
    
    # Тест команды /help
    print("\n4. Тестирование команды /help:")
    update = MockUpdate(4)
    try:
        await help_command(update, context)
        print("✅ Команда /help работает")
    except Exception as e:
        print(f"❌ Ошибка в команде /help: {e}")
    
    print("\n🎉 Тестирование завершено!")

if __name__ == "__main__":
    asyncio.run(test_all_commands())
