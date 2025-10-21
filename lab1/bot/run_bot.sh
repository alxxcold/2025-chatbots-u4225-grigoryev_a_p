#!/bin/bash
# Скрипт для запуска Telegram-бота

echo "🤖 Запуск Telegram-бота для команды Commitly..."

# Проверяем наличие виртуального окружения
if [ ! -d "venv" ]; then
    echo "❌ Виртуальное окружение не найдено. Создаем..."
    python3 -m venv venv
    echo "✅ Виртуальное окружение создано"
fi

# Активируем виртуальное окружение
echo "🔄 Активация виртуального окружения..."
source venv/bin/activate

# Проверяем наличие .env файла
if [ ! -f ".env" ]; then
    echo "❌ Файл .env не найден!"
    echo "📝 Создайте файл .env с вашим токеном бота:"
    echo "   BOT_TOKEN=ваш_токен_здесь"
    echo ""
    echo "💡 Скопируйте env_template.txt в .env и заполните токен"
    exit 1
fi

# Устанавливаем зависимости если нужно
echo "📦 Проверка зависимостей..."
pip install -r requirements.txt --quiet

# Запускаем бота
echo "🚀 Запуск бота..."
python bot.py
