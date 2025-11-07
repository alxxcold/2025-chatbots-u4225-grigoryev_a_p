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
REGION_PREFS: dict[int, str] = {}            # chat_id -> "ru" | "us" | "eu"
DEFAULT_REGION = os.getenv("DEFAULT_REGION", "ru")
RATE_URL = "https://forms.gle/GFWv2BbVZTsMikAd7"


def get_region(chat_id: int) -> str:
    return REGION_PREFS.get(chat_id, DEFAULT_REGION)

def region_to_params(region: str) -> tuple[str, str | None]:
    """Возвращает (language, country) для NewsAPI. country=None => используем get_everything()."""
    r = region.lower()
    if r == "ru":
        return "ru", "ru"
    if r == "us":
        return "en", "us"
    if r == "eu":
        return "en", None
    return "en", None


# --- тексты с эмодзи ---
ABOUT_TEXT_HTML = (
    "🚀 Commitly — B2B-платформа для обучения программистов через геймификацию.\n\n"
    "🧪 Разработчики как обычно пишут код и проходят тесты: юнит, функциональные, "
    "нагрузочные, по безопасности и т.д.\n"
    "🎮 Платформа автоматически генерирует персонализированные обучающие игры.\n"
    "🤖 Обучение через практику новых технологий, адаптировано под уровень и цели с помощью AI.\n"
    "🏆 Постоянный соревновательный режим: рейтинги, награды и лидеры мотивируют учиться активнее."
)

CONTACTS_HTML = (
    "📇 Контакты\n"
    "— Алексей: @alxxcold\n"
    "— Даниил: @D_Korr"
)

QUOTES = [
    "💡 Учись каждый день — маленькие шаги складываются в большие прорывы.",
    "🛠️ Код — это ремесло. Практика делает мастера.",
    "🔁 Падай быстро, вставай быстрее и документируй выводы.",
    "🚦 Нет идеального момента начать — есть текущий коммит.",
    "🧹 Лучший рефакторинг — тот, который делает код понятнее для команды завтра.",
    "🏁 Маленькие победы ведут к большим релизам.",
    "🧪 Тесты — это не тормоз, а педаль безопасности.",
    "⚙️ Автоматизируй скучное — освобождай время для важного.",
    "🧭 Ошибки — следы обучения. Не бойся их, анализируй.",
    "📈 Стабильно лучше, чем идеально.",
    "📖 Читай код как книгу — и пиши, чтобы его хотелось читать.",
    "🧩 Если сложно объяснить — значит, надо упростить дизайн.",
    "👥 Скорость команды важнее скорости одиночки.",
    "1️⃣ Каждый день — новый шанс стать сильнее на 1%.",
    "📊 Сомневаешься — измерь. Данные снимают споры.",
    "🧠 Системное мышление сильнее хаотичной импровизации.",
    "📝 Документация — часть продукта, а не постскриптум.",
    "⚖️ Архитектура — это выбор компромиссов, сделанных осознанно.",
    "🔍 Ревью кода — способ учиться, а не критиковать.",
    "🎯 Главная метрика обучения — применённые знания.",
]


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

# --- описания для /help ---
def desc_about() -> str:
    return "ℹ️ /about — что такое Commitly и как это работает."

def desc_contacts() -> str:
    return "📇 /contacts — быстрые контакты команды."

def desc_news() -> str:
    return ("🗞️ /news [тема] — свежая новость по выбранной теме.\n"
            "   Примеры: /news golang, /news ai, /news обучение разработчиков")

def desc_region() -> str:
    return ("🌍 /region ru|us|eu — выбрать регион новостей (запоминается для чата).")

def desc_start() -> str:
    return ("⏰ /start — включает напоминания и ежедневную цитату:\n"
            "   • Вт 18:50 — подготовка к встрече\n"
            "   • Чт 18:50 — встреча\n"
            "   • Ежедневно 19:00 — мотивационная цитата")

def desc_help() -> str:
    return "❓ /help — список команд и краткие описания."

def desc_rate() -> str:
    return "📝 /rate — оценить работу бота и оставить отзыв."


# --------------------------
# Команды
# --------------------------

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        text = "\n\n".join([
            "🤖 Привет! Вот что я умею:",
            desc_about(),
            desc_contacts(),
            desc_news(),
            desc_region(),
            desc_start(),
            desc_rate(),
            desc_help(),
        ])
        await update.message.reply_text(text)
    except Exception as e:
        logging.exception("help failed: %s", e)
        await update.message.reply_text("Не удалось показать помощь.")


