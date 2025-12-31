#!/usr/bin/env python
"""
SNMP Checker App - Веб-приложение для проверки SNMP OID
Требуется: pip install flet pysnmp
"""

import flet as ft
import asyncio
from pysnmp.hlapi.v3arch.asyncio import *

# Асинхронная функция для проверки SNMP
async def check_snmp_async(ip, oid, community="public"):
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
        "success": "#10b981",
        "error": "#ef4444",
        "warning": "#f59e0b",
        "dark": "#1f2937",
        "light": "#f8fafc"
    }

    # Элементы ввода
    ip_input = ft.TextField(
        label="IP адрес устройства",
        hint_text="Например: 192.168.1.1",
        width=400,
        border_radius=10,
        border_color=colors["primary"],
        keyboard_type=ft.KeyboardType.TEXT
    )

    oid_input = ft.TextField(
        label="SNMP OID",
        hint_text="Например: 1.3.6.1.2.1.1.1.0 (sysDescr)",
        width=400,
        border_radius=10,
        border_color=colors["primary"],
        keyboard_type=ft.KeyboardType.TEXT
    )

    community_input = ft.TextField(
        label="Community string",
        hint_text="Обычно 'public' или 'private'",
        width=400,
        border_radius=10,
        border_color=colors["primary"],
        value="public"
    )

    # Кнопки действий
    check_button = ft.FilledButton(
        "🔍 Проверить OID",
        width=200,
        height=50
    )

    clear_button = ft.OutlinedButton(
        "🗑️ Очистить",
        width=150,
        height=50
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

    async def check_snmp_click(e):
        """Обработчик нажатия кнопки проверки"""
        if not ip_input.value.strip() or not oid_input.value.strip():
            # Показываем ошибку
            page.snack_bar = ft.SnackBar(ft.Text("Введите IP адрес и OID!"))
            page.snack_bar.open = True
            page.update()
            return

        # Показываем индикатор загрузки
        loading_indicator.visible = True
        check_button.disabled = True
        page.update()

        try:
            result = await check_snmp_async(
                ip_input.value,
                oid_input.value,
                community_input.value or "public"
            )

            if result["success"]:
                result_card = ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text("✅ УСПЕШНО", size=16, weight=ft.FontWeight.BOLD, color=colors["success"]),
                                ft.Container(expand=True),
                                ft.Text(f"IP: {ip_input.value}", size=10, color=ft.Colors.GREY_600)
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
                                    "Копировать",
                                    on_click=lambda e, t=result["value"]: copy_to_clipboard(t)
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
                                ft.Text(f"IP: {ip_input.value}", size=10, color=ft.Colors.GREY_600)
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
        result_counter.value = "0"
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
    check_button.on_click = lambda e: asyncio.create_task(check_snmp_click(e))
    clear_button.on_click = clear_results

    # Собираем интерфейс
    page.add(
        ft.Column([
            ft.Container(
                content=ft.Column([
                    ft.Text("🔍 SNMP OID Checker", size=36, weight=ft.FontWeight.BOLD, color=colors["dark"]),
                    ft.Text("Веб-приложение для проверки SNMP OID", size=16, color=ft.Colors.GREY_600),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                margin=ft.margin.only(bottom=30)
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Параметры подключения", size=20, weight=ft.FontWeight.BOLD),
                        ft.Divider(height=1),
                        ip_input,
                        oid_input,
                        community_input,
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
                    width=500
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
                        # Исправленный Badge - передаем текст напрямую
                        ft.Badge("0", ref=result_counter)  # Исправлено
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
            )
        ], spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

# Запуск приложения
if __name__ == "__main__":
    print("=" * 50)
    print("🚀 SNMP Checker запускается...")
    print("📡 Откройте браузер по адресу: http://localhost:8080")
    print("=" * 50)
    
    # Игнорируем предупреждение о deprecated app()
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    
    # Используем ft.app() - это работает
    ft.app(
        target=main,
        port=8080,
        view=ft.AppView.WEB_BROWSER
    )