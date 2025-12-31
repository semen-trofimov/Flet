"""
SNMP утилиты для работы с v2c и v3
"""

import asyncio
import logging
from pysnmp.hlapi.v3arch.asyncio import *

# Логгер для этого модуля
logger = logging.getLogger(__name__)

async def check_snmp_v2c_async(ip, oid, community="public", port=161):
    """Асинхронная проверка SNMP OID для версии v2c"""
    logger.info(f"SNMP v2c запрос: {ip}:{port}, OID: {oid}, Community: {community}")
    
    try:
        transport = await UdpTransportTarget.create((ip, port))
        
        errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
            SnmpEngine(),
            CommunityData(community),
            transport,
            ContextData(),
            ObjectType(ObjectIdentity(oid))
        )

        if errorIndication:
            error_msg = f"SNMP v2c ошибка: {errorIndication}"
            logger.error(f"{error_msg} | IP: {ip}, OID: {oid}")
            return {"success": False, "error": str(errorIndication)}
        elif errorStatus:
            error_msg = f"SNMP v2c ошибка: {errorStatus.prettyPrint()}"
            logger.error(f"{error_msg} | IP: {ip}, OID: {oid}")
            return {"success": False, "error": f"SNMP Error: {errorStatus.prettyPrint()}"}
        else:
            for varBind in varBinds:
                result = str(varBind[1])
                logger.info(f"SNMP v2c успешно: {ip} | OID: {oid} | Результат: {result[:50]}...")
                return {"success": True, "value": result}

    except Exception as e:
        error_msg = f"Исключение в SNMP v2c: {str(e)}"
        logger.error(f"{error_msg} | IP: {ip}, OID: {oid}", exc_info=True)
        return {"success": False, "error": f"Ошибка: {str(e)}"}

async def check_snmp_v3_async(ip, oid, username, auth_key=None, priv_key=None,
                              auth_protocol=None, priv_protocol=None, port=161):
    """Асинхронная проверка SNMP OID для версии v3"""
    logger.info(f"SNMP v3 запрос: {ip}:{port}, OID: {oid}, User: {username}, "
                f"Auth: {auth_protocol}, Priv: {priv_protocol}")
    
    try:
        transport = await UdpTransportTarget.create((ip, port))

        # Пробуем импорт протоколов из разных мест в новой версии pysnmp
        try:
            # Попытка 1: из pysnmp.hlapi
            from pysnmp.hlapi import (
                usmHMACSHAAuthProtocol,
                usmHMACMD5AuthProtocol,
                usmAesCfb128Protocol,
                usmDESPrivProtocol,
                usmAesCfb256Protocol
            )
        except ImportError:
            # Попытка 2: из pysnmp.entity.rfc3413.oneliner
            try:
                from pysnmp.entity.rfc3413.oneliner import (
                    usmHMACSHAAuthProtocol,
                    usmHMACMD5AuthProtocol,
                    usmAesCfb128Protocol,
                    usmDESPrivProtocol,
                    usmAesCfb256Protocol
                )
            except ImportError:
                # Попытка 3: использовать OID напрямую
                logger.warning("Не удалось импортировать протоколы, использую OID")
                # OID для протоколов
                usmHMACSHAAuthProtocol = (1, 3, 6, 1, 6, 3, 10, 1, 1, 3)
                usmHMACMD5AuthProtocol = (1, 3, 6, 1, 6, 3, 10, 1, 1, 2)
                usmAesCfb128Protocol = (1, 3, 6, 1, 6, 3, 10, 1, 2, 4)
                usmDESPrivProtocol = (1, 3, 6, 1, 6, 3, 10, 1, 2, 2)
                usmAesCfb256Protocol = (1, 3, 6, 1, 6, 3, 10, 1, 2, 10)

        auth_proto = None
        priv_proto = None

        if auth_protocol == "SHA":
            auth_proto = usmHMACSHAAuthProtocol
        elif auth_protocol == "MD5":
            auth_proto = usmHMACMD5AuthProtocol

        if priv_protocol == "AES":
            priv_proto = usmAesCfb128Protocol
        elif priv_protocol == "DES":
            priv_proto = usmDESPrivProtocol
        elif priv_protocol == "AES256":
            priv_proto = usmAesCfb256Protocol

        if auth_key and priv_key and auth_proto and priv_proto:
            # authPriv - с аутентификацией и шифрованием
            security_params = UsmUserData(
                username,
                authKey=auth_key,
                privKey=priv_key,
                authProtocol=auth_proto,
                privProtocol=priv_proto
            )
            security_level = "authPriv"
        elif auth_key and auth_proto:
            # authNoPriv - только аутентификация
            security_params = UsmUserData(
                username,
                authKey=auth_key,
                authProtocol=auth_proto
            )
            security_level = "authNoPriv"
        else:
            # noAuthNoPriv - без аутентификации и шифрования
            security_params = UsmUserData(username)
            security_level = "noAuthNoPriv"
        
        logger.debug(f"SNMP v3: {security_level} режим")

        errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
            SnmpEngine(),
            security_params,
            transport,
            ContextData(),
            ObjectType(ObjectIdentity(oid))
        )

        if errorIndication:
            error_msg = f"SNMP v3 ошибка: {errorIndication}"
            logger.error(f"{error_msg} | IP: {ip}, User: {username}, OID: {oid}, Level: {security_level}")
            return {"success": False, "error": str(errorIndication)}
        elif errorStatus:
            error_msg = f"SNMP v3 ошибка: {errorStatus.prettyPrint()}"
            logger.error(f"{error_msg} | IP: {ip}, User: {username}, OID: {oid}, Level: {security_level}")
            return {"success": False, "error": f"SNMP Error: {errorStatus.prettyPrint()}"}
        else:
            for varBind in varBinds:
                result = str(varBind[1])
                logger.info(f"SNMP v3 успешно: {ip} | User: {username} | OID: {oid} | "
                           f"Level: {security_level} | Результат: {result[:50]}...")
                return {"success": True, "value": result}

    except Exception as e:
        error_msg = f"Исключение в SNMP v3: {str(e)}"
        logger.error(f"{error_msg} | IP: {ip}, User: {username}, OID: {oid}", exc_info=True)
        return {"success": False, "error": f"Ошибка: {str(e)}"}

def get_snmp_checker(version="v2c"):
    """Фабрика для получения нужной функции проверки"""
    logger.debug(f"Получен SNMP checker для версии: {version}")
    if version == "v2c":
        return check_snmp_v2c_async
    else:
        return check_snmp_v3_async