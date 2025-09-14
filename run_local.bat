@echo off
echo 🚀 Запуск AI Car Analysis в локальной сети...
echo ================================================

REM Активируем виртуальное окружение если существует
if exist "env\Scripts\activate.bat" (
    echo 📦 Активация виртуального окружения...
    call env\Scripts\activate.bat
)

REM Запускаем Python скрипт
echo 🌐 Запуск сервера...
python run_local.py

pause
