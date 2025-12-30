# styles.py (дополнительный файл для стилей)
class AppStyles:
    PRIMARY_COLOR = "#3b82f6"
    SECONDARY_COLOR = "#8b5cf6"
    SUCCESS_COLOR = "#10b981"
    DANGER_COLOR = "#ef4444"
    WARNING_COLOR = "#f59e0b"
    LIGHT_BG = "#f8fafc"
    DARK_BG = "#1f2937"
    
    CARD_STYLE = {
        "elevation": 8,
        "shadow_color": "0x20000000",
        "surface_tint_color": "white",
        "margin": 10
    }
    
    BUTTON_STYLE = ft.ButtonStyle(
        shape=ft.RoundedRectangleBorder(radius=10),
        padding=ft.padding.symmetric(horizontal=25, vertical=12)
    )