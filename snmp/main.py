"""
Точка входа в приложение
"""

import flet as ft
import warnings
from app import main as app_main
from config import *

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 SNMP Checker запускается...")
    print("📡 Поддерживается SNMP v2c и SNMP v3")
    print("⚡ НОВОЕ: Кнопка быстрой настройки V3 Default")
    print(f"   Username: {V3_DEFAULT_USERNAME}")
    print(f"   Auth/Priv Key: {V3_DEFAULT_AUTH_KEY}")
    print(f"   Auth Protocol: {V3_DEFAULT_AUTH_PROTOCOL}")
    print(f"   Priv Protocol: {V3_DEFAULT_PRIV_PROTOCOL}")
    print("🔐 SNMP v3 поддерживает:")
    print("   - Аутентификация: SHA, MD5")
    print("   - Шифрование: AES-128, AES-256, DES")
    print("🌐 Откройте браузер по адресу: http://127.0.0.1:8080")
    print("=" * 60)
    
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    
    ft.app(
        target=app_main,
        port=DEFAULT_PORT,
        view=ft.AppView.WEB_BROWSER
    )