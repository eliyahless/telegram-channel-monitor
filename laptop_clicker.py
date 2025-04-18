import tkinter as tk
import subprocess
import sys
import os
import json
from tkinter import messagebox

class LaptopClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("Кликер для ноутбука")
        self.root.geometry("400x380")
        self.root.resizable(False, False)
        
        # Находим текущую директорию
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Настройка иконки
        try:
            icon_path = self.resource_path("icon.png")
            if os.path.exists(icon_path):
                self.root.iconphoto(True, tk.PhotoImage(file=icon_path))
            else:
                print(f"Иконка не найдена: {icon_path}")
        except Exception as e:
            print(f"Ошибка при установке иконки: {e}")
        
        # Настраиваем стиль
        bg_color = "#f0f0f0"
        self.root.config(bg=bg_color)
        
        # Состояние приложения
        self.is_enabled = False
        
        # Загружаем настройки или используем значения по умолчанию
        self.settings = self.load_settings()
        
        # Создание рамки
        self.main_frame = tk.Frame(root, padx=30, pady=20, bg=bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        self.title_label = tk.Label(
            self.main_frame, 
            text="Кликер для входа в ноутбук",
            font=("Arial", 16, "bold"),
            bg=bg_color
        )
        self.title_label.pack(pady=(0, 15))
        
        # Индикатор состояния
        self.status_frame = tk.Frame(self.main_frame, bg=bg_color)
        self.status_frame.pack(pady=(0, 15), fill=tk.X)
        
        self.status_label = tk.Label(
            self.status_frame,
            text="Статус:",
            font=("Arial", 12),
            bg=bg_color
        )
        self.status_label.pack(side=tk.LEFT, padx=(50, 5))
        
        self.status_value = tk.Label(
            self.status_frame,
            text="Отключено",
            font=("Arial", 12, "bold"),
            fg="red",
            bg=bg_color
        )
        self.status_value.pack(side=tk.LEFT)
        
        # Фрейм для настроек
        self.settings_frame = tk.LabelFrame(self.main_frame, text="Настройки", padx=15, pady=10, bg=bg_color)
        self.settings_frame.pack(pady=(0, 15), fill=tk.X)
        
        # Выбор приложения
        self.app_label = tk.Label(self.settings_frame, text="Приложение:", bg=bg_color)
        self.app_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        self.app_var = tk.StringVar(value=self.settings.get("app", "Terminal"))
        self.app_entry = tk.Entry(self.settings_frame, textvariable=self.app_var, width=25)
        self.app_entry.grid(row=0, column=1, padx=5, pady=5)
        
        self.save_button = tk.Button(self.settings_frame, text="Сохранить", command=self.save_settings)
        self.save_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Большая одиночная кнопка
        self.button_frame = tk.Frame(self.main_frame, bg=bg_color)
        self.button_frame.pack(pady=(0, 15), fill=tk.X)
        
        # Создаем единую кнопку переключения
        self.toggle_button = tk.Button(
            self.button_frame,
            text="Включить",
            command=self.toggle_app,
            width=25,
            height=3,
            font=("Arial", 12, "bold"),
            relief=tk.RAISED,
            bd=3,
            bg="#4CAF50",  # Зеленый фон для кнопки
            fg="white"     # Белый текст
        )
        self.toggle_button.pack(pady=10)
        
    def load_settings(self):
        """Загрузка настроек из файла"""
        try:
            # Сначала ищем в текущей директории
            settings_file = os.path.join(self.current_dir, "settings.json")
            
            if not os.path.exists(settings_file):
                # Если не найдено, ищем в родительской директории (для .app бандла)
                parent_dir = os.path.dirname(self.current_dir)
                settings_file = os.path.join(parent_dir, "settings.json")
            
            if os.path.exists(settings_file):
                with open(settings_file, "r") as f:
                    return json.load(f)
        except Exception as e:
            print(f"Ошибка при загрузке настроек: {e}")
            
        return {"app": "Terminal"}  # Значения по умолчанию
    
    def save_settings(self):
        """Сохранение настроек в файл"""
        try:
            settings_file = os.path.join(self.current_dir, "settings.json")
            
            # Обновляем настройки
            self.settings["app"] = self.app_var.get()
            
            # Сохраняем в файл
            with open(settings_file, "w") as f:
                json.dump(self.settings, f)
                
            messagebox.showinfo("Успех", "Настройки сохранены!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить настройки: {str(e)}")
    
    def toggle_app(self):
        """Переключает состояние приложения с одного клика"""
        if not self.is_enabled:
            self.enable_app()
        else:
            self.disable_app()
    
    def enable_app(self):
        """Включить приложение"""
        self.is_enabled = True
        self.status_value.config(text="Включено", fg="green")
        self.toggle_button.config(text="Отключить", bg="#F44336")
        
        # Меняем фон всего приложения для индикации активности
        self.root.config(bg="#E8F5E9")  # Светло-зеленый фон
        self.main_frame.config(bg="#E8F5E9")
        self.status_frame.config(bg="#E8F5E9")
        self.title_label.config(bg="#E8F5E9")
        self.status_label.config(bg="#E8F5E9")
        self.status_value.config(bg="#E8F5E9")
        self.settings_frame.config(bg="#E8F5E9")
        self.app_label.config(bg="#E8F5E9")
        self.button_frame.config(bg="#E8F5E9")
        
        # Получаем имя приложения из настроек
        app_name = self.app_var.get().strip()
        if not app_name:
            app_name = "Terminal"  # Значение по умолчанию
        
        # Запускаем выбранное приложение без показа терминала
        try:
            # Для macOS - используем subprocess с DEVNULL для скрытия вывода
            if sys.platform == "darwin":
                # Создаем скрытый процесс
                DEVNULL = subprocess.DEVNULL
                subprocess.Popen(["open", "-a", app_name], 
                                stdout=DEVNULL, stderr=DEVNULL, 
                                start_new_session=True)
            # Для Windows
            elif sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                subprocess.Popen([app_name], startupinfo=startupinfo, 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # Для Linux
            elif sys.platform.startswith("linux"):
                subprocess.Popen([app_name], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, 
                                start_new_session=True)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить приложение: {str(e)}")
        
    def disable_app(self):
        """Отключить приложение"""
        self.is_enabled = False
        self.status_value.config(text="Отключено", fg="red")
        self.toggle_button.config(text="Включить", bg="#4CAF50")
        
        # Возвращаем стандартный фон для индикации неактивности 
        bg_color = "#f0f0f0"
        self.root.config(bg=bg_color)
        self.main_frame.config(bg=bg_color)
        self.status_frame.config(bg=bg_color) 
        self.title_label.config(bg=bg_color)
        self.status_label.config(bg=bg_color)
        self.status_value.config(bg=bg_color)
        self.settings_frame.config(bg=bg_color)
        self.app_label.config(bg=bg_color)
        self.button_frame.config(bg=bg_color)
        
        # Получаем имя приложения из настроек
        app_name = self.app_var.get().strip()
        if not app_name:
            app_name = "Terminal"  # Значение по умолчанию
        
        # Закрываем запущенное приложение без показа терминала
        try:
            # Для macOS - скрываем вывод
            if sys.platform == "darwin":
                DEVNULL = subprocess.DEVNULL
                subprocess.Popen(["killall", app_name], 
                                stdout=DEVNULL, stderr=DEVNULL, 
                                start_new_session=True)
            # Для Windows
            elif sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                subprocess.Popen(["taskkill", "/F", "/IM", f"{app_name}.exe"], 
                                startupinfo=startupinfo,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # Для Linux
            elif sys.platform.startswith("linux"):
                subprocess.Popen(["killall", app_name], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, 
                                start_new_session=True)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось закрыть приложение: {str(e)}")
    
    def resource_path(self, relative_path):
        """ Получить абсолютный путь к ресурсу """
        try:
            # PyInstaller создает временную папку и хранит путь в _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = self.current_dir
        
        return os.path.join(base_path, relative_path)

# Создание ярлыка при запуске как самостоятельное приложение
def create_desktop_shortcut():
    try:
        # Путь к рабочему столу пользователя
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        
        # Полный путь к текущему скрипту
        app_path = os.path.abspath(sys.argv[0])
        
        # Для macOS
        if sys.platform == "darwin":
            shortcut_path = os.path.join(desktop_path, "ЛаптопКликер.command")
            with open(shortcut_path, "w") as f:
                f.write(f"#!/bin/bash\ncd \"$(dirname '$0')\"\npython3 \"{app_path}\"\n")
            os.chmod(shortcut_path, 0o755)
            
        # Для Windows
        elif sys.platform == "win32":
            shortcut_path = os.path.join(desktop_path, "ЛаптопКликер.bat")
            with open(shortcut_path, "w") as f:
                f.write(f"@echo off\npython \"{app_path}\"\n")
                
        # Для Linux
        elif sys.platform.startswith("linux"):
            shortcut_path = os.path.join(desktop_path, "ЛаптопКликер.desktop")
            with open(shortcut_path, "w") as f:
                icon_path = os.path.join(os.path.dirname(app_path), "icon.png")
                f.write(f"[Desktop Entry]\nType=Application\nName=ЛаптопКликер\nExec=python3 {app_path}\nIcon={icon_path}\nTerminal=false")
            os.chmod(shortcut_path, 0o755)
            
        print(f"Ярлык создан: {shortcut_path}")
        return True
    except Exception as e:
        print(f"Ошибка при создании ярлыка: {e}")
        return False

if __name__ == "__main__":
    # Создаем главное окно
    root = tk.Tk()
    app = LaptopClicker(root)
    
    # Не создаем ярлык автоматически - это вызывает запрос прав доступа
    # create_desktop_shortcut()
    
    # Запускаем основной цикл
    root.mainloop() 