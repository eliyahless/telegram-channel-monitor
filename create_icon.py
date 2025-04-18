from PIL import Image, ImageDraw, ImageFont
import os

def create_laptop_icon():
    # Создаем изображение 128x128 пикселей с прозрачным фоном
    icon = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    # Рисуем простой ноутбук
    # Экран
    draw.rounded_rectangle([(24, 20), (104, 80)], radius=5, fill=(30, 144, 255), outline=(20, 20, 20), width=2)
    # Клавиатура
    draw.rounded_rectangle([(20, 80), (108, 100)], radius=3, fill=(60, 60, 60), outline=(20, 20, 20), width=2)
    
    # Рисуем кнопку
    draw.ellipse([(54, 85), (74, 95)], fill=(255, 50, 50), outline=(20, 20, 20), width=1)
    
    # Добавляем текст "LM" на экране
    try:
        # Пытаемся использовать встроенный шрифт
        font = ImageFont.truetype("Arial", 24)
    except:
        # Если не получилось, используем стандартный
        font = ImageFont.load_default()
    
    draw.text((64, 45), "LM", fill=(255, 255, 255), font=font, anchor="mm")
    
    # Сохраняем изображение
    icon.save('icon.png')
    print(f"Иконка создана в {os.path.abspath('icon.png')}")

if __name__ == "__main__":
    create_laptop_icon() 