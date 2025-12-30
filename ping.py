import json
import subprocess
import platform
import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

def check_port(ip, port=22, timeout=2):
    """Проверяет доступность порта (например, SSH порт 22)"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except:
        return False

def ping_host(ip, hostname, count=2, timeout=2):
    """
    Пингует хост и возвращает детальный результат
    """
    # Определяем параметры ping в зависимости от ОС
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    
    # Формируем команду ping с учетом ОС
    if platform.system().lower() == 'windows':
        command = ['ping', param, str(count), '-w', str(timeout*1000), ip]
    else:
        command = ['ping', param, str(count), '-W', str(timeout), ip]
    
    try:
        # Выполняем команду ping
        output = subprocess.run(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            encoding='utf-8',
            errors='ignore',
            timeout=timeout+2
        )
        
        if output.returncode == 0:
            # Парсим вывод для получения подробной информации
            output_text = output.stdout
            packet_loss = "N/A"
            
            # Ищем процент потерь
            for line in output_text.split('\n'):
                if 'packet loss' in line.lower() or 'потерь' in line.lower():
                    if '%' in line:
                        parts = line.split('%')
                        for part in parts:
                            if part.strip() and any(char.isdigit() for char in part):
                                loss = ''.join(filter(lambda x: x.isdigit() or x == '.', part))
                                if loss:
                                    packet_loss = f"{loss}%"
                                    break
                    break
            
            # Проверяем доступность порта 22 (SSH) для дополнительной проверки
            port_check = check_port(ip)
            
            return {
                'status': 'UP',
                'packet_loss': packet_loss,
                'port_22_open': port_check,
                'output': output_text[:200] + '...' if len(output_text) > 200 else output_text
            }
        else:
            return {
                'status': 'DOWN',
                'packet_loss': '100%',
                'port_22_open': check_port(ip),
                'output': output.stderr or output.stdout or 'No output'
            }
            
    except subprocess.TimeoutExpired:
        return {
            'status': 'TIMEOUT',
            'packet_loss': '100%',
            'port_22_open': False,
            'output': 'Ping timeout'
        }
    except Exception as e:
        return {
            'status': 'ERROR',
            'packet_loss': 'N/A',
            'port_22_open': False,
            'output': str(e)
        }

def ping_all_devices(json_file, max_workers=10):
    """
    Пингует все устройства из JSON файла
    """
    # Читаем JSON файл
    with open(json_file, 'r', encoding='utf-8') as f:
        devices = json.load(f)
    
    print(f"Пингуем {len(devices)} устройств...")
    print(f"Время начала: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"ОС: {platform.system()} {platform.release()}")
    print("=" * 80)
    
    results = {}
    up_count = 0
    down_count = 0
    
    # Используем многопоточность для ускорения
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Создаем задачи для ping
        future_to_device = {
            executor.submit(ping_host, device['ip'], device['hostname']): device 
            for device in devices
        }
        
        # Обрабатываем результаты по мере их получения
        for future in as_completed(future_to_device):
            device = future_to_device[future]
            ip = device['ip']
            hostname = device['hostname']
            
            try:
                result = future.result()
                results[ip] = {
                    'hostname': hostname,
                    'result': result
                }
                
                # Выводим результат
                if result['status'] == 'UP':
                    print(f"✓ {hostname:25} ({ip:15}) - ДОСТУПНО")
                    if result['packet_loss'] != 'N/A':
                        print(f"  Потери пакетов: {result['packet_loss']}")
                    if result['port_22_open']:
                        print(f"  Порт 22 (SSH): открыт")
                    up_count += 1
                else:
                    print(f"✗ {hostname:25} ({ip:15}) - {result['status']}")
                    if result['packet_loss'] != 'N/A':
                        print(f"  Потери пакетов: {result['packet_loss']}")
                    if result['port_22_open']:
                        print(f"  Порт 22 (SSH): открыт (но ping не работает)")
                    down_count += 1
                
                print(f"  Подробности: {result['output'][:50]}...")
                print()
                    
            except Exception as e:
                print(f"✗ {hostname:25} ({ip:15}) - ОШИБКА: {str(e)}")
                down_count += 1
                print()
    
    # Сводная статистика
    print("\n" + "=" * 80)
    print("ИТОГ:")
    print("=" * 80)
    print(f"Всего устройств: {len(devices)}")
    print(f"Доступно: {up_count}")
    print(f"Недоступно: {down_count}")
    print(f"Время окончания: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Дополнительная диагностика
    print("\n" + "=" * 80)
    print("ДИАГНОСТИКА:")
    print("=" * 80)
    
    # Проверяем свой собственный доступ в интернет
    print("\n1. Проверка доступа в интернет:")
    try:
        internet_test = ping_host("8.8.8.8", "Google DNS")
        if internet_test['status'] == 'UP':
            print("   ✓ Доступ в интернет есть")
        else:
            print("   ✗ Нет доступа в интернет")
    except:
        print("   ? Не удалось проверить доступ в интернет")
    
    # Проверяем локальный хост
    print("\n2. Проверка локального хоста:")
    try:
        local_test = ping_host("127.0.0.1", "localhost")
        if local_test['status'] == 'UP':
            print("   ✓ Локальный хост доступен")
        else:
            print("   ✗ Локальный хост недоступен (проблема с системой)")
    except:
        print("   ? Не удалось проверить локальный хост")
    
    # Проверяем шлюз по умолчанию (если можем его определить)
    print("\n3. Рекомендации по устранению:")
    if up_count == 0:
        print("   - Все устройства недоступны. Возможные причины:")
        print("     * Брандмауэр блокирует ICMP (ping)")
        print("     * Сетевое подключение отсутствует")
        print("     * Устройства находятся в другой подсети")
        print("     * Устройства выключены или не настроены")
        print("   - Попробуйте:")
        print("     * Проверить сетевое подключение")
        print("     * Отключить брандмауэр на время теста")
        print("     * Использовать tracert/traceroute до одного из устройств")
    else:
        print(f"   - Доступно {up_count} из {len(devices)} устройств")
    
    return results

# Основная функция
if __name__ == "__main__":
    # Укажите путь к вашему JSON файлу
    json_file = "fixed_devices.json"
    
    try:
        # Выполняем ping всех устройств
        ping_all_devices(json_file, max_workers=20)
            
    except FileNotFoundError:
        print(f"Ошибка: Файл '{json_file}' не найден.")
        print("Убедитесь, что файл находится в той же директории, что и скрипт.")
    except json.JSONDecodeError:
        print(f"Ошибка: Файл '{json_file}' содержит некорректный JSON.")
    except Exception as e:
        print(f"Неожиданная ошибка: {str(e)}")