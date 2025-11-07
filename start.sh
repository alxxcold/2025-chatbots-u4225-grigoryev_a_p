#!/usr/bin/env bash
set -Eeuo pipefail

# Переходим в папку с ботом
cd "$(dirname "$0")/lab2"

echo "[start.sh] Working dir: $(pwd)"

# Проверяем необходимые токены (задай их в Railway → Variables)
: "${BOT_TOKEN:?Set BOT_TOKEN in Railway project variables}"
: "${NEWSAPI_KEY:?Set NEWSAPI_KEY in Railway project variables}"

# Необязательные переменные (имеют дефолты в коде)
: "${BOT_TIMEZONE:=Europe/Moscow}"
: "${DEFAULT_REGION:=ru}"

echo "[start.sh] BOT_TIMEZONE=${BOT_TIMEZONE} DEFAULT_REGION=${DEFAULT_REGION}"

# Обновляем pip и ставим зависимости
python -m pip install --upgrade pip wheel setuptools
pip install --no-cache-dir -r requirements.txt

# Запускаем бота
exec python bot.py