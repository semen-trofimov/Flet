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
    ("1.3.6.1.2.1.1.3.0", "sysUpTime - Время работы"),
    ("1.3.6.1.2.1.1.5.0", "sysName - Имя системы"),
    ("1.3.6.1.2.1.2.2.1.10.1", "ifInOctets.1 - Входящий трафик"),
    ("1.3.6.1.2.1.2.2.1.16.1", "ifOutOctets.1 - Исходящий трафик"),
    ("1.3.6.1.2.1.1.6.0", "sysLocation - Местоположение"),
    ("1.3.6.1.2.1.1.4.0", "sysContact - Контактное лицо"),
    ("1.3.6.1.2.1.25.1.1.0", "hrSystemUptime - Время работы системы"),
    ("1.3.6.1.2.1.25.3.3.1.2.1", "hrProcessorLoad - Загрузка процессора"),
    ("1.3.6.1.2.1.2.2.1.8.1", "ifOperStatus - Статус интерфейса"),
    ("1.3.6.1.2.1.2.2.1.5.1", "ifSpeed - Скорость интерфейса"),
    ("1.3.6.1.2.1.4.20.1.1", "ipAdEntAddr - IP адреса интерфейса"),
    ("1.3.6.1.2.1.25.2.3.1.6.1", "hrStorageUsed - Используемое хранилище"),
]

# Параметры приложения
APP_TITLE = "🔍 SNMP OID Checker"
APP_DESCRIPTION = "Веб-приложение для проверки SNMP OID"
DEFAULT_PORT = 8080

# Настройки логирования
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'