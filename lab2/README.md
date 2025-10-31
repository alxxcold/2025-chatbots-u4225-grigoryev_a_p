# Commitly Helper Bot

Телеграм-бот на Python (python-telegram-bot v20+), который:
- Рассказывает о проекте (`/about`)
- Показывает контакты (`/contacts`)
- Присылает свежую новость об обучении/разработке из NewsAPI (`/news`)
- По команде `/start` подписывает текущий чат на напоминания и ежедневные цитаты:
  - Вторник 18:50 — напоминание о подготовке к встрече
  - Четверг 18:50 — напоминание о встрече
  - Ежедневно 19:00 — мотивационная цитата

## Быстрый старт

1) Установите зависимости (Python 3.10+ рекомендован):
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# заполните токены
python bot.py
