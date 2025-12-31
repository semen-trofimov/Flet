"""
SNMP утилиты для работы с v2c и v3
"""

import asyncio
from pysnmp.hlapi.v3arch.asyncio import *
from pysnmp import hlapi


async def check_snmp_v2c_async(ip, oid, community="public", port=161):
    """Асинхронная проверка SNMP OID для версии v2c"""
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
            return {"success": False, "error": str(errorIndication)}
        elif errorStatus:
            return {"success": False, "error": f"SNMP Error: {errorStatus.prettyPrint()}"}
        else:
            for varBind in varBinds:
                return {"success": True, "value": str(varBind[1])}

    except Exception as e:
        return {"success": False, "error": f"Ошибка: {str(e)}"}


async def check_snmp_v3_async(ip, oid, username, auth_key=None, priv_key=None,
                              auth_protocol=None, priv_protocol=None, port=161):
    """Асинхронная проверка SNMP OID для версии v3"""
    try:
        transport = await UdpTransportTarget.create((ip, port))

        auth_proto = None
        priv_proto = None

        if auth_protocol == "SHA":
            auth_proto = hlapi.usmHMACSHAAuthProtocol
        elif auth_protocol == "MD5":
            auth_proto = hlapi.usmHMACMD5AuthProtocol

        if priv_protocol == "AES":
            priv_proto = hlapi.usmAesCfb128Protocol
        elif priv_protocol == "DES":
            priv_proto = hlapi.usmDESPrivProtocol
        elif priv_protocol == "AES256":
            priv_proto = hlapi.usmAesCfb256Protocol

        if auth_key and priv_key:
            security_params = UsmUserData(
                username,
                authKey=auth_key,
                privKey=priv_key,
                authProtocol=auth_proto,
                privProtocol=priv_proto
            )
        elif auth_key:
            security_params = UsmUserData(
                username,
                authKey=auth_key,
                authProtocol=auth_proto
            )
        else:
            security_params = UsmUserData(username)

        errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
            SnmpEngine(),
            security_params,
            transport,
            ContextData(),
            ObjectType(ObjectIdentity(oid))
        )

        if errorIndication:
            return {"success": False, "error": str(errorIndication)}
        elif errorStatus:
            return {"success": False, "error": f"SNMP Error: {errorStatus.prettyPrint()}"}
        else:
            for varBind in varBinds:
                return {"success": True, "value": str(varBind[1])}

    except Exception as e:
        return {"success": False, "error": f"Ошибка: {str(e)}"}


def get_snmp_checker(version="v2c"):
    """Фабрика для получения нужной функции проверки"""
    if version == "v2c":
        return check_snmp_v2c_async
    else:
        return check_snmp_v3_async