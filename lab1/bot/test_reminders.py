#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки отправки напоминаний
"""

import asyncio
import logging
from bot import send_motivational_quote, remind_meeting_preparation, remind_meeting_start, load_data, save_data

# Настройка логирования
logging.basicConfig(level=logging.INFO)

class MockBot:
    def __init__(self):
        self.sent_messages = []
    
    async def send_message(self, chat_id, text, parse_mode=None):
        print(f"\n{'='*60}")
        print(f"ОТПРАВКА СООБЩЕНИЯ:")
        print(f"Получатель: {chat_id}")
        print(f"Текст: {text}")
        print(f"{'='*60}")
        self.sent_messages.append({
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode
        })
        return True

class MockContext:
    def __init__(self):
        self.bot = MockBot()

async def test_reminders():
    """Тестирует отправку напоминаний"""
    print("🤖 Тестирование отправки напоминаний...")
    
    # Добавляем тестового пользователя
    test_user_id = 123456789
    data = {'users': [test_user_id]}
    save_data(data)
    print(f"✅ Добавлен тестовый пользователь: {test_user_id}")
    
    context = MockContext()
    
    # Тест мотивирующих цитат
    print("\n1. Тестирование мотивирующих цитат:")
    try:
        await send_motivational_quote(context)
        print("✅ Мотивирующие цитаты работают")
    except Exception as e:
        print(f"❌ Ошибка в мотивирующих цитатах: {e}")
    
    # Тест напоминания о подготовке к встрече
    print("\n2. Тестирование напоминания о подготовке к встрече:")
    try:
        await remind_meeting_preparation(context)
        print("✅ Напоминание о подготовке к встрече работает")
    except Exception as e:
        print(f"❌ Ошибка в напоминании о подготовке: {e}")
    
    # Тест напоминания о начале встречи
    print("\n3. Тестирование напоминания о начале встречи:")
    try:
        await remind_meeting_start(context)
        print("✅ Напоминание о начале встречи работает")
    except Exception as e:
        print(f"❌ Ошибка в напоминании о встрече: {e}")
    
    print(f"\n📊 Статистика: отправлено {len(context.bot.sent_messages)} сообщений")
    print("🎉 Тестирование завершено!")

if __name__ == "__main__":
    asyncio.run(test_reminders())
