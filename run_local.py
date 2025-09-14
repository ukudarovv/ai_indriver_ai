#!/usr/bin/env python
"""
Скрипт для запуска Django сервера в локальной сети
"""
import os
import sys
import socket
import subprocess
from pathlib import Path

def get_local_ip():
    """Получает локальный IP адрес"""
    try:
        # Подключаемся к внешнему адресу для определения локального IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def main():
    """Запускает Django сервер"""
    print("🚀 Запуск AI Car Analysis в локальной сети...")
    print("=" * 50)
    
    # Получаем локальный IP
    local_ip = get_local_ip()
    port = 8000
    
    print(f"📡 Локальный IP: {local_ip}")
    print(f"🌐 Порт: {port}")
    print(f"🔗 URL для доступа: http://{local_ip}:{port}/app2/")
    print("=" * 50)
    print("📱 Доступ с других устройств в сети:")
    print(f"   • С телефона: http://{local_ip}:{port}/app2/")
    print(f"   • С другого ПК: http://{local_ip}:{port}/app2/")
    print("=" * 50)
    print("⚠️  Для остановки нажмите Ctrl+C")
    print("=" * 50)
    
    # Запускаем Django сервер
    try:
        os.system(f"python manage.py runserver 0.0.0.0:{port}")
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен")

if __name__ == "__main__":
    main()
