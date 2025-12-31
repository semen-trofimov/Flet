"""
UI компоненты для приложения
"""

import flet as ft
import logging
from config import COLORS, COMMON_OIDS

# Логгер для этого модуля
logger = logging.getLogger(__name__)

def create_input_field(label, hint, width=500, password=False, visible=True):
    """Создает стандартное поле ввода"""
    logger.debug(f"Создание поля ввода: {label}")
    return ft.TextField(
        label=label,
        hint_text=hint,
        width=width,
        border_radius=10,
        border_color=COLORS["primary"],
        password=password,
        can_reveal_password=True if password else False,
        visible=visible
    )

def create_version_button(text, color, is_active=False):
    """Создает кнопку выбора версии SNMP"""
    logger.debug(f"Создание кнопки версии: {text}, активна: {is_active}")
    bgcolor = color if is_active else ft.Colors.GREY_300
    text_color = ft.Colors.WHITE if is_active else COLORS["dark"]
    
    return ft.ElevatedButton(
        text,
        width=120,
        height=40,
        bgcolor=bgcolor,
        color=text_color,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10)
        )
    )

def create_action_button(text, icon=None, color=None, width=200, height=50):
    """Создает кнопку действия"""
    logger.debug(f"Создание кнопки действия: {text}")
    button_text = text
    if icon:
        button_text = f"{icon} {text}"
    
    return ft.FilledButton(
        button_text,
        width=width,
        height=height,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10)
        )
    )

def create_oid_card(oid, description, on_use_click):
    """Создает карточку OID"""
    logger.debug(f"Создание карточки OID: {description} ({oid})")
    return ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Text(description, size=12, weight=ft.FontWeight.BOLD),
                ft.Text(oid, size=10, color=COLORS["primary"], selectable=True),
                ft.TextButton(
                    "Использовать",
                    on_click=lambda e: on_use_click(oid)
                )
            ], spacing=5),
            padding=10,
            width=250
        ),
        elevation=3,
        bgcolor=COLORS["light"]
    )

def create_oid_cards_container(on_use_callback):
    """Создает контейнер с карточками OID"""
    logger.info(f"Создание контейнера OID карточек ({len(COMMON_OIDS)} карточек)")
    oid_cards = ft.Row(wrap=True, spacing=10, run_spacing=10, width=800)
    
    for oid, description in COMMON_OIDS:
        oid_cards.controls.append(
            create_oid_card(oid, description, on_use_callback)
        )
    
    logger.debug("Контейнер OID карточек создан")
    return oid_cards

def create_version_badge(version_text, version_color):
    """Создает бейдж версии (альтернатива Badge)"""
    return ft.Container(
        content=ft.Text(
            version_text,
            size=10,
            color=ft.Colors.WHITE,
            weight=ft.FontWeight.BOLD
        ),
        padding=ft.padding.symmetric(horizontal=8, vertical=2),
        bgcolor=version_color,
        border_radius=15,
        margin=ft.margin.symmetric(horizontal=5)
    )

def create_result_card(result, version_text, version_color, ip, oid):
    """Создает карточку результата"""
    logger.debug(f"Создание карточки результата: {ip} -> {oid[:30]}...")
    
    version_badge = create_version_badge(version_text, version_color)
    
    if result["success"]:
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("✅ УСПЕШНО", size=16, weight=ft.FontWeight.BOLD, color=COLORS["success"]),
                        ft.Container(expand=True),
                        version_badge,
                        ft.Text(f"IP: {ip}", size=10, color=ft.Colors.GREY_600)
                    ]),
                    ft.Text(f"OID: {oid}", size=12, color=ft.Colors.GREY_700, selectable=True),
                    ft.Divider(height=1),
                    ft.Container(
                        content=ft.Text(
                            result["value"], 
                            size=12, 
                            selectable=True, 
                            font_family="monospace",
                            max_lines=5,
                            overflow=ft.TextOverflow.ELLIPSIS
                        ),
                        padding=10,
                        bgcolor=COLORS["light"],
                        border_radius=5
                    ),
                    ft.Row([
                        ft.TextButton(
                            "Копировать значение",
                            on_click=lambda e: logger.info(f"Копирование значения: {ip}")
                        ),
                        ft.TextButton(
                            "Копировать OID",
                            on_click=lambda e: logger.info(f"Копирование OID: {oid}")
                        )
                    ])
                ], spacing=5),
                padding=15,
                width=600
            ),
            elevation=2
        )
    else:
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("❌ ОШИБКА", size=16, weight=ft.FontWeight.BOLD, color=COLORS["error"]),
                        ft.Container(expand=True),
                        version_badge,
                        ft.Text(f"IP: {ip}", size=10, color=ft.Colors.GREY_600)
                    ]),
                    ft.Text(f"OID: {oid}", size=12, color=ft.Colors.GREY_700, selectable=True),
                    ft.Divider(height=1),
                    ft.Container(
                        content=ft.Text(
                            result["error"], 
                            size=12, 
                            selectable=True, 
                            font_family="monospace",
                            color=COLORS["error"]
                        ),
                        padding=10,
                        bgcolor=COLORS["light"],
                        border_radius=5
                    )
                ], spacing=5),
                padding=15,
                width=600
            ),
            elevation=2
        )

def create_v3_parameters_container():
    """Создает контейнер параметров SNMP v3"""
    logger.info("Создание контейнера параметров SNMP v3")
    
    username_input = create_input_field("Username", "SNMP v3 username", visible=False)
    
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
    
    auth_key_input = create_input_field("Auth Key", "Пароль для аутентификации", 
                                        password=True, visible=False)
    
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
    
    priv_key_input = create_input_field("Priv Key", "Пароль для шифрования", 
                                        password=True, visible=False)
    
    enable_encryption_checkbox = ft.Checkbox(
        label="Включить шифрование (Priv)",
        value=False,
        visible=False
    )
    
    logger.debug("Контейнер параметров SNMP v3 создан")
    return {
        "username_input": username_input,
        "auth_protocol_dropdown": auth_protocol_dropdown,
        "auth_key_input": auth_key_input,
        "priv_protocol_dropdown": priv_protocol_dropdown,
        "priv_key_input": priv_key_input,
        "enable_encryption_checkbox": enable_encryption_checkbox
    }