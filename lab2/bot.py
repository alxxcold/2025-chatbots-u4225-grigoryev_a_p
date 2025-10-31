#!/usr/bin/env python3
"""
Commitly Helper Bot
===================
Простой Telegram-бот на python-telegram-bot (v20+) с функциями:
- /about — кратко о проекте
- /contacts — контакты коллег
- /news — поиск свежей новости об обучении/разработке через NewsAPI
- /start — включает напоминания и ежедневные дайджесты для текущего чата

Напоминания (через JobQueue):
- Каждый вторник в 18:50 — напоминание о подготовке к встрече
- Каждый четверг в 18:50 — напоминание о встрече
- Ежедневно в 19:00 — мотивационная цитата

Часы берутся из переменной окружения BOT_TIMEZONE (по умолчанию Europe/Moscow).
"""

import asyncio
import logging
import os
import random
from datetime import time

from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    Defaults,
)

# NewsAPI client
# Документация: https://newsapi.org/docs/client-libraries/python
from newsapi import NewsApiClient

# Для таймзоны используем zoneinfo из стандартной библиотеки (Python 3.9+).
# На некоторых системах может понадобиться пакет tzdata (добавлен в requirements.txt).
try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except Exception:  # pragma: no cover
    ZoneInfo = None

# --------------------------
# Конфигурация и константы
# --------------------------

load_dotenv()  # Загружаем .env (если есть)

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "").strip()
BOT_TIMEZONE = os.getenv("BOT_TIMEZONE", "Europe/Moscow").strip()

# Тексты
ABOUT_TEXT_HTML = (
    "Commitly — это B2B-платформа для обучения программистов через геймификацию.\n\n"
    "— Программисты как обычно пишут код и проходят тесты: юнит, функциональное тестирование, "
    "нагрузочное, тесты по безопасности и т.д.\n"
    "— Платформа автоматически генерирует для них персонализированные обучающие игры.\n"
    "— Обучение фокусируется на изучении новых технологий через практику, адаптированные "
    "под уровень и цели пользователя с помощью AI.\n"
    "— Система включает постоянный конкурентный режим с рейтингами, наградами и лидерами, "
    "что мотивирует сотрудников учиться активнее."
)

CONTACTS_HTML = (
    "Контакты\n"
    "Алексей: @alxxcold\n"
    "Даниил: @D_Korr"
)

# 20 коротких цитат (рус) — бот будет выбирать одну случайно каждый день
QUOTES = [
    "Учись каждый день — маленькие шаги складываются в большие прорывы.",
    "Код — это ремесло. Практика делает мастера.",
    "Падай быстро, вставай быстрее и документируй выводы.",
    "Нет идеального момента начать — есть текущий коммит.",
    "Лучший рефакторинг — тот, который делает код понятнее для команды завтра.",
    "Маленькие победы ведут к большим релизам.",
    "Тесты — это не тормоз, а педаль безопасности.",
    "Автоматизируй скучное — освобождай время для важного.",
    "Ошибки — следы обучения. Не бойся их, анализируй.",
    "Стабильно лучше, чем идеально.",
    "Читай код как книгу — и пиши, чтобы его хотелось читать.",
    "Если сложно объяснить — значит, надо упростить дизайн.",
    "Скорость команды важнее скорости одиночки.",
    "Каждый день — новый шанс стать сильнее на 1%.",
    "Сомневаешься — измерь. Данные снимают споры.",
    "Системное мышление сильнее хаотичной импровизации.",
    "Документация — часть продукта, а не постскриптум.",
    "Архитектура — это выбор компромиссов, сделанных осознанно.",
    "Ревью кода — способ учиться, а не критиковать.",
    "Главная метрика обучения — применённые знания.",
]

# --------------------------
# Вспомогательные функции
# --------------------------

