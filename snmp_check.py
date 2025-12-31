#!/usr/bin/env python
"""
SNMP Checker App - Веб-приложение для проверки SNMP OID
Требуется: pip install flet pysnmp
"""

import flet as ft
import asyncio
from pysnmp.hlapi.v3arch.asyncio import *
from pysnmp import hlapi

# Настройки по умолчанию для v3 (вынесены в глобальную область)
V3_DEFAULT_USERNAME = "Mr_PRTG2"
V3_DEFAULT_AUTH_KEY = "Flutter$hybestPony"
V3_DEFAULT_PRIV_KEY = "Flutter$hybestPony"
V3_DEFAULT_AUTH_PROTOCOL = "SHA"
V3_DEFAULT_PRIV_PROTOCOL = "AES"

# Асинхронная функция для проверки SNMP v2c
async def check_snmp_v2c_async(ip, oid, community="public", port=161):
    """Асинхронная проверка SNMP OID для версии v2c"""
    try:
        # Создаем транспорт асинхронно
        transport = await UdpTransportTarget.create((ip, port))

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

# Асинхронная функция для проверки SNMP v3
async def check_snmp_v3_async(ip, oid, username, auth_key=None, priv_key=None, 
                              auth_protocol=None, priv_protocol=None, port=161):
    """Асинхронная проверка SNMP OID для версии v3"""
    try:
        # Создаем транспорт асинхронно
        transport = await UdpTransportTarget.create((ip, port))

        # Определяем протоколы аутентификации
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
        
        # Определяем уровень безопасности
        if auth_key and priv_key:
            # authPriv - с аутентификацией и шифрованием
            security_level = hlapi.usmAuthPrivProtocol
            security_params = UsmUserData(
                username,
                authKey=auth_key,
                privKey=priv_key,
                authProtocol=auth_proto,
                privProtocol=priv_proto
            )
        elif auth_key:
            # authNoPriv - только аутентификация
            security_level = hlapi.usmAuthNoPrivProtocol
            security_params = UsmUserData(
                username,
                authKey=auth_key,
                authProtocol=auth_proto
            )
        else:
            # noAuthNoPriv - без аутентификации
            security_level = hlapi.usmNoAuthProtocol
            security_params = UsmUserData(username)

        # Выполняем SNMP запрос асинхронно
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

