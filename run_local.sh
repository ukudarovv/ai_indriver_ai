#!/bin/bash

echo "🚀 Запуск AI Car Analysis в локальной сети..."
echo "================================================"

# Активируем виртуальное окружение если существует
if [ -f "env/bin/activate" ]; then
    echo "📦 Активация виртуального окружения..."
    source env/bin/activate
fi

# Запускаем Python скрипт
echo "🌐 Запуск сервера..."
python run_local.py
