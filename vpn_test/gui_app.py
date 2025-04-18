#!/usr/bin/env python3
import sys
import os
import platform
import threading
import webbrowser
import subprocess
import time
from tkinter import Tk, Label, Button, Frame, Text, Scrollbar, VERTICAL, RIGHT, Y, LEFT, BOTH, END, PhotoImage, Entry, StringVar, OptionMenu, messagebox
import tkinter.font as tkFont
import tempfile
import base64
import json

# Импортируем наши модули
try:
    from check_ip import check_ip as check_ip_func
except ImportError:
    def check_ip_func():
        return {"ip": "Модуль не найден", "country": "Неизвестно", "city": "Неизвестно", "org": "Неизвестно"}

# Цветовая схема
COLORS = {
    "primary": "#2563eb",           # Более глубокий синий
    "secondary": "#1d4ed8",         # Темно-синий
    "success": "#16a34a",           # Насыщенный зеленый
    "danger": "#dc2626",           # Яркий красный
    "warning": "#d97706",          # Насыщенный оранжевый
    "background": "#f8fafc",       # Светло-серый фон
    "text": "#1e293b",            # Темно-синий текст
    "light_text": "#64748b",      # Серый текст
    "border": "#e2e8f0",          # Цвет границ
    "button_hover": "#3b82f6"     # Цвет при наведении
}

class RedirectText:
    """Класс для перенаправления вывода в текстовое поле"""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.buffer = ""
        
    def write(self, string):
        self.buffer += string
        self.text_widget.config(state="normal")
        self.text_widget.insert(END, string)
        self.text_widget.see(END)
        self.text_widget.config(state="disabled")
        
    def flush(self):
        pass

