# app.py
import flet as ft

def main(page: ft.Page):
    # Настройки страницы
    page.title = "✨ Мое первое Flet-приложение"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    
    # Элементы интерфейса
    txt_name = ft.TextField(
        label="Ваше имя", 
        width=300,
        hint_text="Введите ваше имя здесь..."
    )
    
    txt_result = ft.Text(size=24, weight=ft.FontWeight.BOLD)
    
    # Функции
    def say_hello(e):
        if txt_name.value.strip():
            txt_result.value = f"Привет, {txt_name.value}! 👋"
            txt_result.color = "green"
        else:
            txt_result.value = "Пожалуйста, введите имя! 📝"
            txt_result.color = "red"
        page.update()
    
    def clear_all(e):
        txt_name.value = ""
        txt_result.value = ""
        page.update()
    
    # Сборка интерфейса
    page.add(
        ft.Column([
            ft.Text("✨", size=100, text_align=ft.TextAlign.CENTER),
            
            ft.Text("Добро пожаловать в Flet!", 
                   size=32, 
                   weight=ft.FontWeight.BOLD,
                   text_align=ft.TextAlign.CENTER),
            
            ft.Text("Это простое приложение на Python!",
                   size=16,
                   color="gray",
                   text_align=ft.TextAlign.CENTER),
            
            ft.Container(height=20),
            
            txt_name,
            
            ft.Row([
                ft.FilledButton("👋 Поздороваться", on_click=say_hello),
                ft.OutlinedButton("🗑️ Очистить", on_click=clear_all),
            ], alignment=ft.MainAxisAlignment.CENTER),
            
            ft.Container(height=20),
            
            ft.Container(
                content=txt_result,
                padding=20,
                border_radius=10,
                bgcolor="#f5f5f5",
                width=400,
                alignment=ft.alignment.Alignment(0, 0)
            ),
            
            ft.Divider(height=30),
            
            ft.Text("💡 Попробуй ввести свое имя и нажать кнопку!",
                   size=14,
                   italic=True,
                   color="blue")
        ], 
        spacing=10,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

# Запуск приложения - ПРАВИЛЬНЫЙ СПОСОБ
if __name__ == "__main__":
    # Вариант 1: Самый простой
    ft.app(main)
    
    # Вариант 2: С указанием порта
    # ft.app(main, port=8000)