"""
Конфигурация приложения
"""

import logging

# Настройки по умолчанию для SNMP v3
V3_DEFAULT_USERNAME = "Mr_PRTG2"
V3_DEFAULT_AUTH_KEY = "Flutter$hybestPony"
V3_DEFAULT_PRIV_KEY = "Flutter$hybestPony"
V3_DEFAULT_AUTH_PROTOCOL = "SHA"
V3_DEFAULT_PRIV_PROTOCOL = "AES"

# Цвета интерфейса
COLORS = {
    "primary": "#3b82f6",
    "primary_dark": "#2563eb",
    "success": "#10b981",
    "error": "#ef4444",
    "warning": "#f59e0b",
    "dark": "#1f2937",
    "light": "#f8fafc",
    "v2c": "#10b981",
    "v3": "#8b5cf6",
    "v3_default": "#ec4899"
}

# Часто используемые OID
COMMON_OIDS = [
    ("1.3.6.1.2.1.1.1.0", "sysDescr - Описание системы"),
    ("1.3.6.1.2.1.1.5.0", "sysName - Имя системы"),
    ("1.3.6.1.2.1.4.20.1.1", "ipAdEntAddr - IP адреса интерфейса"),
]

# Параметры приложения
APP_TITLE = "🔍 SNMP OID Checker"
APP_DESCRIPTION = "Веб-приложение для проверки SNMP OID"
DEFAULT_PORT = 8888

# Настройки логирования
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'