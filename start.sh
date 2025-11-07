#!/bin/sh
set -eu

# Переходим в папку с ботом
cd "$(dirname "$0")/lab2" || exit 1
echo "[start.sh] Working dir: $(pwd)"

# Обязательные переменные окружения (задать в Railway → Variables)
: "${BOT_TOKEN:?Set BOT_TOKEN in Railway project variables}"
: "${NEWSAPI_KEY:?Set NEWSAPI_KEY in Railway project variables}"

# Необязательные (имеют дефолты в коде), экспортируем на всякий случай
: "${BOT_TIMEZONE:=Europe/Moscow}"
: "${DEFAULT_REGION:=ru}"
export BOT_TIMEZONE DEFAULT_REGION

# Определяем python
if command -v python3 >/dev/null 2>&1; then
  PY=python3
else
  PY=python
fi

# Устанавливаем зависимости
$PY -m pip install --upgrade pip setuptools wheel
$PY -m pip install --no-cache-dir -r requirements.txt

# Запускаем бота
exec $PY bot.py