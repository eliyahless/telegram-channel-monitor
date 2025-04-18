#!/usr/bin/env python3
"""
Скрипт для создания macOS приложения (.app) из Python-скрипта
"""

import os
import shutil
import stat
import subprocess
import sys

def create_macos_app(app_name="ЛаптопКликер"):
    """Создает macOS приложение (.app bundle) из текущего скрипта"""
    
    # Текущая директория
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Пути к файлам
    script_path = os.path.join(current_dir, "laptop_clicker.py")
    icon_path = os.path.join(current_dir, "icon.png")
    
    # Путь к рабочему столу
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    
    # Путь для создания приложения
    app_bundle_path = os.path.join(desktop_path, f"{app_name}.app")
    
    # Если уже существует, удаляем
    if os.path.exists(app_bundle_path):
        shutil.rmtree(app_bundle_path)
    
    # Создаем структуру .app
    contents_path = os.path.join(app_bundle_path, "Contents")
    macos_path = os.path.join(contents_path, "MacOS")
    resources_path = os.path.join(contents_path, "Resources")
    
    os.makedirs(macos_path, exist_ok=True)
    os.makedirs(resources_path, exist_ok=True)
    
    # Создаем Info.plist
    with open(os.path.join(contents_path, "Info.plist"), "w") as f:
        f.write(f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>{app_name}</string>
    <key>CFBundleIconFile</key>
    <string>icon.icns</string>
    <key>CFBundleIdentifier</key>
    <string>com.myapp.{app_name}</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>{app_name}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.14</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>''')
    
    # Создаем простой AppleScript запускатор
    with open(os.path.join(macos_path, f"{app_name}.applescript"), "w") as f:
        f.write(f'''
tell application "Finder"
    set scriptPath to (path to me as text) & "Contents:Resources:laptop_clicker.py"
    do shell script "/usr/bin/env python3 " & quoted form of POSIX path of scriptPath & " > /dev/null 2>&1 &"
end tell
''')
    
    # Компилируем AppleScript в исполняемый файл
    try:
        app_script = os.path.join(macos_path, f"{app_name}.applescript")
        exec_file = os.path.join(macos_path, app_name)
        
        # Компилируем AppleScript в исполняемый файл
        subprocess.run(["osacompile", "-o", exec_file, app_script], check=True)
        
        # Делаем файл исполняемым (если это отдельный файл, а не бандл)
        if os.path.isfile(exec_file):
            os.chmod(exec_file, 0o755)
            
    except subprocess.CalledProcessError as e:
        print(f"Ошибка компиляции AppleScript: {e}")
        print("Используем shell-script вместо AppleScript...")
        
        # Если компиляция не удалась, создаем shell-скрипт
        with open(os.path.join(macos_path, app_name), "w") as f:
            f.write(f'''#!/bin/sh
# Запуск Python-скрипта без терминала
DIR="$( cd "$( dirname "$0" )" && pwd )"
RESOURCES_DIR="${{DIR}}/../Resources"
PYTHON_SCRIPT="${{RESOURCES_DIR}}/laptop_clicker.py"

# Запускаем скрипт и отключаем вывод
/usr/bin/env python3 "${{PYTHON_SCRIPT}}" > /dev/null 2>&1 &
''')
        # Делаем файл исполняемым
        os.chmod(os.path.join(macos_path, app_name), 0o755)
    
    # Копируем скрипт и ресурсы
    shutil.copy2(script_path, resources_path)
    
    # Копируем иконку
    if os.path.exists(icon_path):
        shutil.copy2(icon_path, resources_path)
        shutil.copy2(icon_path, os.path.join(resources_path, "icon.icns"))
    
    print(f"Приложение создано: {app_bundle_path}")
    
    # Делаем дополнительную настройку для macOS
    try:
        subprocess.run(["xattr", "-cr", app_bundle_path], check=False)
    except:
        pass
    
    # Удаляем временные файлы
    temp_script = os.path.join(macos_path, f"{app_name}.applescript")
    if os.path.exists(temp_script):
        os.remove(temp_script)
    
    return app_bundle_path

if __name__ == "__main__":
    app_path = create_macos_app()
    print(f"Запустите приложение двойным кликом по иконке: {app_path}") 