#!/usr/bin/env python3
"""
Скрипт для сборки защищенного приложения Secure Notebook Access
Этот скрипт создает автономный исполняемый файл, который можно запустить без Python
"""

import os
import sys
import platform
import subprocess
import shutil
import time

def create_icon():
    """Создает иконку для приложения"""
    # Простой лого в формате ASCII
    print("Создание иконки для приложения...")
    
    # На разных платформах разные требования к иконкам
    system = platform.system()
    
    if system == "Windows":
        # Для Windows нужен .ico файл
        print("Для Windows требуется .ico файл для иконки.")
        print("Будет использована стандартная иконка Python.")
    elif system == "Darwin":  # macOS
        # Для macOS нужен .icns файл
        print("Для macOS требуется .icns файл для иконки.")
        print("Будет использована стандартная иконка Python.")
    else:  # Linux
        # Для Linux обычно используется .png
        print("Для Linux требуется .png файл для иконки.")
        print("Будет использована стандартная иконка Python.")
    
    print("Иконка настроена успешно.")
    return True

def build_app():
    """Создает исполняемый файл с помощью PyInstaller"""
    print("\n=== Сборка защищенного приложения ===")
    print("Этот процесс займет некоторое время...")
    
    system = platform.system()
    
    # Создаем папку для сборки, если её нет
    if not os.path.exists("build"):
        os.makedirs("build")
    
    # Параметры для PyInstaller
    app_name = "SecureNotebookAccess"
    main_script = "gui_app.py"
    
    # Дополнительные файлы для включения в сборку
    additional_files = [
        "check_ip.py",
        "check_webrtc.py",
        "privacy_enhance.py",
        "vpn_guide.md",
        "requirements.txt"
    ]
    
    # Проверяем, что все файлы существуют
    for file in additional_files + [main_script]:
        if not os.path.exists(file):
            print(f"Ошибка: Файл {file} не найден!")
            return False
    
    # Формируем команду для PyInstaller
    pyinstaller_cmd = [
        "pyinstaller",
        "--name=" + app_name,
        "--onefile",  # Создаем один исполняемый файл
        "--windowed",  # Без консольного окна (для GUI приложений)
        "--clean",  # Очищаем кэш перед сборкой
        "--log-level=INFO",
        # "--icon=app_icon.ico" если у вас есть иконка
    ]
    
    # Добавляем дополнительные файлы
    for file in additional_files:
        pyinstaller_cmd.append("--add-data=" + file + os.pathsep + ".")
    
    # Добавляем главный скрипт
    pyinstaller_cmd.append(main_script)
    
    print("Запуск PyInstaller с параметрами:")
    print(" ".join(pyinstaller_cmd))
    
    try:
        # Запускаем PyInstaller
        subprocess.run(pyinstaller_cmd, check=True)
        
        # Проверяем, что исполняемый файл создан
        dist_dir = "dist"
        if system == "Windows":
            exe_path = os.path.join(dist_dir, app_name + ".exe")
        else:
            exe_path = os.path.join(dist_dir, app_name)
        
        if os.path.exists(exe_path):
            print(f"\nУспешно создан исполняемый файл: {exe_path}")
            
            # Копируем исполняемый файл в корневую директорию для удобства
            target_path = app_name + (".exe" if system == "Windows" else "")
            shutil.copy2(exe_path, target_path)
            print(f"Файл скопирован в: {os.path.abspath(target_path)}")
            return True
        else:
            print(f"Ошибка: Исполняемый файл не найден по пути {exe_path}")
            return False
    
    except Exception as e:
        print(f"Ошибка при сборке приложения: {e}")
        return False