def get_tz():
    """Возвращает объект таймзоны для JobQueue."""
    if ZoneInfo is None:
        # Фолбэк: без tz-aware времени JobQueue будет работать в локальном времени контейнера/сервера.
        return None
    try:
        return ZoneInfo(BOT_TIMEZONE)
    except Exception:
        return ZoneInfo("Europe/Moscow")  # простой запасной вариант


def job_name(prefix: str, chat_id: int) -> str:
    """Уникальное имя задания JobQueue для конкретного чата."""
    return f"{prefix}_{chat_id}"


async def send_safe_text(context: ContextTypes.DEFAULT_TYPE, chat_id: int, text: str, parse_mode: ParseMode | None = ParseMode.HTML) -> None:
    """Безопасная отправка сообщения c лаконичной обработкой ошибок."""
    try:
        await context.bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)
    except Exception as e:  # простой перехват, чтобы бот не падал
        logging.exception("Failed to send message: %s", e)


# --------------------------
# Команды
# --------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        chat_id = update.effective_chat.id
        jq = context.application.job_queue
        if jq is None:
            await update.message.reply_text(
                "Планировщик недоступен. Установите зависимости: "
                "pip install 'python-telegram-bot[job-queue]' 'APScheduler>=3.10' и перезапустите бота."
            )
            return

        tz = get_tz()

        # Сносим старые задания для этого чата (на случай повторного /start)
        for name in (
            job_name("daily_quote", chat_id),
            job_name("prep_reminder", chat_id),
            job_name("meet_reminder", chat_id),
        ):
            for job in jq.get_jobs_by_name(name):
                job.schedule_removal()

        # Ежедневная цитата в 19:00
        jq.run_daily(
            callback=daily_quote_job,
            time=time(hour=19, minute=0, tzinfo=tz),
            name=job_name("daily_quote", chat_id),
            data={"chat_id": chat_id},
        )

        # Вторник (1) в 18:50 — напоминание о подготовке
        jq.run_daily(
            callback=prep_reminder_job,
            time=time(hour=18, minute=50, tzinfo=tz),
            days=(1,),
            name=job_name("prep_reminder", chat_id),
            data={"chat_id": chat_id},
        )

        # Четверг (3) в 18:50 — напоминание о встрече
        jq.run_daily(
            callback=meet_reminder_job,
            time=time(hour=18, minute=50, tzinfo=tz),
            days=(3,),
            name=job_name("meet_reminder", chat_id),
            data={"chat_id": chat_id},
        )

        schedule_info = (
            f"Подписал этот чат на напоминания и ежедневные цитаты.\n\n"
            f"Часовой пояс: {BOT_TIMEZONE}\n"
            f"— Вторник 18:50: напоминание о подготовке к встрече\n"
            f"— Четверг 18:50: напоминание о встрече\n"
            f"— Ежедневно 19:00: мотивационная цитата"
        )
        await update.message.reply_text(schedule_info)
    except Exception as e:
        logging.exception("start failed: %s", e)
        await update.message.reply_text("Что-то пошло не так. Попробуйте ещё раз.")


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/about — описание проекта."""
    try:
        await update.message.reply_html(ABOUT_TEXT_HTML)
    except Exception as e:
        logging.exception("about failed: %s", e)
        await update.message.reply_text("Не удалось показать описание. Попробуйте позже.")


async def contacts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/contacts — контакты коллег."""
    try:
        await update.message.reply_html(CONTACTS_HTML)
    except Exception as e:
        logging.exception("contacts failed: %s", e)
        await update.message.reply_text("Не удалось показать контакты. Попробуйте позже.")


def _pick_first_paragraph(article: dict) -> tuple[str, str]:
    """Извлекает (title, first_paragraph) из объекта новости NewsAPI."""
    title = (article.get("title") or "").strip()
    # Предпочитаем description как краткий первый абзац
    text = (article.get("description") or article.get("content") or "").strip()

    # Убираем хвосты вида '… [+123 chars]' из content
    cut_idx = text.find(" [+")
    if cut_idx != -1:
        text = text[:cut_idx].rstrip()
    else:
        # иногда бывает длинное троеточие-эллипсис
        if text.endswith("…"):
            text = text.rstrip("…").strip()

    if not text:
        text = "Без краткого описания. Перейдите к источнику для деталей."

    return title, text


