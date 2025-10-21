#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для проверки работы планировщика задач
"""

import asyncio
import logging
from datetime import datetime, time, timedelta
import pytz
from bot import load_data, save_data

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MSK_TZ = pytz.timezone('Europe/Moscow')

def check_scheduler_status():
    """Проверяет статус планировщика и пользователей"""
    print("🔍 Проверка статуса планировщика...")
    
    # Проверяем данные пользователей
    data = load_data()
    users = data.get('users', [])
    
    print(f"📊 Пользователей в базе: {len(users)}")
    if users:
        print(f"👥 ID пользователей: {users}")
    else:
        print("⚠️ Нет пользователей! Добавьте тестового пользователя.")
        test_user_id = input("Введите ваш Telegram user_id для тестирования: ").strip()
        if test_user_id:
            try:
                test_user_id = int(test_user_id)
                data['users'] = [test_user_id]
                save_data(data)
                print(f"✅ Добавлен тестовый пользователь: {test_user_id}")
            except ValueError:
                print("❌ Неверный формат user_id")
    
    # Проверяем текущее время
    current_time = datetime.now(MSK_TZ)
    print(f"🕐 Текущее время (МСК): {current_time.strftime('%H:%M:%S %d.%m.%Y')}")
    
    # Показываем расписание
    print("\n📅 Расписание напоминаний:")
    print("• Ежедневно в 19:20 - мотивирующие цитаты")
    print("• Вторник в 19:18 - напоминание о подготовке к встрече")
    print("• Четверг в 18:50 - напоминание о начале встречи")
    
    # Проверяем, когда будет следующее напоминание
    current_weekday = current_time.weekday()  # 0=понедельник, 1=вторник, ..., 6=воскресенье
    
    print(f"\n📆 Текущий день недели: {['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'][current_weekday]}")
    
    # Следующая мотивирующая цитата
    today_motivation = current_time.replace(hour=19, minute=20, second=0, microsecond=0)
    if current_time < today_motivation:
        print(f"⏰ Следующая мотивирующая цитата: сегодня в {today_motivation.strftime('%H:%M')}")
    else:
        tomorrow_motivation = current_time.replace(hour=19, minute=20, second=0, microsecond=0) + timedelta(days=1)
        print(f"⏰ Следующая мотивирующая цитата: завтра в {tomorrow_motivation.strftime('%H:%M')}")
    
    # Следующее напоминание о подготовке (вторник)
    if current_weekday == 1:  # вторник
        today_prep = current_time.replace(hour=19, minute=18, second=0, microsecond=0)
        if current_time < today_prep:
            print(f"⏰ Напоминание о подготовке: сегодня в {today_prep.strftime('%H:%M')}")
        else:
            print("⏰ Напоминание о подготовке: уже прошло сегодня")
    else:
        days_until_tuesday = (1 - current_weekday) % 7
        if days_until_tuesday == 0:
            days_until_tuesday = 7
        next_tuesday = current_time + timedelta(days=days_until_tuesday)
        next_tuesday = next_tuesday.replace(hour=19, minute=18, second=0, microsecond=0)
        print(f"⏰ Следующее напоминание о подготовке: {next_tuesday.strftime('%d.%m.%Y в %H:%M')}")
    
    # Следующее напоминание о встрече (четверг)
    if current_weekday == 3:  # четверг
        today_meeting = current_time.replace(hour=18, minute=50, second=0, microsecond=0)
        if current_time < today_meeting:
            print(f"⏰ Напоминание о встрече: сегодня в {today_meeting.strftime('%H:%M')}")
        else:
            print("⏰ Напоминание о встрече: уже прошло сегодня")
    else:
        days_until_thursday = (3 - current_weekday) % 7
        if days_until_thursday == 0:
            days_until_thursday = 7
        next_thursday = current_time + timedelta(days=days_until_thursday)
        next_thursday = next_thursday.replace(hour=18, minute=50, second=0, microsecond=0)
        print(f"⏰ Следующее напоминание о встрече: {next_thursday.strftime('%d.%m.%Y в %H:%M')}")

if __name__ == "__main__":
    check_scheduler_status()