def create_secure_readme():
    """Создает README файл с инструкциями по безопасности"""
    readme_path = "SecureAccess_README.txt"
    
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("=== Secure Notebook Access ===\n\n")
        f.write("Это приложение создано для безопасного доступа к Notebook LM из России.\n\n")
        
        f.write("== Инструкции по безопасности ==\n\n")
        f.write("1. Перед использованием приложения активируйте ваш VPN\n")
        f.write("2. Используйте приложение только для личных образовательных целей\n")
        f.write("3. Не распространяйте приложение - оно создано только для вашего личного использования\n")
        f.write("4. Регулярно проверяйте обновления системы и VPN-клиента\n\n")
        
        f.write("== Запуск приложения ==\n\n")
        
        system = platform.system()
        if system == "Windows":
            f.write("Запустите файл SecureNotebookAccess.exe двойным кликом\n\n")
        elif system == "Darwin":  # macOS
            f.write("1. Откройте терминал\n")
            f.write("2. Перейдите в директорию с приложением: cd путь/к/папке\n")
            f.write("3. Сделайте файл исполняемым: chmod +x SecureNotebookAccess\n")
            f.write("4. Запустите приложение: ./SecureNotebookAccess\n\n")
        else:  # Linux
            f.write("1. Откройте терминал\n")
            f.write("2. Перейдите в директорию с приложением: cd путь/к/папке\n")
            f.write("3. Сделайте файл исполняемым: chmod +x SecureNotebookAccess\n")
            f.write("4. Запустите приложение: ./SecureNotebookAccess\n\n")
        
        f.write("== Функции приложения ==\n\n")
        f.write("- Проверка IP-адреса и статуса VPN\n")
        f.write("- Тестирование на утечки WebRTC\n")
        f.write("- Настройка Яндекс.Браузера\n")
        f.write("- Защищенный доступ к Notebook LM\n")
        f.write("- Инструменты повышения приватности\n\n")
        
        f.write("== Техническая поддержка ==\n\n")
        f.write("Это приложение создано для личного использования.\n")
        f.write("При возникновении проблем, проверьте:\n")
        f.write("1. Активен ли ваш VPN\n")
        f.write("2. Настроен ли браузер согласно инструкциям\n")
        f.write("3. Не блокирует ли ваш антивирус приложение\n\n")
        
        f.write("Используйте приложение ответственно и только в законных целях.")
    
    print(f"Создан файл инструкций: {os.path.abspath(readme_path)}")
    return True

def main():
    """Основная функция сборки приложения"""
    print("=="*30)
    print("      СБОРКА ЗАЩИЩЕННОГО ПРИЛОЖЕНИЯ SECURE NOTEBOOK ACCESS")
    print("=="*30)
    print("\nЭтот скрипт создаст защищенное автономное приложение для")
    print("безопасного доступа к Notebook LM с вашего компьютера.\n")
    
    # Проверяем наличие PyInstaller
    try:
        subprocess.run(["pyinstaller", "--version"], check=True, capture_output=True)
    except:
        print("Ошибка: PyInstaller не установлен. Установите его командой:")
        print("pip install pyinstaller")
        return
    
    # Проверяем наличие всех необходимых файлов
    required_files = ["gui_app.py", "check_ip.py"]
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print("Ошибка: Следующие файлы не найдены:")
        for file in missing_files:
            print(f" - {file}")
        return
    
    # Создаем иконку приложения
    if not create_icon():
        print("Предупреждение: Не удалось создать иконку. Продолжаем без иконки.")
    
    # Создаем README с инструкциями по безопасности
    if not create_secure_readme():
        print("Предупреждение: Не удалось создать инструкции. Продолжаем без них.")
    
    # Собираем приложение
    if not build_app():
        print("\nСборка приложения завершилась с ошибкой.")
        print("Пожалуйста, проверьте вывод ошибок выше.")
        return
    
    print("\n" + "=="*30)
    print("      СБОРКА ЗАВЕРШЕНА УСПЕШНО")
    print("=="*30)
    print("\nПриложение готово к использованию!")
    print("Теперь у вас есть защищенное автономное приложение для доступа к Notebook LM.")
    
    # Показываем инструкции по запуску в зависимости от ОС
    system = platform.system()
    print("\nИнструкции по запуску приложения:")
    
    if system == "Windows":
        print("Запустите файл SecureNotebookAccess.exe двойным кликом")
    elif system == "Darwin":  # macOS
        print("1. Откройте терминал")
        print("2. Перейдите в директорию с приложением: cd путь/к/папке")
        print("3. Сделайте файл исполняемым: chmod +x SecureNotebookAccess")
        print("4. Запустите приложение: ./SecureNotebookAccess")
    else:  # Linux
        print("1. Откройте терминал")
        print("2. Перейдите в директорию с приложением: cd путь/к/папке")
        print("3. Сделайте файл исполняемым: chmod +x SecureNotebookAccess")
        print("4. Запустите приложение: ./SecureNotebookAccess")
    
    print("\nПодробные инструкции по безопасному использованию приложения")
    print("находятся в файле SecureAccess_README.txt")

if __name__ == "__main__":
    main() 