# Основная функция Flet приложения
def main(page: ft.Page):
    page.title = "🔍 SNMP OID Checker"
    page.padding = 30
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO

    # Цвета для интерфейса
    colors = {
        "primary": "#3b82f6",
        "primary_dark": "#2563eb",
        "success": "#10b981",
        "error": "#ef4444",
        "warning": "#f59e0b",
        "dark": "#1f2937",
        "light": "#f8fafc",
        "v2c": "#10b981",
        "v3": "#8b5cf6",
        "v3_default": "#ec4899"  # Розовый цвет для кнопки быстрой настройки
    }

    # Переменные для хранения выбранной версии
    current_snmp_version = ft.Text("v2c")  # По умолчанию v2c

    # Элементы ввода для v2c (изначально видимые)
    ip_input = ft.TextField(
        label="IP адрес устройства",
        hint_text="Например: 192.168.1.1",
        width=500,
        border_radius=10,
        border_color=colors["primary"],
        keyboard_type=ft.KeyboardType.TEXT
    )

    oid_input = ft.TextField(
        label="SNMP OID",
        hint_text="Например: 1.3.6.1.2.1.1.1.0 (sysDescr)",
        width=500,
        border_radius=10,
        border_color=colors["primary"],
        keyboard_type=ft.KeyboardType.TEXT
    )

    community_input = ft.TextField(
        label="Community string",
        hint_text="Обычно 'public' или 'private'",
        width=500,
        border_radius=10,
        border_color=colors["primary"],
        value="public",
        password=False
    )

    # Элементы ввода для v3 (изначально скрытые)
    v3_username_input = ft.TextField(
        label="Username",
        hint_text="SNMP v3 username",
        width=500,
        border_radius=10,
        border_color=colors["v3"],
        visible=False
    )

    # Выбор протокола аутентификации
    auth_protocol_dropdown = ft.Dropdown(
        label="Auth Protocol",
        width=220,
        options=[
            ft.dropdown.Option("SHA"),
            ft.dropdown.Option("MD5"),
        ],
        value="SHA",
        visible=False
    )

    # Поле для пароля аутентификации
    auth_key_input = ft.TextField(
        label="Auth Key",
        hint_text="Пароль для аутентификации",
        width=500,
        border_radius=10,
        border_color=colors["v3"],
        password=True,
        can_reveal_password=True,
        visible=False
    )

    # Выбор протокола шифрования
    priv_protocol_dropdown = ft.Dropdown(
        label="Priv Protocol",
        width=220,
        options=[
            ft.dropdown.Option("AES"),
            ft.dropdown.Option("AES256"),
            ft.dropdown.Option("DES"),
        ],
        value="AES",
        visible=False
    )

    # Поле для пароля шифрования
    priv_key_input = ft.TextField(
        label="Priv Key",
        hint_text="Пароль для шифрования",
        width=500,
        border_radius=10,
        border_color=colors["v3"],
        password=True,
        can_reveal_password=True,
        visible=False
    )

    # Чекбокс для включения шифрования
    enable_encryption_checkbox = ft.Checkbox(
        label="Включить шифрование (Priv)",
        value=False,
        visible=False,
        on_change=lambda e: toggle_encryption_fields(e)
    )

    def toggle_encryption_fields(e):
        """Включение/выключение полей шифрования"""
        priv_protocol_dropdown.visible = enable_encryption_checkbox.value
        priv_key_input.visible = enable_encryption_checkbox.value
        page.update()

    # Контейнер для v3 параметров - ВАЖНО: изначально невидимый
    v3_params_container = ft.Column(
        [
            v3_username_input,
            ft.Row([
                auth_protocol_dropdown,
            ], alignment=ft.MainAxisAlignment.START),
            auth_key_input,
            enable_encryption_checkbox,
            # Поля шифрования (изначально скрыты)
            ft.Column([
                priv_protocol_dropdown,
                priv_key_input,
            ], visible=False)
        ],
        spacing=15,
        visible=False  # По умолчанию скрыт
    )

    # Кнопки выбора версии SNMP
    v2c_button = ft.ElevatedButton(
        "SNMP v2c",
        width=120,
        height=40,
        bgcolor=colors["v2c"],
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10)
        )
    )

    v3_button = ft.ElevatedButton(
        "SNMP v3",
        width=120,
        height=40,
        bgcolor=ft.Colors.GREY_300,
        color=colors["dark"],
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10)
        )
    )

    # НОВАЯ КНОПКА: Быстрая настройка v3 по умолчанию
    v3_default_button = ft.ElevatedButton(
        "V3 Default",
        width=120,
        height=40,
        bgcolor=ft.Colors.GREY_300,
        color=colors["dark"],
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10)
        ),
        tooltip=f"Быстрая настройка SNMP v3\nUsername: {V3_DEFAULT_USERNAME}\nAuth/Priv Key: {V3_DEFAULT_AUTH_KEY}\nAuth: {V3_DEFAULT_AUTH_PROTOCOL}, Priv: {V3_DEFAULT_PRIV_PROTOCOL}"
    )

    # Кнопки действий
    check_button = ft.FilledButton(
        "🔍 Проверить OID",
        width=200,
        height=50,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10)
        )
    )

    clear_button = ft.OutlinedButton(
        "🗑️ Очистить",
        width=150,
        height=50,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10)
        )
    )

    # Область вывода результатов
    result_output = ft.Column(
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
        height=300,
        width=600
    )

    # Список часто используемых OID
    common_oids = [
        ("1.3.6.1.2.1.1.1.0", "sysDescr - Описание системы"),
        ("1.3.6.1.2.1.1.3.0", "sysUpTime - Время работы"),
        ("1.3.6.1.2.1.1.5.0", "sysName - Имя системы"),
        ("1.3.6.1.2.1.2.2.1.10.1", "ifInOctets.1 - Входящий трафик"),
        ("1.3.6.1.2.1.2.2.1.16.1", "ifOutOctets.1 - Исходящий трафик"),
    ]

    # Карточки OID
    oid_cards = ft.Row(wrap=True, spacing=10, run_spacing=10, width=800)

    def use_common_oid(oid):
        oid_input.value = oid
        page.update()

    for oid, description in common_oids:
        oid_cards.controls.append(
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text(description, size=12, weight=ft.FontWeight.BOLD),
                        ft.Text(oid, size=10, color=colors["primary"], selectable=True),
                        ft.TextButton(
                            "Использовать",
                            on_click=lambda e, o=oid: use_common_oid(o)
                        )
                    ], spacing=5),
                    padding=10,
                    width=250
                ),
                elevation=3,
                bgcolor=colors["light"]
            )
        )

    # Функции для переключения между версиями SNMP
    def switch_to_v2c(e):
        current_snmp_version.value = "v2c"
        v2c_button.bgcolor = colors["v2c"]
        v2c_button.color = ft.Colors.WHITE
        v3_button.bgcolor = ft.Colors.GREY_300
        v3_button.color = colors["dark"]
        v3_default_button.bgcolor = ft.Colors.GREY_300
        v3_default_button.color = colors["dark"]
        
        # Показываем v2c параметры, скрываем v3
        community_input.visible = True
        v3_params_container.visible = False
        
        page.update()

    def switch_to_v3(e):
        current_snmp_version.value = "v3"
        v3_button.bgcolor = colors["v3"]
        v3_button.color = ft.Colors.WHITE
        v2c_button.bgcolor = ft.Colors.GREY_300
        v2c_button.color = colors["dark"]
        v3_default_button.bgcolor = ft.Colors.GREY_300
        v3_default_button.color = colors["dark"]
        
        # Показываем v3 параметры, скрываем v2c
        community_input.visible = False
        v3_params_container.visible = True
        
        # Сбрасываем состояние шифрования
        enable_encryption_checkbox.value = False
        priv_protocol_dropdown.visible = False
        priv_key_input.visible = False
        
        # Показываем основные поля v3
        v3_username_input.visible = True
        auth_protocol_dropdown.visible = True
        auth_key_input.visible = True
        enable_encryption_checkbox.visible = True
        
        # Сбрасываем значения на стандартные
        v3_username_input.value = ""
        auth_protocol_dropdown.value = V3_DEFAULT_AUTH_PROTOCOL
        auth_key_input.value = ""
        priv_protocol_dropdown.value = V3_DEFAULT_PRIV_PROTOCOL
        priv_key_input.value = ""
        
        page.update()

    # НОВАЯ ФУНКЦИЯ: Быстрая настройка v3 по умолчанию
    def switch_to_v3_default(e):
        current_snmp_version.value = "v3_default"
        v3_default_button.bgcolor = colors["v3_default"]
        v3_default_button.color = ft.Colors.WHITE
        v2c_button.bgcolor = ft.Colors.GREY_300
        v2c_button.color = colors["dark"]
        v3_button.bgcolor = ft.Colors.GREY_300
        v3_button.color = colors["dark"]
        
        # Показываем v3 параметры, скрываем v2c
        community_input.visible = False
        v3_params_container.visible = True
        
        # Автоматически включаем шифрование и заполняем поля
        enable_encryption_checkbox.value = True
        priv_protocol_dropdown.visible = True
        priv_key_input.visible = True
        
        # Заполняем поля значениями по умолчанию
        v3_username_input.value = V3_DEFAULT_USERNAME
        auth_protocol_dropdown.value = V3_DEFAULT_AUTH_PROTOCOL
        auth_key_input.value = V3_DEFAULT_AUTH_KEY
        priv_protocol_dropdown.value = V3_DEFAULT_PRIV_PROTOCOL
        priv_key_input.value = V3_DEFAULT_PRIV_KEY
        
        # Показываем все поля v3
        v3_username_input.visible = True
        auth_protocol_dropdown.visible = True
        auth_key_input.visible = True
        enable_encryption_checkbox.visible = True
        
        page.update()
        
        # Показываем уведомление
        page.snack_bar = ft.SnackBar(
            ft.Text(f"Загружены настройки по умолчанию: {V3_DEFAULT_USERNAME}")
        )
        page.snack_bar.open = True
        page.update()

    async def check_snmp_click(e):
        """Обработчик нажатия кнопки проверки"""
        if not ip_input.value.strip() or not oid_input.value.strip():
            page.snack_bar = ft.SnackBar(ft.Text("Введите IP адрес и OID!"))
            page.snack_bar.open = True
            page.update()
            return

        # Показываем индикатор загрузки
        loading_indicator.visible = True
        check_button.disabled = True
        page.update()

        try:
            if current_snmp_version.value == "v2c":
                # Проверка SNMP v2c
                result = await check_snmp_v2c_async(
                    ip_input.value,
                    oid_input.value,
                    community_input.value or "public"
                )
                version_text = "SNMP v2c"
                version_color = colors["v2c"]
                version_badge_text = "v2c"
            elif current_snmp_version.value == "v3_default":
                # Проверка SNMP v3 с настройками по умолчанию
                result = await check_snmp_v3_async(
                    ip_input.value,
                    oid_input.value,
                    V3_DEFAULT_USERNAME,
                    V3_DEFAULT_AUTH_KEY,
                    V3_DEFAULT_PRIV_KEY,
                    V3_DEFAULT_AUTH_PROTOCOL,
                    V3_DEFAULT_PRIV_PROTOCOL
                )
                version_text = "SNMP v3 (Default)"
                version_color = colors["v3_default"]
                version_badge_text = "v3 ⚡"
            else:
                # Проверка SNMP v3 с ручными настройками
                if not v3_username_input.value.strip():
                    page.snack_bar = ft.SnackBar(ft.Text("Введите Username для SNMP v3!"))
                    page.snack_bar.open = True
                    loading_indicator.visible = False
                    check_button.disabled = False
                    page.update()
                    return

                # Определяем, какой уровень безопасности использовать
                auth_key = auth_key_input.value if auth_key_input.value.strip() else None
                
                if enable_encryption_checkbox.value:
                    priv_key = priv_key_input.value if priv_key_input.value.strip() else None
                    auth_protocol = auth_protocol_dropdown.value
                    priv_protocol = priv_protocol_dropdown.value
                else:
                    priv_key = None
                    auth_protocol = auth_protocol_dropdown.value
                    priv_protocol = None

                result = await check_snmp_v3_async(
                    ip_input.value,
                    oid_input.value,
                    v3_username_input.value,
                    auth_key,
                    priv_key,
                    auth_protocol,
                    priv_protocol
                )
                version_text = "SNMP v3"
                version_color = colors["v3"]
                version_badge_text = "v3"

            if result["success"]:
                result_card = ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text("✅ УСПЕШНО", size=16, weight=ft.FontWeight.BOLD, color=colors["success"]),
                                ft.Container(expand=True),
                                ft.Badge(version_badge_text, bgcolor=version_color, color=ft.Colors.WHITE),
                                ft.Text(f" | IP: {ip_input.value}", size=10, color=ft.Colors.GREY_600)
                            ]),
                            ft.Text(f"OID: {oid_input.value}", size=12, color=ft.Colors.GREY_700),
                            ft.Divider(height=1),
                            ft.Container(
                                content=ft.Text(result["value"], size=12, selectable=True, font_family="Monospace"),
                                padding=10,
                                bgcolor=colors["light"],
                                border_radius=5
                            ),
                            ft.Row([
                                ft.TextButton(
                                    "Копировать значение",
                                    on_click=lambda e, t=result["value"]: copy_to_clipboard(t)
                                ),
                                ft.TextButton(
                                    "Копировать OID",
                                    on_click=lambda e, t=oid_input.value: copy_to_clipboard(t)
                                )
                            ])
                        ], spacing=5),
                        padding=15,
                        width=600
                    ),
                    elevation=2
                )
            else:
                result_card = ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text("❌ ОШИБКА", size=16, weight=ft.FontWeight.BOLD, color=colors["error"]),
                                ft.Container(expand=True),
                                ft.Badge(version_badge_text, bgcolor=version_color, color=ft.Colors.WHITE),
                                ft.Text(f" | IP: {ip_input.value}", size=10, color=ft.Colors.GREY_600)
                            ]),
                            ft.Text(f"OID: {oid_input.value}", size=12, color=ft.Colors.GREY_700),
                            ft.Divider(height=1),
                            ft.Container(
                                content=ft.Text(result["error"], size=12, selectable=True, font_family="Monospace"),
                                padding=10,
                                bgcolor=colors["light"],
                                border_radius=5
                            )
                        ], spacing=5),
                        padding=15,
                        width=600
                    ),
                    elevation=2
                )

            result_output.controls.insert(0, result_card)
            
            # Обновляем счетчик результатов
            result_counter.value = str(len(result_output.controls))
            
            page.update()

        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Ошибка: {str(ex)}"))
            page.snack_bar.open = True
        finally:
            loading_indicator.visible = False
            check_button.disabled = False
            page.update()

    def clear_results(e):
        result_output.controls.clear()
        ip_input.value = ""
        oid_input.value = ""
        community_input.value = "public"
        v3_username_input.value = ""
        auth_key_input.value = ""
        auth_protocol_dropdown.value = "SHA"
        enable_encryption_checkbox.value = False
        priv_protocol_dropdown.value = "AES"
        priv_key_input.value = ""
        result_counter.value = "0"
        
        # Восстанавливаем видимость полей в зависимости от текущей версии
        if current_snmp_version.value == "v2c":
            switch_to_v2c(None)
        elif current_snmp_version.value == "v3_default":
            switch_to_v3_default(None)
        else:
            switch_to_v3(None)
        
        page.update()

    def copy_to_clipboard(text):
        page.set_clipboard(text)
        page.snack_bar = ft.SnackBar(ft.Text("Скопировано в буфер обмена!"))
        page.snack_bar.open = True
        page.update()

    # Индикатор загрузки
    loading_indicator = ft.ProgressRing(visible=False, width=40, height=40, stroke_width=3)
    
    # Счетчик результатов
    result_counter = ft.Text("0")

    # Привязываем обработчики
    v2c_button.on_click = switch_to_v2c
    v3_button.on_click = switch_to_v3
    v3_default_button.on_click = switch_to_v3_default
    check_button.on_click = lambda e: asyncio.create_task(check_snmp_click(e))
    clear_button.on_click = clear_results

    # Собираем интерфейс
    page.add(
        ft.Column([
            ft.Container(
                content=ft.Column([
                    ft.Text("🔍 SNMP OID Checker", size=36, weight=ft.FontWeight.BOLD, color=colors["dark"]),
                    ft.Text("Веб-приложение для проверки SNMP OID (v2c и v3)", size=16, color=ft.Colors.GREY_600),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                margin=ft.margin.only(bottom=30)
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Параметры подключения", size=20, weight=ft.FontWeight.BOLD),
                        ft.Divider(height=1),
                        
                        ft.Row([
                            v2c_button,
                            ft.Container(width=10),
                            v3_button,
                            ft.Container(width=10),
                            v3_default_button
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        
                        ft.Container(height=10),
                        
                        # Подсказка под кнопками
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Выберите режим работы:", size=12, color=ft.Colors.GREY_600),
                                ft.Row([
                                    ft.Text("• v2c: Простая community-аутентификация", size=10, color=colors["v2c"]),
                                    ft.Text("• v3: Настраиваемые параметры", size=10, color=colors["v3"]),
                                    ft.Text("• V3 Default: Быстрая настройка", size=10, color=colors["v3_default"]),
                                ], wrap=True, spacing=10)
                            ], spacing=5),
                            padding=ft.padding.symmetric(vertical=5)
                        ),
                        
                        ft.Container(height=10),
                        
                        ip_input,
                        oid_input,
                        
                        # Параметры v2c (изначально видимые)
                        community_input,
                        
                        # Параметры v3 (изначально скрытые, отображаются при переключении)
                        v3_params_container,
                        
                        ft.Container(height=20),
                        
                        ft.Row([
                            check_button,
                            ft.Container(width=20),
                            clear_button,
                            ft.Container(width=20),
                            loading_indicator
                        ], alignment=ft.MainAxisAlignment.CENTER)
                    ], spacing=15),
                    padding=25,
                    width=550
                ),
                elevation=5
            ),
            
            ft.Container(height=20),
            
            ft.Container(
                content=ft.Column([
                    ft.Text("Часто используемые OID", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text("Кликните для использования", size=12, color=ft.Colors.GREY_600),
                    ft.Container(height=10),
                    oid_cards
                ]),
                width=800
            ),
            
            ft.Container(height=20),
            
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("Результаты проверки", size=20, weight=ft.FontWeight.BOLD),
                        ft.Container(expand=True),
                        ft.Badge("0", ref=result_counter)
                    ]),
                    ft.Divider(height=1),
                    ft.Container(
                        content=result_output,
                        border=ft.border.all(2, ft.Colors.GREY_300),
                        border_radius=10,
                        padding=10,
                        bgcolor=ft.Colors.WHITE
                    )
                ]),
                width=650
            ),
            
            ft.Container(
                content=ft.Column([
                    ft.Divider(),
                    ft.Row([
                        ft.Text("Информация:", size=12, color=ft.Colors.GREY_600),
                        ft.Text("• SNMP v2c: community-based аутентификация", size=12, color=colors["v2c"]),
                        ft.Text("• SNMP v3: user-based аутентификация с поддержкой шифрования", size=12, color=colors["v3"]),
                        ft.Text(f"• V3 Default: {V3_DEFAULT_USERNAME} (SHA+AES)", size=12, color=colors["v3_default"]),
                        ft.Text("• Протоколы: SHA/MD5 для аутентификации, AES/DES для шифрования", size=12, color=colors["dark"]),
                    ], wrap=True, spacing=10)
                ], spacing=10),
                margin=ft.margin.only(top=20)
            )
        ], spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

# Запуск приложения
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
    print("🌐 Откройте браузер по адресу: http://localhost:8080")
    print("=" * 60)
    
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    
    ft.app(
        target=main,
        port=8080,
        view=ft.AppView.WEB_BROWSER
    )