async def rate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await update.message.reply_text(
            f"📝 Пожалуйста, оцените работу бота и оставьте отзыв:\n{RATE_URL}"
        )
    except Exception as e:
        logging.exception("rate failed: %s", e)
        await update.message.reply_text("Не удалось отправить ссылку на форму.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        chat_id = update.effective_chat.id
        jq = context.application.job_queue
        if jq is None:
            await update.message.reply_text(
                "⚠️ Планировщик недоступен.\n"
                "Установите зависимости: pip install 'python-telegram-bot[job-queue]' APScheduler>=3.10"
            )
            return

        tz = get_tz()

        for name in (
            job_name("daily_quote", chat_id),
            job_name("prep_reminder", chat_id),
            job_name("meet_reminder", chat_id),
        ):
            for job in jq.get_jobs_by_name(name):
                job.schedule_removal()

        jq.run_daily(
            callback=daily_quote_job,
            time=time(hour=19, minute=0, tzinfo=tz),
            name=job_name("daily_quote", chat_id),
            data={"chat_id": chat_id},
        )
        jq.run_daily(
            callback=prep_reminder_job,
            time=time(hour=18, minute=50, tzinfo=tz),
            days=(1,),
            name=job_name("prep_reminder", chat_id),
            data={"chat_id": chat_id},
        )
        jq.run_daily(
            callback=meet_reminder_job,
            time=time(hour=18, minute=50, tzinfo=tz),
            days=(3,),
            name=job_name("meet_reminder", chat_id),
            data={"chat_id": chat_id},
        )

        schedule_info = (
            f"✅ Подписал этот чат на напоминания и ежедневные цитаты.\n\n"
            f"🌐 Часовой пояс: {BOT_TIMEZONE}\n"
            f"📅 Вт 18:50 — напоминание о подготовке к встрече\n"
            f"📅 Чт 18:50 — напоминание о встрече\n"
            f"🕖 Ежедневно 19:00 — мотивационная цитата\n\n"
            f"{desc_help()}"
        )
        await update.message.reply_text(schedule_info)
    except Exception as e:
        logging.exception("start failed: %s", e)
        await update.message.reply_text("Что-то пошло не так. Попробуйте ещё раз.")


async def set_region(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        chat_id = update.effective_chat.id
        if not context.args:
            await update.message.reply_text("🌍 Укажите регион: /region ru | /region us | /region eu")
            return
        region = context.args[0].lower()
        if region not in {"ru", "us", "eu"}:
            await update.message.reply_text("❌ Недопустимый регион. Доступно: ru, us, eu.")
            return
        REGION_PREFS[chat_id] = region
        await update.message.reply_text(f"✅ Регион сохранён: {region.upper()} — новости будут подбираться под него.")
    except Exception as e:
        logging.exception("region failed: %s", e)
        await update.message.reply_text("Не удалось установить регион.")


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
    try:
        if not NEWSAPI_KEY:
            await update.message.reply_text("🔑 NEWSAPI_KEY не задан. Добавьте ключ в .env.")
            return

        client = NewsApiClient(api_key=NEWSAPI_KEY)

        chat_id = update.effective_chat.id
        region = get_region(chat_id)
        language, country = region_to_params(region)

        topic = " ".join(context.args).strip() if context.args else ""
        if not topic:
            topic = "software development OR developer training OR programming education"

        article = None

        if country:
            try:
                resp = client.get_top_headlines(q=topic, country=country, page_size=10)
                articles = resp.get("articles", []) if isinstance(resp, dict) else []
                if articles:
                    article = articles[0]
            except Exception:
                pass

        if article is None:
            resp = client.get_everything(
                q=topic,
                language=language,
                sort_by="publishedAt",
                page_size=10,
            )
            articles = resp.get("articles", []) if isinstance(resp, dict) else []
            if articles:
                article = articles[0]

        if not article:
            await update.message.reply_text("😕 Новости не найдены. Попробуйте другую тему или регион (/region).")
            return

        title, first_para = _pick_first_paragraph(article)

        # Форматируем через HTML (только <b> и переносы строк), чтобы избежать проблем MarkdownV2
        import html as _html
        title_html = _html.escape(title) if title else "Без заголовка"
        first_para_html = _html.escape(first_para)
        url = article.get("url") or ""

        formatted = f"<b>{title_html}</b>\n\n{first_para_html}"
        if url:
            formatted += f"\n\n{url}"  # Telegram сам сделает ссылку кликабельной

        await update.message.reply_text(formatted, parse_mode=ParseMode.HTML)
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
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("region", set_region))
    application.add_handler(CommandHandler("rate", rate_command))



    # Запускаем поллинг (для простоты; вебхуки можно настроить отдельно).
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    try:
        main()  # <-- без asyncio.run
    except KeyboardInterrupt:
        pass
