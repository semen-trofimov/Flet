# simple.py
import flet as ft

def main(page: ft.Page):
    page.title = "Простое приложение"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    name_field = ft.TextField(label="Введите имя", width=200)
    output_text = ft.Text(size=20)
    
    def on_click(e):
        if name_field.value:
            output_text.value = f"Привет, {name_field.value}!"
        else:
            output_text.value = "Введите имя!"
        page.update()
    
    page.add(
        ft.Column([
            ft.Text("Мое приложение", size=30),
            name_field,
            ft.ElevatedButton("Поздороваться", on_click=on_click),
            output_text
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

# Новый способ запуска
ft.app(target=main)