async def news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/news — выдаёт самую свежую/популярную новость на тему обучения/разработки."""
    try:
        if not NEWSAPI_KEY:
            await update.message.reply_text("NEWSAPI_KEY не задан. Добавьте ключ в .env.")
            return

        client = NewsApiClient(api_key=NEWSAPI_KEY)

        # Ключевые запросы по теме обучения и разработки
        queries = [
            # Сначала попытка на русском:
            {"q": "обучение разработчиков OR обучение программированию OR разработка программного обеспечения", "language": "ru", "sort_by": "publishedAt"},
            # Потом на английском как запасной вариант:
            {"q": "software development OR developer training OR programming education", "language": "en", "sort_by": "publishedAt"},
        ]

        article = None
        for q in queries:
            resp = client.get_everything(
                q=q["q"],
                language=q["language"],
                sort_by=q["sort_by"],    # 'publishedAt' или 'popularity'
                page_size=10,
            )
            articles = resp.get("articles", []) if isinstance(resp, dict) else []
            if articles:
                # Берём первую подходящую
                article = articles[0]
                break

        if not article:
            await update.message.reply_text("Новости не найдены. Попробуйте позже.")
            return

        title, first_para = _pick_first_paragraph(article)

        # Формат как в задании — оставляем ** для наглядности, без Markdown парсинга
        formatted = f"**{title}**\n\n{first_para}"
        await update.message.reply_text(formatted, parse_mode=None)
    except Exception as e:
        logging.exception("news failed: %s", e)
        await update.message.reply_text("Ошибка при получении новостей. Попробуйте позже.")


# --------------------------
# Задания JobQueue (напоминания и дайджест)
# --------------------------

async def daily_quote_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ежедневная мотивационная цитата в 19:00."""
    try:
        chat_id = context.job.data["chat_id"]
        quote = random.choice(QUOTES)
        await send_safe_text(context, chat_id, f"💡 {quote}")
    except Exception as e:
        logging.exception("daily_quote_job failed: %s", e)


async def prep_reminder_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Вторник 18:50 — напоминание о подготовке к встрече."""
    try:
        chat_id = context.job.data["chat_id"]
        text = (
            "📌 Время готовиться к встрече: обновите статус задач, соберите метрики и отметьте риски. "
            "Подготовьте демо/слайды, если требуется."
        )
        await send_safe_text(context, chat_id, text)
    except Exception as e:
        logging.exception("prep_reminder_job failed: %s", e)


async def meet_reminder_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Четверг 18:50 — напоминание о встрече."""
    try:
        chat_id = context.job.data["chat_id"]
        text = (
            "⏰ Напоминание: сегодня встреча! Проверьте доступ к стендап- или созвону, "
            "подготовьте краткий апдейт по задачам и блокерам."
        )
        await send_safe_text(context, chat_id, text)
    except Exception as e:
        logging.exception("meet_reminder_job failed: %s", e)


# --------------------------
# Точка входа
# --------------------------

def main() -> None:
    """Создание и запуск приложения бота."""
    if not BOT_TOKEN:
        raise SystemExit("BOT_TOKEN не задан. Укажите его в .env")

    logging.basicConfig(
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        level=logging.INFO,
    )

    application: Application = (
    ApplicationBuilder()
    .token(BOT_TOKEN)
    .defaults(Defaults(parse_mode=ParseMode.HTML))  # <-- исправили
    .build()
    )

    # Регистрируем команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("about", about))
    application.add_handler(CommandHandler("contacts", contacts))
    application.add_handler(CommandHandler("news", news))

    # Запускаем поллинг (для простоты; вебхуки можно настроить отдельно).
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    try:
        main()  # <-- без asyncio.run
    except KeyboardInterrupt:
        pass