class SecureNotebookAccessApp:
    """Основной класс приложения"""
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Access • Notebook LM")
        self.root.geometry("900x600")
        self.root.minsize(800, 600)
        self.root.configure(bg=COLORS["background"])
        
        # Устанавливаем шрифт
        self.default_font = tkFont.Font(family="Helvetica", size=10)
        self.title_font = tkFont.Font(family="Helvetica", size=14, weight="bold")
        self.button_font = tkFont.Font(family="Helvetica", size=11)
        
        # Инициализация пользовательского интерфейса
        self.setup_ui()
        
        # Показываем правовую информацию при старте
        self.root.after(500, self.show_legal_info)
    
    def setup_ui(self):
        """Настройка интерфейса"""
        # Создаем верхнюю панель с градиентом
        self.header_frame = Frame(self.root, bg=COLORS["primary"], height=70)
        self.header_frame.pack(fill="x")
        
        # Заголовок с увеличенным размером
        Label(self.header_frame, text="Secure Access • Notebook LM", 
              font=("Helvetica", 18, "bold"), 
              bg=COLORS["primary"], fg="white").pack(side=LEFT, padx=25, pady=15)
        
        # Индикатор статуса VPN с улучшенным стилем
        self.vpn_status_var = StringVar(value="VPN статус: Неизвестно")
        self.vpn_status_label = Label(self.header_frame, textvariable=self.vpn_status_var, 
                                      font=("Helvetica", 12), bg=COLORS["primary"], fg="white")
        self.vpn_status_label.pack(side=RIGHT, padx=25, pady=15)
        
        # Основной контейнер с увеличенными отступами
        self.main_container = Frame(self.root, bg=COLORS["background"])
        self.main_container.pack(fill=BOTH, expand=True, padx=30, pady=25)
        
        # Левая панель с кнопками
        self.sidebar = Frame(self.main_container, bg=COLORS["background"], width=250)
        self.sidebar.pack(side=LEFT, fill="y", padx=(0, 25))
        
        # Кнопки действий с улучшенным стилем
        button_style = {
            "font": ("Helvetica", 12),
            "width": 25,
            "height": 2,
            "relief": "flat",
            "cursor": "hand2"  # Курсор-рука при наведении
        }
        
        self.create_button("Проверить IP", self.check_ip, COLORS["primary"], **button_style)
        self.create_button("Тест WebRTC", self.webrtc_test, COLORS["primary"], **button_style)
        self.create_button("Настройка Яндекс.Браузера", self.yandex_browser_settings, COLORS["primary"], **button_style)
        self.create_button("Открыть Notebook LM", self.open_notebook_lm, COLORS["success"], **button_style)
        self.create_button("Приватность", self.privacy_tools, COLORS["primary"], **button_style)
        self.create_button("Правовая информация", self.show_legal_info, COLORS["warning"], **button_style)
        
        # Панель вывода с тенью
        self.output_frame = Frame(self.main_container, bg="white", bd=0)
        self.output_frame.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Заголовок панели вывода
        self.output_header = Frame(self.output_frame, bg=COLORS["secondary"], height=40)
        self.output_header.pack(fill="x")
        
        self.output_title = Label(self.output_header, text="Доступ к Notebook LM", 
                                 font=("Helvetica", 14), bg=COLORS["secondary"], fg="white")
        self.output_title.pack(side=LEFT, padx=15, pady=8)
        
        # Область вывода с улучшенным стилем
        self.output_container = Frame(self.output_frame, bg="white")
        self.output_container.pack(fill=BOTH, expand=True)
        
        self.output_text = Text(self.output_container, wrap="word", bg="white", fg=COLORS["text"],
                               font=("Consolas", 11), padx=15, pady=15)
        self.output_text.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Стилизованный скроллбар
        self.scrollbar = Scrollbar(self.output_container, orient=VERTICAL, command=self.output_text.yview,
                                  width=12)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        
        self.output_text.config(yscrollcommand=self.scrollbar.set, state="disabled")
        
        # Перенаправляем стандартный вывод в текстовое поле
        self.redirect = RedirectText(self.output_text)
        sys.stdout = self.redirect
        
        # Нижняя панель с информацией
        self.footer = Frame(self.root, bg=COLORS["text"], height=35)
        self.footer.pack(fill="x", side="bottom")
        
        Label(self.footer, text="© 2023 Secure Access. Для личного использования.", 
              font=("Helvetica", 9), bg=COLORS["text"], fg="white").pack(pady=8)
        
        # Статус IP
        threading.Thread(target=self.update_vpn_status, daemon=True).start()
    
    def create_button(self, text, command, color, **kwargs):
        """Создает современную кнопку с эффектом при наведении"""
        frame = Frame(self.sidebar, bg=COLORS["background"])
        frame.pack(pady=6, fill="x")
        
        btn = Button(frame, text=text, bg=color, fg="white",
                    activebackground=COLORS["button_hover"], 
                    activeforeground="white", command=command, **kwargs)
        btn.pack(fill="x")
        
        # Добавляем эффект при наведении
        def on_enter(e):
            btn['background'] = COLORS["button_hover"]
        
        def on_leave(e):
            btn['background'] = color
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
    
    def clear_output(self):
        """Очищает область вывода"""
        self.output_text.config(state="normal")
        self.output_text.delete(1.0, END)
        self.output_text.config(state="disabled")
    
    def update_output_title(self, title):
        """Обновляет заголовок панели вывода"""
        self.output_title.config(text=title)
    
    def check_ip(self):
        """Проверяет IP адрес"""
        self.clear_output()
        self.update_output_title("Проверка IP-адреса")
        
        print("=== Проверка IP-адреса и местоположения ===\n")
        print("Выполняем запросы к серверам проверки IP...")
        
        # Запускаем проверку в отдельном потоке
        threading.Thread(target=self._run_ip_check, daemon=True).start()
    
    def _run_ip_check(self):
        """Запускает проверку IP в отдельном потоке"""
        try:
            # Используем нашу функцию check_ip из check_ip.py
            result = check_ip_func()
            
            # Этот код выполняется, если всё прошло успешно
            self.update_vpn_status()
        except Exception as e:
            print(f"\nОшибка при проверке IP: {e}")
            print("\nПроверьте подключение к интернету и попробуйте снова.")
    
    def update_vpn_status(self):
        """Обновляет статус VPN в верхней панели"""
        try:
            import requests
            response = requests.get("https://ipinfo.io/json", timeout=5, verify=True).json()
            
            country = response.get("country", "Unknown")
            ip = response.get("ip", "Unknown")
            
            if country == "RU":
                self.vpn_status_var.set(f"VPN: Выключен ({country} • {ip})")
                self.vpn_status_label.config(fg="#e74c3c")  # Красный цвет
            else:
                self.vpn_status_var.set(f"VPN: Активен ({country} • {ip})")
                self.vpn_status_label.config(fg="#2ecc71")  # Зеленый цвет
        except:
            self.vpn_status_var.set("VPN статус: Ошибка проверки")
            self.vpn_status_label.config(fg="#f39c12")  # Желтый цвет
    
    def webrtc_test(self):
        """Запускает тест WebRTC утечек"""
        self.clear_output()
        self.update_output_title("Проверка WebRTC утечек")
        
        print("=== Проверка WebRTC утечек ===\n")
        print("WebRTC может раскрыть ваш реальный IP-адрес, даже если вы используете VPN.")
        print("Сейчас мы проверим наличие таких утечек в вашем браузере.\n")
        
        print("ПРЕДУПРЕЖДЕНИЕ: Будут открыты внешние сайты для проверки. Не вводите на них личные данные.")
        print("После проверки ЗАКРОЙТЕ эти сайты для вашей безопасности!\n")
        
        choice = messagebox.askyesno("Подтверждение", 
                                      "Сейчас будут открыты внешние сайты для проверки утечек WebRTC. Продолжить?")
        if not choice:
            print("Операция отменена пользователем.")
            return
        
        print("Открываем сайты для проверки...\n")
        
        # Открываем сайты для проверки в браузере по умолчанию
        webbrowser.open("https://browserleaks.com/webrtc")
        time.sleep(1)
        
        print("\nПроверьте, показывает ли сайт ваш реальный IP-адрес.")
        print("Если показывает - у вас есть утечка WebRTC, и вам нужно настроить браузер.")
        
        print("\nВоспользуйтесь кнопкой 'Настройка Яндекс.Браузера' для получения инструкций по устранению утечек.")
    
    def yandex_browser_settings(self):
        """Показывает инструкции по настройке Яндекс.Браузера"""
        self.clear_output()
        self.update_output_title("Настройка Яндекс.Браузера")
        
        print("=== Настройка Яндекс.Браузера для работы с VPN ===\n")
        print("Яндекс.Браузер может раскрывать ваш реальный IP-адрес через WebRTC и другие механизмы.\n")
        
        print("Для решения этой проблемы выполните следующие шаги:\n")
        print("1. Откройте about:config в адресной строке Яндекс.Браузера")
        print("2. Найдите и отключите следующие настройки:")
        print("   - media.peerconnection.enabled → false (отключает WebRTC)")
        print("   - privacy.resistFingerprinting → true (повышает приватность)\n")
        
        print("3. Установите расширения:")
        print("   - WebRTC Control - блокирует утечки WebRTC")
        print("   - Location Guard - защищает вашу геолокацию\n")
        
        print("ВАЖНО: После внесения изменений перезапустите браузер.\n")
        
        choice = messagebox.askyesno("Открыть расширения", 
                                     "Открыть страницу с расширениями для Яндекс.Браузера?")
        if choice:
            webbrowser.open("https://browser.yandex.ru/extensions/")
            print("Открыта страница расширений. Установите рекомендуемые расширения.")
    
    def open_notebook_lm(self):
        """Открывает Notebook LM в браузере"""
        self.clear_output()
        self.update_output_title("Доступ к Notebook LM")
        
        print("=== Открытие Notebook LM ===\n")
        
        # Проверяем статус VPN
        self.update_vpn_status()
        
        print("ВАЖНО: Перед открытием убедитесь, что:\n")
        print("1. Ваш VPN включен и работает (проверьте индикатор в верхней панели)")
        print("2. В браузере отключены утечки WebRTC")
        print("3. Вы используете режим инкогнито\n")
        
        choice = messagebox.askyesno("Подтверждение", 
                                     "Вы хотите открыть Notebook LM сейчас? Убедитесь, что VPN активен.")
        if not choice:
            print("Операция отменена пользователем.")
            return
        
        print("Открываем Notebook LM...\n")
        webbrowser.open("https://notebooklm.google.com/")
        
        print("Страница Notebook LM должна открыться в вашем браузере.")
        print("Если вы видите сообщение о недоступности сервиса в вашем регионе:")
        print("1. Проверьте, что VPN действительно работает (статус в верхней панели)")
        print("2. Убедитесь, что в браузере отключены утечки WebRTC")
        print("3. Попробуйте использовать другой браузер (Firefox или Brave)")
    
    def privacy_tools(self):
        """Показывает инструменты для повышения приватности"""
        self.clear_output()
        self.update_output_title("Инструменты приватности")
        
        print("=== Инструменты повышения приватности ===\n")
        print("Для максимальной защиты рекомендуется использовать следующие методы:\n")
        
        print("1. Использование режима инкогнито")
        print("   - В Яндекс.Браузере: Ctrl+Shift+N (или Cmd+Shift+N на macOS)")
        print("   - В Firefox: Ctrl+Shift+P (или Cmd+Shift+P на macOS)\n")
        
        print("2. Смена User-Agent (идентификатора браузера)")
        print("   - Установите расширение User-Agent Switcher")
        print("   - Выберите User-Agent, отличный от вашего обычного браузера\n")
        
        print("3. Блокировка cookies и трекеров")
        print("   - Установите расширение Privacy Badger")
        print("   - Используйте uBlock Origin для блокировки рекламы и трекеров\n")
        
        print("4. Защита от цифрового отпечатка браузера")
        print("   - В Firefox включите настройку privacy.resistFingerprinting")
        print("   - В Brave используйте встроенную защиту от отпечатков\n")
        
        print("5. Защита от DNS-утечек")
        print("   - Используйте DNS-серверы, которые не хранят логи (1.1.1.1 или 9.9.9.9)")
        print("   - Убедитесь, что ваш VPN-провайдер защищает DNS-запросы\n")
        
        choice = messagebox.askyesno("Проверка безопасности", 
                                    "Хотите проверить защиту от цифрового отпечатка вашего браузера?")
        if choice:
            webbrowser.open("https://coveryourtracks.eff.org/")
            print("Открыт сайт для проверки цифрового отпечатка браузера.")
    
    def show_legal_info(self):
        """Показывает правовую информацию"""
        self.clear_output()
        self.update_output_title("Правовая информация")
        
        print("=== Правовая информация ===\n")
        print("В Российской Федерации использование VPN регулируется законодательством.\n")
        
        print("Согласно российскому законодательству:")
        print("1. Использование VPN для личных целей НЕ запрещено")
        print("2. Закон №276-ФЗ запрещает использование VPN для доступа к запрещенным ресурсам")
        print("3. Сервис Notebook LM НЕ входит в список запрещенных ресурсов Роскомнадзора\n")
        
        print("Использование нашей утилиты для личных целей (например, для доступа к")
        print("Notebook LM с целью образования или работы) не противоречит законодательству.\n")
        
        print("Однако, обратите внимание, что:")
        print("1. Вы используете данную утилиту на свой страх и риск")
        print("2. Авторы программы не несут ответственности за неправомерное использование")
        print("3. Всегда следите за изменениями в законодательстве\n")
        
        # Показываем диалоговое окно для подтверждения
        choice = messagebox.askyesno("Правовая информация", 
                                    "Я понимаю и принимаю эту информацию?")
        if not choice:
            print("Для использования приложения необходимо принять эту информацию.")
            self.root.after(2000, self.root.destroy)
        else:
            print("Информация принята. Приложение готово к использованию.")

def main():
    """Точка входа в приложение"""
    root = Tk()
    app = SecureNotebookAccessApp(root)
    
    # Устанавливаем иконку приложения (закодированную в base64)
    try:
        # Тут будет закодированная иконка
        icon_data = ""  # В реальности тут будет длинная base64 строка
        
        if icon_data:
            # Декодируем иконку
            icon_data_decoded = base64.b64decode(icon_data)
            
            # Сохраняем во временный файл
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as icon_file:
                icon_file.write(icon_data_decoded)
                icon_path = icon_file.name
            
            icon = PhotoImage(file=icon_path)
            root.iconphoto(True, icon)
            
            # Удаляем временный файл
            os.remove(icon_path)
    except:
        # Если что-то пошло не так, просто игнорируем ошибку иконки
        pass
    
    root.mainloop()

if __name__ == "__main__":
    main() 