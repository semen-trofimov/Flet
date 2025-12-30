# run.py
import subprocess
import sys
import webbrowser
import time

def run_flet_app():
    print("🚀 Запуск Flet приложения...")
    print("⏳ Пожалуйста, подождите несколько секунд...")
    
    # Запускаем приложение в фоне
    process = subprocess.Popen(
        [sys.executable, "simple_app.py", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Ждем немного для запуска сервера
    time.sleep(2)
    
    # Открываем браузер автоматически
    url = "http://localhost:8000"
    print(f"🌐 Открываю браузер: {url}")
    webbrowser.open(url)
    
    print("\n📋 Инструкции:")
    print("1. Приложение запущено на http://localhost:8000")
    print("2. Нажмите Ctrl+C в этом окне, чтобы остановить приложение")
    print("3. Обновите страницу в браузере, если что-то не загрузилось")
    
    try:
        # Ждем завершения процесса
        process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Останавливаю приложение...")
        process.terminate()
        process.wait()
        print("✅ Приложение остановлено")

if __name__ == "__main__":
    run_flet_app()