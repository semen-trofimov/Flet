"""
Точка входа в приложение
"""

import flet as ft
import warnings
import logging
from datetime import datetime
from app import main as app_main
from config import *

# Настройка логирования
def setup_logging():
    """Настройка системы логирования"""
    # Создаем директорию для логов, если её нет
    import os
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Создаем имя файла с датой
    log_filename = f"{log_dir}/snmp_checker_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # Настраиваем логгер
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()  # также выводим в консоль
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Логирование инициализировано. Файл логов: {log_filename}")
    return logger

if __name__ == "__main__":
    logger = setup_logging()
    
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
    print("📝 Логирование в файл: logs/snmp_checker_*.log")
    print("=" * 60)
    
    logger.info("=" * 60)
    logger.info("SNMP Checker запускается...")
    logger.info(f"Порт: {DEFAULT_PORT}")
    logger.info(f"V3 Default Username: {V3_DEFAULT_USERNAME}")
    logger.info("=" * 60)
    
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    
    try:
        ft.app(
            target=app_main,
            port=DEFAULT_PORT,
            view=ft.AppView.WEB_BROWSER
        )
        logger.info("Приложение успешно завершено")
    except Exception as e:
        logger.error(f"Ошибка запуска приложения: {str(e)}", exc_info=True)
        raise