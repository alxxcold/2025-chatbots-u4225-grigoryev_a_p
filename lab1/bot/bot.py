#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram-бот для команды Commitly
Бот-помощник с функциями информации о компании, контактами и напоминаниями
"""

import logging
import json
import os
import random
import asyncio
from datetime import datetime, time, timezone, timedelta
from typing import Dict, Any

from telegram import Update
from telegram.ext import (
    Application, 
    CommandHandler, 
    ContextTypes,
    CallbackContext
)
from telegram.constants import ParseMode
import pytz
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Дополнительное логирование для отладки
logging.getLogger('telegram').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)

# Конфигурация
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения!")

# Часовой пояс для МСК
MSK_TZ = pytz.timezone('Europe/Moscow')

# Файл для хранения данных
DATA_FILE = 'bot_data.json'

# Импорт мотивирующих цитат
from quotes import get_random_quote

def load_data() -> Dict[str, Any]:
    """Загружает данные из JSON файла"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Ошибка при загрузке данных: {e}")
        return {}

def save_data(data: Dict[str, Any]) -> None:
    """Сохраняет данные в JSON файл"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка при сохранении данных: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    try:
        welcome_message = """
🤖 Добро пожаловать в бот-помощник команды Commitly!

Доступные команды:
/about - информация о компании
/contacts - контакты команды
/help - справка по командам

