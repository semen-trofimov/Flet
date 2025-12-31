"""
Основное Flet приложение
"""

import flet as ft
import asyncio
import logging
from datetime import datetime
from config import *
from snmp_utils import check_snmp_v2c_async, check_snmp_v3_async
from components import *

# Логгер для этого модуля
logger = logging.getLogger(__name__)

class SNMPCheckerApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.setup_page()
        self.create_ui_elements()
        self.setup_event_handlers()
        self.build_ui()
        
        logger.info("Приложение SNMPChecker инициализировано")
        logger.info(f"Текущий режим: {self.current_snmp_version}")
    
    def setup_page(self):
        self.page.title = APP_TITLE
        self.page.padding = 30
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.scroll = ft.ScrollMode.AUTO
        logger.debug("Страница настроена")
    
    def create_ui_elements(self):
        # Текущая версия SNMP
        self.current_snmp_version = "v2c"
        
        # Основные поля ввода
        self.ip_input = create_input_field("IP адрес устройства", "Например: 192.168.1.1")
        self.oid_input = create_input_field("SNMP OID", "Например: 1.3.6.1.2.1.1.1.0 (sysDescr)")
        self.community_input = create_input_field("Community string", "Обычно 'public' или 'private'")
        self.community_input.value = "public"
        
        # Кнопки версий
        self.v2c_button = create_version_button("SNMP v2c", COLORS["v2c"], True)
        self.v3_button = create_version_button("SNMP v3", COLORS["v3"])
        self.v3_default_button = create_version_button("V3 Default", COLORS["v3_default"])
        
        # Контейнер параметров v3
        v3_params = create_v3_parameters_container()
        self.v3_username_input = v3_params["username_input"]
        self.auth_protocol_dropdown = v3_params["auth_protocol_dropdown"]
        self.auth_key_input = v3_params["auth_key_input"]
        self.priv_protocol_dropdown = v3_params["priv_protocol_dropdown"]
        self.priv_key_input = v3_params["priv_key_input"]
        self.enable_encryption_checkbox = v3_params["enable_encryption_checkbox"]
        
        # Кнопки действий
        self.check_button = create_action_button("Проверить OID", "🔍", width=200)
        self.clear_button = ft.OutlinedButton(
            "🗑️ Очистить",
            width=150,
            height=50,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10)
            )
        )
        
        # Результаты
        self.result_output = ft.Column(
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
            height=300,
            width=600
        )
        # Заменяем Badge на Container для счетчика результатов
        self.result_counter = ft.Container(
            content=ft.Text("0", size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
            padding=ft.padding.symmetric(horizontal=8, vertical=3),
            bgcolor=COLORS["primary"],
            border_radius=15
        )
        self.loading_indicator = ft.ProgressRing(visible=False, width=40, height=40, stroke_width=3)
        
        # Контейнеры
        self.v3_params_container = self.create_v3_params_container()
        self.oid_cards_container = create_oid_cards_container(self.use_common_oid)
        
        logger.debug("UI элементы созданы")
    
    def create_v3_params_container(self):
        return ft.Column(
            [
                self.v3_username_input,
                ft.Row([self.auth_protocol_dropdown], alignment=ft.MainAxisAlignment.START),
                self.auth_key_input,
                self.enable_encryption_checkbox,
                ft.Column([
                    self.priv_protocol_dropdown,
                    self.priv_key_input,
                ], visible=False)
            ],
            spacing=15,
            visible=False
        )
    
    def setup_event_handlers(self):
        self.v2c_button.on_click = self.switch_to_v2c
        self.v3_button.on_click = self.switch_to_v3
        self.v3_default_button.on_click = self.switch_to_v3_default
        self.check_button.on_click = lambda e: asyncio.create_task(self.check_snmp_click(e))
        self.clear_button.on_click = self.clear_results
        self.enable_encryption_checkbox.on_change = self.toggle_encryption_fields
        logger.debug("Обработчики событий настроены")
    
    def build_ui(self):
        self.page.add(
            ft.Column([
                self.create_header(),
                self.create_main_card(),
                ft.Container(height=20),
                self.create_common_oids_section(),
                ft.Container(height=20),
                self.create_results_section(),
                self.create_footer()
            ], spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
        logger.info("UI построен")
    
    def create_header(self):
        return ft.Container(
            content=ft.Column([
                ft.Text(APP_TITLE, size=36, weight=ft.FontWeight.BOLD, color=COLORS["dark"]),
                ft.Text(APP_DESCRIPTION, size=16, color=ft.Colors.GREY_600),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            margin=ft.margin.only(bottom=30)
        )
    
    def create_main_card(self):
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Параметры подключения", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=1),
                    
                    ft.Row([
                        self.v2c_button,
                        ft.Container(width=10),
                        self.v3_button,
                        ft.Container(width=10),
                        self.v3_default_button
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    
                    ft.Container(height=10),
                    self.create_mode_hint(),
                    ft.Container(height=10),
                    
                    self.ip_input,
                    self.oid_input,
                    self.community_input,
                    self.v3_params_container,
                    
                    ft.Container(height=20),
                    
                    ft.Row([
                        self.check_button,
                        ft.Container(width=20),
                        self.clear_button,
                        ft.Container(width=20),
                        self.loading_indicator
                    ], alignment=ft.MainAxisAlignment.CENTER)
                ], spacing=15),
                padding=25,
                width=550
            ),
            elevation=5
        )
    
    def create_mode_hint(self):
        return ft.Container(
            content=ft.Column([
                ft.Text("Выберите режим работы:", size=12, color=ft.Colors.GREY_600),
                ft.Row([
                    ft.Text("• v2c: Простая community-аутентификация", size=10, color=COLORS["v2c"]),
                    ft.Text("• v3: Настраиваемые параметры", size=10, color=COLORS["v3"]),
                    ft.Text("• V3 Default: Быстрая настройка", size=10, color=COLORS["v3_default"]),
                ], wrap=True, spacing=10)
            ], spacing=5),
            padding=ft.padding.symmetric(vertical=5)
        )
    
    def create_common_oids_section(self):
        return ft.Container(
            content=ft.Column([
                ft.Text("Часто используемые OID", size=20, weight=ft.FontWeight.BOLD),
                ft.Text("Кликните для использования", size=12, color=ft.Colors.GREY_600),
                ft.Container(height=10),
                self.oid_cards_container
            ]),
            width=800
        )
    
    def create_results_section(self):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Результаты проверки", size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    self.result_counter  # Используем Container вместо Badge
                ]),
                ft.Divider(height=1),
                ft.Container(
                    content=self.result_output,
                    border=ft.border.all(2, ft.Colors.GREY_300),
                    border_radius=10,
                    padding=10,
                    bgcolor=ft.Colors.WHITE
                )
            ]),
            width=650
        )
    
    def create_footer(self):
        return ft.Container(
            content=ft.Column([
                ft.Divider(),
                ft.Row([
                    ft.Text("Информация:", size=12, color=ft.Colors.GREY_600),
                    ft.Text("• SNMP v2c: community-based аутентификация", size=12, color=COLORS["v2c"]),
                    ft.Text("• SNMP v3: user-based аутентификация с поддержкой шифрования", size=12, color=COLORS["v3"]),
                    ft.Text(f"• V3 Default: {V3_DEFAULT_USERNAME} (SHA+AES)", size=12, color=COLORS["v3_default"]),
                    ft.Text("• Протоколы: SHA/MD5 для аутентификации, AES/DES для шифрования", size=12, color=COLORS["dark"]),
                ], wrap=True, spacing=10)
            ], spacing=10),
            margin=ft.margin.only(top=20)
        )
    
    # Методы обработки событий
    def switch_to_v2c(self, e):
        self.current_snmp_version = "v2c"
        self.update_version_buttons("v2c")
        self.community_input.visible = True
        self.v3_params_container.visible = False
        self.page.update()
        logger.info("Переключен режим на SNMP v2c")
    
    def switch_to_v3(self, e):
        self.current_snmp_version = "v3"
        self.update_version_buttons("v3")
        self.community_input.visible = False
        self.v3_params_container.visible = True
        self.reset_v3_fields()
        self.page.update()
        logger.info("Переключен режим на SNMP v3 (ручные настройки)")
    
    def switch_to_v3_default(self, e):
        self.current_snmp_version = "v3_default"
        self.update_version_buttons("v3_default")
        self.community_input.visible = False
        self.v3_params_container.visible = True
        
        self.enable_encryption_checkbox.value = True
        self.toggle_encryption_fields(None)
        
        self.v3_username_input.value = V3_DEFAULT_USERNAME
        self.auth_protocol_dropdown.value = V3_DEFAULT_AUTH_PROTOCOL
        self.auth_key_input.value = V3_DEFAULT_AUTH_KEY
        self.priv_protocol_dropdown.value = V3_DEFAULT_PRIV_PROTOCOL
        self.priv_key_input.value = V3_DEFAULT_PRIV_KEY
        
        logger.info(f"Переключен режим на SNMP v3 Default: {V3_DEFAULT_USERNAME}")
        self.show_snackbar(f"Загружены настройки по умолчанию: {V3_DEFAULT_USERNAME}")
        self.page.update()
    
    def update_version_buttons(self, active_version):
        buttons = {
            "v2c": self.v2c_button,
            "v3": self.v3_button,
            "v3_default": self.v3_default_button
        }
        
        for version, button in buttons.items():
            if version == active_version:
                button.bgcolor = COLORS[version]
                button.color = ft.Colors.WHITE
            else:
                button.bgcolor = ft.Colors.GREY_300
                button.color = COLORS["dark"]
    
    def reset_v3_fields(self):
        self.enable_encryption_checkbox.value = False
        self.priv_protocol_dropdown.visible = False
        self.priv_key_input.visible = False
        
        self.v3_username_input.visible = True
        self.auth_protocol_dropdown.visible = True
        self.auth_key_input.visible = True
        self.enable_encryption_checkbox.visible = True
        
        self.v3_username_input.value = ""
        self.auth_protocol_dropdown.value = V3_DEFAULT_AUTH_PROTOCOL
        self.auth_key_input.value = ""
        self.priv_protocol_dropdown.value = V3_DEFAULT_PRIV_PROTOCOL
        self.priv_key_input.value = ""
    
    def toggle_encryption_fields(self, e):
        self.priv_protocol_dropdown.visible = self.enable_encryption_checkbox.value
        self.priv_key_input.visible = self.enable_encryption_checkbox.value
        logger.debug(f"Шифрование {'включено' if self.enable_encryption_checkbox.value else 'выключено'}")
        self.page.update()
    
    def use_common_oid(self, oid):
        self.oid_input.value = oid
        logger.info(f"Использован общий OID: {oid}")
        self.page.update()
    
    async def check_snmp_click(self, e):
        if not self.ip_input.value.strip() or not self.oid_input.value.strip():
            error_msg = "Не заполнены IP адрес и/или OID"
            logger.warning(error_msg)
            self.show_snackbar("Введите IP адрес и OID!")
            return
        
        logger.info(f"Начало проверки SNMP: IP={self.ip_input.value}, OID={self.oid_input.value}")
        
        self.loading_indicator.visible = True
        self.check_button.disabled = True
        self.page.update()
        
        try:
            result = await self.perform_snmp_check()
            logger.info(f"Результат проверки: {'Успех' if result['success'] else 'Ошибка'}")
            self.add_result_card(result)
        except Exception as ex:
            error_msg = f"Исключение при проверке SNMP: {str(ex)}"
            logger.error(error_msg, exc_info=True)
            self.show_snackbar(f"Ошибка: {str(ex)}")
        finally:
            self.loading_indicator.visible = False
            self.check_button.disabled = False
            self.page.update()
    
    async def perform_snmp_check(self):
        ip = self.ip_input.value
        oid = self.oid_input.value
        
        if self.current_snmp_version == "v2c":
            logger.info(f"Выполнение SNMP v2c запроса к {ip}")
            return await check_snmp_v2c_async(
                ip, oid, self.community_input.value or "public"
            )
        elif self.current_snmp_version == "v3_default":
            logger.info(f"Выполнение SNMP v3 Default запроса к {ip}")
            return await check_snmp_v3_async(
                ip, oid,
                V3_DEFAULT_USERNAME,
                V3_DEFAULT_AUTH_KEY,
                V3_DEFAULT_PRIV_KEY,
                V3_DEFAULT_AUTH_PROTOCOL,
                V3_DEFAULT_PRIV_PROTOCOL
            )
        else:
            if not self.v3_username_input.value.strip():
                logger.error("SNMP v3: не указан Username")
                raise ValueError("Введите Username для SNMP v3!")
            
            auth_key = self.auth_key_input.value if self.auth_key_input.value.strip() else None
            priv_key = None
            priv_protocol = None
            
            if self.enable_encryption_checkbox.value:
                priv_key = self.priv_key_input.value if self.priv_key_input.value.strip() else None
                priv_protocol = self.priv_protocol_dropdown.value
            
            logger.info(f"Выполнение SNMP v3 запроса к {ip} (User: {self.v3_username_input.value})")
            return await check_snmp_v3_async(
                ip, oid,
                self.v3_username_input.value,
                auth_key,
                priv_key,
                self.auth_protocol_dropdown.value,
                priv_protocol
            )
    
    def add_result_card(self, result):
        version_info = self.get_version_info()
        
        card = create_result_card(
            result,
            version_info["badge"],
            version_info["color"],
            self.ip_input.value,
            self.oid_input.value
        )
        
        self.result_output.controls.insert(0, card)
        
        # Обновляем счетчик результатов
        count = len(self.result_output.controls)
        self.result_counter.content.value = str(count)
        
        # Логируем результат
        if result["success"]:
            logger.info(f"Добавлена карточка успешного результата: {self.ip_input.value}")
        else:
            logger.warning(f"Добавлена карточка ошибки: {self.ip_input.value}")
    
    def get_version_info(self):
        if self.current_snmp_version == "v2c":
            return {"badge": "v2c", "color": COLORS["v2c"]}
        elif self.current_snmp_version == "v3_default":
            return {"badge": "v3 ⚡", "color": COLORS["v3_default"]}
        else:
            return {"badge": "v3", "color": COLORS["v3"]}
    
    def clear_results(self, e):
        logger.info("Очистка результатов и полей ввода")
        
        self.result_output.controls.clear()
        self.ip_input.value = ""
        self.oid_input.value = ""
        self.community_input.value = "public"
        
        # Сбрасываем счетчик
        self.result_counter.content.value = "0"
        
        if self.current_snmp_version == "v2c":
            self.switch_to_v2c(None)
        elif self.current_snmp_version == "v3_default":
            self.switch_to_v3_default(None)
        else:
            self.switch_to_v3(None)
        
        self.page.update()
    
    def show_snackbar(self, message):
        logger.debug(f"Показан snackbar: {message}")
        self.page.snack_bar = ft.SnackBar(ft.Text(message))
        self.page.snack_bar.open = True
        self.page.update()


def main(page: ft.Page):
    logger.info(f"Страница инициализирована: {page.title}")
    logger.info(f"URL страницы: {page.url}")
    app = SNMPCheckerApp(page)