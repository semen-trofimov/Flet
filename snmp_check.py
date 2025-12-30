#!/usr/bin/env python
"""
SNMP checker для pysnmp 7.x с асинхронным API
"""

import sys
import asyncio
from pysnmp.hlapi.v3arch.asyncio import *

async def check_snmp(ip, oid, community="public"):
    """Асинхронная проверка SNMP OID"""
    try:
        # Создаем транспорт асинхронно
        transport = await UdpTransportTarget.create((ip, 161))
        
        # Выполняем SNMP запрос асинхронно
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

def main():
    if len(sys.argv) < 3:
        print("=" * 50)
        print("SNMP OID Checker для pysnmp 7.x (асинхронный)")
        print("=" * 50)
        print("\nИспользование:")
        print("  python snmp_check.py <IP> <OID> [community]")
        print("\nПримеры:")
        print("  python snmp_check.py 192.168.1.1 1.3.6.1.2.1.1.1.0")
        print("  python snmp_check.py demo.snmplabs.com 1.3.6.1.2.1.1.1.0 public")
        return
    
    ip = sys.argv[1]
    oid = sys.argv[2]
    community = sys.argv[3] if len(sys.argv) > 3 else "public"
    
    print(f"Проверка OID: {oid}")
    print(f"Устройство: {ip}")
    print(f"Community: {community}")
    print("-" * 40)
    
    # Запускаем асинхронную функцию
    result = asyncio.run(check_snmp(ip, oid, community))
    
    if result["success"]:
        print("✓ УСПЕХ")
        print(f"Значение: {result['value']}")
    else:
        print("✗ ОШИБКА")
        print(f"Причина: {result['error']}")

if __name__ == "__main__":
    main()