Бот будет напоминать о важных событиях и мотивировать вас каждый день! 🚀
        """
        await update.message.reply_text(welcome_message)
        logger.info(f"Пользователь {update.effective_user.id} запустил бота")
    except Exception as e:
        logger.error(f"Ошибка в команде start: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /about - информация о компании"""
    try:
        logger.info(f"Пользователь {update.effective_user.id} запросил информацию о компании")
        
        about_text = """*Commitly* — это B2B-платформа для обучения программистов через геймификацию.

• Программисты как обычно пишут код и проходят тесты: юнит, функциональное тестирование, нагрузочное, тесты по безопасности и тд

• Платформа автоматически генерирует для них персонализированные обучающие игры.

• Обучение фокусируется на изучении новых технологий через практику, адаптированные под уровень и цели пользователя с помощью AI.

• Система включает постоянный конкурентный режим с рейтингами, наградами и лидерами, что мотивирует сотрудников учиться активнее."""
        
        await update.message.reply_text(about_text, parse_mode=ParseMode.MARKDOWN)
        logger.info(f"Информация о компании успешно отправлена пользователю {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"Ошибка в команде about: {e}", exc_info=True)
        try:
            # Fallback без Markdown
            fallback_text = """Commitly — это B2B-платформа для обучения программистов через геймификацию.

Программисты как обычно пишут код и проходят тесты: юнит, функциональное тестирование, нагрузочное, тесты по безопасности и тд

Платформа автоматически генерирует для них персонализированные обучающие игры.

Обучение фокусируется на изучении новых технологий через практику, адаптированные под уровень и цели пользователя с помощью AI.

Система включает постоянный конкурентный режим с рейтингами, наградами и лидерами, что мотивирует сотрудников учиться активнее."""
            await update.message.reply_text(fallback_text)
        except Exception as fallback_error:
            logger.error(f"Критическая ошибка при отправке fallback сообщения: {fallback_error}")
            await update.message.reply_text("Произошла ошибка. Попробуйте позже.")

async def contacts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /contacts - контакты команды"""
    try:
        logger.info(f"Пользователь {update.effective_user.id} запросил контакты")
        
        # Простой текст без Markdown для избежания ошибок форматирования
        contacts_text = """📞 Контакты команды:

👨‍💻 Алексей: @alxxcold
👨‍💻 Даниил: @D_Korr

Свяжитесь с нами для любых вопросов! 💬"""
        
        await update.message.reply_text(contacts_text)
        logger.info(f"Контакты успешно отправлены пользователю {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"Ошибка в команде contacts: {e}", exc_info=True)
        try:
            # Fallback - отправляем простой текст без эмодзи
            fallback_text = "Контакты команды:\nАлексей: @alxxcold\nДаниил: @D_Korr"
            await update.message.reply_text(fallback_text)
        except Exception as fallback_error:
            logger.error(f"Критическая ошибка при отправке fallback сообщения: {fallback_error}")
            await update.message.reply_text("Произошла ошибка. Попробуйте позже.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help"""
    try:
        logger.info(f"Пользователь {update.effective_user.id} запросил справку")
        
        help_text = """🆘 Справка по командам:

/start - запуск бота
/about - информация о компании Commitly
/contacts - контакты команды
/help - эта справка
/test - тест отправки сообщений
/test_reminders - ручной тест напоминаний

🤖 Автоматические функции:
• Напоминания о встречах (вторник, четверг)
• Ежедневные мотивирующие цитаты"""
        
        await update.message.reply_text(help_text)
        logger.info(f"Справка успешно отправлена пользователю {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"Ошибка в команде help: {e}", exc_info=True)
        try:
            # Fallback без эмодзи
            fallback_text = """Справка по командам:

/start - запуск бота
/about - информация о компании Commitly
/contacts - контакты команды
/help - эта справка
/test - тест отправки сообщений
/test_reminders - ручной тест напоминаний

Автоматические функции:
• Напоминания о встречах (вторник, четверг)
• Ежедневные мотивирующие цитаты"""
            await update.message.reply_text(fallback_text)
        except Exception as fallback_error:
            logger.error(f"Критическая ошибка при отправке fallback сообщения: {fallback_error}")
            await update.message.reply_text("Произошла ошибка. Попробуйте позже.")

async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /test - тест отправки сообщений"""
    try:
        logger.info(f"Пользователь {update.effective_user.id} запросил тест")
        
        # Отправляем тестовое сообщение
        test_message = """🧪 Тест отправки сообщений

Если вы видите это сообщение, значит:
✅ Бот работает правильно
✅ Сообщения доставляются
✅ Напоминания будут приходить вовремя

Время теста: {time}""".format(time=datetime.now(MSK_TZ).strftime("%H:%M:%S %d.%m.%Y"))
        
        await update.message.reply_text(test_message)
        logger.info(f"Тестовое сообщение отправлено пользователю {update.effective_user.id}")
        
        # Тест мотивирующей цитаты
        await asyncio.sleep(1)
        quote = get_random_quote()
        quote_message = f"💫 Тест мотивации:\n\n{quote}"
        await update.message.reply_text(quote_message)
        logger.info(f"Тестовая цитата отправлена пользователю {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"Ошибка в команде test: {e}", exc_info=True)
        await update.message.reply_text("Ошибка при тестировании. Проверьте логи.")

async def test_reminders_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /test_reminders - ручной запуск напоминаний"""
    try:
        logger.info(f"Пользователь {update.effective_user.id} запросил тест напоминаний")
        
        await update.message.reply_text("🧪 Запуск теста напоминаний...")
        
        # Запускаем все функции напоминаний
        await send_motivational_quote(context.bot)
        await asyncio.sleep(1)
        await remind_meeting_preparation(context.bot)
        await asyncio.sleep(1)
        await remind_meeting_start(context.bot)
        
        await update.message.reply_text("✅ Тест напоминаний завершен! Проверьте логи.")
        
    except Exception as e:
        logger.error(f"Ошибка в команде test_reminders: {e}", exc_info=True)
        await update.message.reply_text("Ошибка при тестировании напоминаний. Проверьте логи.")

async def send_motivational_quote(bot) -> None:
    """Отправляет мотивирующую цитату всем пользователям"""
    try:
        data = load_data()
        users = data.get('users', [])
        
        if not users:
            logger.info("Нет пользователей для отправки мотивирующей цитаты")
            return
            
        quote = get_random_quote()
        success_count = 0
        
        for user_id in users:
            try:
                # Отправляем без Markdown для избежания ошибок
                message_text = f"💫 Мотивация дня:\n\n{quote}"
                await bot.send_message(
                    chat_id=user_id,
                    text=message_text
                )
                success_count += 1
                logger.info(f"Мотивирующая цитата отправлена пользователю {user_id}")
            except Exception as e:
                logger.error(f"Ошибка отправки цитаты пользователю {user_id}: {e}")
                # Пробуем отправить без эмодзи
                try:
                    simple_quote = quote.replace("🚀", "").replace("💡", "").replace("⚡", "").replace("🎯", "").replace("🔥", "").replace("🌟", "").replace("💪", "").replace("🎨", "").replace("⭐", "").replace("🎪", "").replace("🏆", "").replace("🎵", "").replace("🌈", "").replace("🎭", "")
                    await bot.send_message(
                        chat_id=user_id,
                        text=f"Мотивация дня:\n\n{simple_quote}"
                    )
                    success_count += 1
                    logger.info(f"Мотивирующая цитата (упрощенная) отправлена пользователю {user_id}")
                except Exception as e2:
                    logger.error(f"Критическая ошибка отправки цитаты пользователю {user_id}: {e2}")
        
        logger.info(f"Отправлена мотивирующая цитата {success_count} из {len(users)} пользователям")
    except Exception as e:
        logger.error(f"Ошибка при отправке мотивирующих цитат: {e}", exc_info=True)

async def remind_meeting_preparation(bot) -> None:
    """Напоминает о подготовке к встрече (вторник 19:30)"""
    try:
        data = load_data()
        users = data.get('users', [])
        
        if not users:
            logger.info("Нет пользователей для напоминания о подготовке к встрече")
            return
            
        success_count = 0
        
        for user_id in users:
            try:
                # Отправляем без Markdown для избежания ошибок
                message = """📅 Напоминание о встрече!

Завтра (среда) в 18:50 начинается встреча по проекту! 

⏰ Время подготовки: сегодня в 19:32
🎯 Не забудьте подготовить отчеты и вопросы!

Удачи! 🚀"""
                
                await bot.send_message(
                    chat_id=user_id,
                    text=message
                )
                success_count += 1
                logger.info(f"Напоминание о подготовке к встрече отправлено пользователю {user_id}")
            except Exception as e:
                logger.error(f"Ошибка отправки напоминания пользователю {user_id}: {e}")
                # Пробуем отправить упрощенную версию
                try:
                    simple_message = """Напоминание о встрече!

Завтра (среда) в 18:50 начинается встреча по проекту! 

Время подготовки: сегодня в 19:30
Не забудьте подготовить отчеты и вопросы!

Удачи!"""
                    await bot.send_message(
                        chat_id=user_id,
                        text=simple_message
                    )
                    success_count += 1
                    logger.info(f"Напоминание о подготовке (упрощенное) отправлено пользователю {user_id}")
                except Exception as e2:
                    logger.error(f"Критическая ошибка отправки напоминания пользователю {user_id}: {e2}")
        
        logger.info(f"Отправлено напоминание о подготовке к встрече {success_count} из {len(users)} пользователям")
    except Exception as e:
        logger.error(f"Ошибка при отправке напоминания о подготовке: {e}", exc_info=True)

async def remind_meeting_start(bot) -> None:
    """Напоминает о начале встречи (четверг 18:50)"""
    try:
        data = load_data()
        users = data.get('users', [])
        
        if not users:
            logger.info("Нет пользователей для напоминания о встрече")
            return
            
        success_count = 0
        
        for user_id in users:
            try:
                # Отправляем без Markdown для избежания ошибок
                message = """🚀 Встреча начинается!

Сейчас (18:50) начинается встреча по проекту!

📋 Готовьтесь к обсуждению:
• Текущие задачи
• Проблемы и решения
• Планы на следующую неделю

Удачной встречи! 💪"""
                
                await bot.send_message(
                    chat_id=user_id,
                    text=message
                )
                success_count += 1
                logger.info(f"Напоминание о встрече отправлено пользователю {user_id}")
            except Exception as e:
                logger.error(f"Ошибка отправки напоминания о встрече пользователю {user_id}: {e}")
                # Пробуем отправить упрощенную версию
                try:
                    simple_message = """Встреча начинается!

Сейчас (18:50) начинается встреча по проекту!

Готовьтесь к обсуждению:
• Текущие задачи
• Проблемы и решения
• Планы на следующую неделю

Удачной встречи!"""
                    await bot.send_message(
                        chat_id=user_id,
                        text=simple_message
                    )
                    success_count += 1
                    logger.info(f"Напоминание о встрече (упрощенное) отправлено пользователю {user_id}")
                except Exception as e2:
                    logger.error(f"Критическая ошибка отправки напоминания о встрече пользователю {user_id}: {e2}")
        
        logger.info(f"Отправлено напоминание о встрече {success_count} из {len(users)} пользователям")
    except Exception as e:
        logger.error(f"Ошибка при отправке напоминания о встрече: {e}", exc_info=True)

async def test_scheduled_message(bot) -> None:
    """Тестовая функция для проверки работы планировщика"""
    try:
        logger.info("🧪 Тестовая задача выполняется - планировщик работает!")
        
        data = load_data()
        users = data.get('users', [])
        
        if not users:
            logger.info("Нет пользователей для тестового сообщения")
            return
            
        test_message = "🧪 Тест планировщика!\n\nЕсли вы получили это сообщение, значит периодические задачи работают правильно!"
        
        success_count = 0
        for user_id in users:
            try:
                await bot.send_message(
                    chat_id=user_id,
                    text=test_message
                )
                success_count += 1
                logger.info(f"Тестовое сообщение отправлено пользователю {user_id}")
            except Exception as e:
                logger.error(f"Ошибка отправки тестового сообщения пользователю {user_id}: {e}")
        
        logger.info(f"Тестовая задача завершена. Отправлено {success_count} из {len(users)} сообщений")
        
    except Exception as e:
        logger.error(f"Ошибка в тестовой задаче: {e}", exc_info=True)

async def track_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отслеживает пользователей для отправки напоминаний"""
    try:
        user_id = update.effective_user.id
        data = load_data()
        
        if 'users' not in data:
            data['users'] = []
            
        if user_id not in data['users']:
            data['users'].append(user_id)
            save_data(data)
            logger.info(f"Добавлен новый пользователь: {user_id}")
    except Exception as e:
        logger.error(f"Ошибка при отслеживании пользователя: {e}")

# ...existing code...

async def test_scheduled_message(bot) -> None:
    """Тестовая функция для проверки работы планировщика"""
    try:
        logger.info("🧪 Тестовая задача выполняется - планировщик работает!")
        
        data = load_data()
        users = data.get('users', [])
        
        if not users:
            logger.info("Нет пользователей для тестового сообщения")
            return
            
        test_message = "🧪 Тест планировщика!\n\nЕсли вы получили это сообщение, значит периодические задачи работают правильно!"
        
        success_count = 0
        for user_id in users:
            try:
                await bot.send_message(
                    chat_id=user_id,
                    text=test_message
                )
                success_count += 1
                logger.info(f"Тестовое сообщение отправлено пользователю {user_id}")
            except Exception as e:
                logger.error(f"Ошибка отправки тестового сообщения пользователю {user_id}: {e}")
        
        logger.info(f"Тестовая задача завершена. Отправлено {success_count} из {len(users)} сообщений")
        
    except Exception as e:
        logger.error(f"Ошибка в тестовой задаче: {e}", exc_info=True)

# ...existing code...

async def track_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отслеживает пользователей для отправки напоминаний"""
    try:
        user_id = update.effective_user.id
        data = load_data()
        
        if 'users' not in data:
            data['users'] = []
            
        if user_id not in data['users']:
            data['users'].append(user_id)
            save_data(data)
            logger.info(f"Добавлен новый пользователь: {user_id}")
    except Exception as e:
        logger.error(f"Ошибка при отслеживании пользователя: {e}")

# Новая функция: цикл отправки мотиваций каждые 30 секунд (для отладки)
async def _motivation_30s_loop(bot) -> None:
    """Отправляет мотивирующие цитаты всем пользователям каждые 30 секунд (тестовый режим)"""
    while True:
        try:
            logger.info("Запуск цикла тестовой мотивации (каждые 30 секунд)")
            await send_motivational_quote(bot)
        except Exception as e:
            logger.error(f"Ошибка в цикле мотивации (30с): {e}", exc_info=True)
        await asyncio.sleep(30)

# Старая функция setup_jobs удалена - используется SimpleScheduler

def main() -> None:
    """Основная функция запуска бота"""
    try:
        # Создание приложения без JobQueue для совместимости с Python 3.13
        from telegram.ext import ApplicationBuilder
        
        application = (
            ApplicationBuilder()
            .token(BOT_TOKEN)
            .concurrent_updates(True)
            .job_queue(None)  # Отключаем JobQueue
            .build()
        )
        
        # Добавление обработчиков команд
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("about", about))
        application.add_handler(CommandHandler("contacts", contacts))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("test", test_command))
        application.add_handler(CommandHandler("test_reminders", test_reminders_command))
        
        # Добавление обработчика для отслеживания пользователей
        application.add_handler(CommandHandler("start", track_user), group=1)
        application.add_handler(CommandHandler("about", track_user), group=1)
        application.add_handler(CommandHandler("contacts", track_user), group=1)
        application.add_handler(CommandHandler("help", track_user), group=1)
        application.add_handler(CommandHandler("test", track_user), group=1)
        application.add_handler(CommandHandler("test_reminders", track_user), group=1)
        
        # Настройка простого планировщика задач
        try:
            from simple_scheduler import SimpleScheduler
            scheduler = SimpleScheduler(application.bot, MSK_TZ)
            
            # Добавляем задачи
            scheduler.add_daily_task(
                send_motivational_quote,
                time(19, 30),
                name="daily_motivation"
            )
            
            scheduler.add_daily_task(
                remind_meeting_preparation,
                time(19, 32),
                days=(1,),  # вторник
                name="meeting_prep_reminder"
            )
            
            scheduler.add_daily_task(
                remind_meeting_start,
                time(18, 50),
                days=(3,),  # четверг
                name="meeting_start_reminder"
            )
            
            # Тестовая задача через 1 минуту
            current_time = datetime.now(MSK_TZ)
            test_time = current_time + timedelta(minutes=1)
            scheduler.add_one_time_task(
                test_scheduled_message,
                test_time,
                name="test_scheduled"
            )
            
            # Запускаем планировщик
            asyncio.create_task(scheduler.start())
            logger.info("Простой планировщик задач настроен и запущен")
            
        except Exception as e:
            logger.warning(f"Не удалось настроить планировщик задач: {e}")
            logger.info("Бот будет работать без автоматических напоминаний")
        
        # Запускаем тестовый цикл мотиваций каждые 30 секунд (для отладки)
        try:
            application.create_task(_motivation_30s_loop(application.bot))
            logger.info("Запущен цикл мотиваций (30s) для тестирования")
        except Exception as e:
            logger.warning(f"Не удалось запустить цикл мотиваций: {e}")
        
        # Запуск бота
        logger.info("Запуск бота...")
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
        
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске бота: {e}")
        raise

if __name__ == '__main__':
    main()

if __name__ == '__main__':
    main()
