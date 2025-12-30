# app.py
import flet as ft
import random
import socket
import sys
from datetime import datetime

def main(page: ft.Page):
    page.title = "✨ Красивое приложение"
    page.padding = 50
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO  # Добавляем скролл при необходимости
    
    colors = ["#3b82f6", "#10b981", "#ef4444", "#8b5cf6", "#f59e0b", "#ec4899"]
    
    # Добавляем обработчик Enter в поле ввода
    def on_enter(e):
        if name_input.value.strip():
            greet(e)
    
    name_input = ft.TextField(
        label="Ваше имя",
        width=300,
        border_radius=10,
        border_color="#3b82f6",
        on_submit=on_enter,  # Обработка нажатия Enter
        hint_text="Введите ваше имя здесь...",
        text_size=16
    )
    
    result = ft.Text(size=28, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
    status_text = ft.Text(size=14, color="#6b7280", italic=True)
    
    def greet(e):
        if name_input.value.strip():
            greetings = [
                f"Привет, {name_input.value}! 👋",
                f"Здравствуй, {name_input.value}! 😊",
                f"Рад видеть тебя, {name_input.value}! 🎉",
                f"Приветствую, {name_input.value}! 🌟",
                f"Добро пожаловать, {name_input.value}! 🚀"
            ]
            result.value = random.choice(greetings)
            result.color = random.choice(colors)
            status_text.value = f"Приветствие отправлено в {datetime.now().strftime('%H:%M:%S')}"
        else:
            result.value = "Пожалуйста, введите имя! ✏️"
            result.color = "#ef4444"
            status_text.value = "Ожидание ввода имени..."
        page.update()
    
    def clear(e):
        name_input.value = ""
        result.value = ""
        status_text.value = "Готов к приветствиям..."
        name_input.focus()  # Фокус на поле ввода
        page.update()
    
    # Иконки для кнопок
    greet_btn = ft.FilledButton(
        text="👋 Поздороваться",
        on_click=greet,
        icon="waving_hand",
        style=ft.ButtonStyle(
            padding=ft.Padding(20, 10, 20, 10)
        )
    )
    
    clear_btn = ft.OutlinedButton(
        text="🗑️ Очистить",
        on_click=clear,
        icon="delete"
    )
    
    page.add(
        ft.Column([
            ft.Container(
                content=ft.Icon("rocket_launch", size=80, color="#3b82f6"),
                margin=ft.margin.only(bottom=20)
            ),
            ft.Text("Приложение в браузере", 
                   size=36, 
                   weight=ft.FontWeight.BOLD,
                   color="#3b82f6",
                   text_align=ft.TextAlign.CENTER),
            ft.Text("Запущено в веб-режиме",
                   size=16,
                   color="#6b7280",
                   italic=True,
                   text_align=ft.TextAlign.CENTER),
            ft.Container(height=30),
            name_input,
            ft.Container(height=20),
            ft.Row([
                greet_btn,
                clear_btn,
            ], 
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20),
            ft.Container(height=20),
            status_text,
            ft.Container(height=30),
            ft.Container(
                content=result,
                padding=25,
                border_radius=15,
                bgcolor="#f8fafc",
                border=ft.Border.all(2, "#e5e7eb"),
                width=400,
                alignment=ft.alignment.center
            ),
            ft.Container(height=40),
            ft.Text(f"✅ Приложение работает в браузере",
                   size=14,
                   color="#10b981",
                   weight=ft.FontWeight.BOLD,
                   text_align=ft.TextAlign.CENTER)
        ], 
        spacing=10, 
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        scroll=ft.ScrollMode.AUTO)
    )
    
    # Фокус на поле ввода при загрузке
    name_input.focus()

# Функция запуска с проверкой порта
def run_app(port=80):
    """Запуск приложения на указанном порту"""
    try:
        # Проверяем, доступен ли порт
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as test_socket:
            test_socket.bind(('0.0.0.0', port))
        
        print("=" * 60)
        print(f"🚀 ЗАПУСК В БРАУЗЕРЕ НА ПОРТУ {port}")
        print("=" * 60)
        
        if port == 80:
            print("🌐 Откройте в браузере: http://localhost")
        else:
            print(f"🌐 Откройте в браузере: http://localhost:{port}")
        
        # Дополнительные ссылки
        print(f"📱 Также доступно по IP: http://127.0.0.1:{port}")
        print("🛑 Для остановки нажмите Ctrl+C")
        print("=" * 60)
        
        # Запускаем приложение
        ft.run(
            target=main,
            port=port,
            host="0.0.0.0",
            view=ft.AppView.WEB_BROWSER
        )
        
    except PermissionError:
        print("\n❌ ОШИБКА: Недостаточно прав для порта 80!")
        print("\n📋 РЕШЕНИЕ: Используем порт 8080")
        run_app(port=8080)
            
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n⚠️  Порт {port} занят. Пробую порт 8080...")
            run_app(port=8080)
        else:
            print(f"\n❌ Неизвестная ошибка: {e}")
            print("Пробую порт 8080...")
            run_app(port=8080)

if __name__ == "__main__":
    try:
        run_app(port=80)
    except KeyboardInterrupt:
        print("\n\n👋 Приложение остановлено пользователем")
        sys.exit(0)