# simple_app.py
import flet as ft
import random

def main(page: ft.Page):
    page.title = "✨ Красивое приложение"
    page.padding = 50
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    colors = ["#3b82f6", "#10b981", "#ef4444", "#8b5cf6", "#f59e0b"]
    
    name_input = ft.TextField(
        label="Ваше имя",
        width=300,
        border_radius=10,
        border_color="#3b82f6",
        prefix_icon="person"
    )
    
    result = ft.Text(size=28, weight=ft.FontWeight.BOLD, text_align="center")
    
    def greet(e):
        if name_input.value.strip():
            greetings = [
                f"Привет, {name_input.value}! 👋",
                f"Здравствуй, {name_input.value}! 😊",
                f"Рад видеть тебя, {name_input.value}! 🎉"
            ]
            result.value = random.choice(greetings)
            result.color = random.choice(colors)
        else:
            result.value = "Введите имя! ✏️"
            result.color = "#ef4444"
        page.update()
    
    def clear(e):
        name_input.value = ""
        result.value = ""
        page.update()
    
    page.add(
        ft.Column([
            ft.Container(
                content=ft.Text("✨", size=100),
                margin=ft.margin.only(bottom=20)
            ),
            
            ft.Text("Добро пожаловать!", 
                   size=36, 
                   weight=ft.FontWeight.BOLD,
                   color="#3b82f6"),
            
            ft.Text("Простое и красивое приложение на Flet",
                   size=16,
                   color="#6b7280",
                   italic=True),
            
            ft.Container(height=30),
            
            name_input,
            
            ft.Container(height=20),
            
            ft.Row([
                ft.FilledButton("👋 Поздороваться", on_click=greet, icon="waving_hand"),
                ft.OutlinedButton("🗑️ Очистить", on_click=clear, icon="delete"),
            ], alignment="center"),
            
            ft.Container(height=30),
            
            ft.Container(
                content=result,
                padding=25,
                border_radius=15,
                bgcolor="#f8fafc",
                border=ft.border.all(2, "#e5e7eb"),
                width=400,
                alignment=ft.alignment.Alignment(0, 0)
            ),
            
            ft.Container(height=40),
            
            ft.Text("💡 Попробуйте ввести свое имя!",
                   size=14,
                   color="#9ca3af",
                   italic=True)
        ], spacing=10, horizontal_alignment="center")
    )

# Запуск
ft.run(main, port=8000)