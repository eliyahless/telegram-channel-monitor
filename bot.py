import os
import logging
import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from dotenv import load_dotenv
from db_manager import DatabaseManager

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Получение токена бота
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Инициализация менеджера базы данных
db = DatabaseManager()

# Определение состояний для FSM (конечного автомата)
class Form(StatesGroup):
    city = State()  # Состояние выбора города
    add_channel = State()  # Состояние добавления канала
    add_keyword = State()  # Состояние добавления ключевого слова
    add_city = State()  # Состояние добавления города
    delete_channel = State()  # Состояние удаления канала
    delete_keyword = State()  # Состояние удаления ключевого слова
    search = State()  # Состояние поиска

# Функция для создания главной клавиатуры
def get_main_keyboard(user_id=None):
    is_admin = False
    if user_id:
        user = db.get_user(user_id)
        is_admin = user and user['is_admin'] == 1
    
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('🌆 Выбрать город'))
    keyboard.add(KeyboardButton('📊 Статистика'))
    
    if is_admin:
        keyboard.add(KeyboardButton('➕ Добавить канал'))
        keyboard.add(KeyboardButton('➕ Добавить ключевое слово'))
        keyboard.add(KeyboardButton('➕ Добавить город'))
        keyboard.add(KeyboardButton('❌ Удалить канал'))
        keyboard.add(KeyboardButton('❌ Удалить ключевое слово'))
    
    keyboard.add(KeyboardButton('🔍 Поиск'))
    return keyboard

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if not user:
        db.add_user(user_id)
        user = db.get_user(user_id)
    
    await message.answer(
        f"Привет, {message.from_user.first_name}! Я бот для отслеживания скидок и акций из Telegram-каналов.",
        reply_markup=get_main_keyboard(user_id)
    )

# Обработчик команды /admin для назначения администратором
@dp.message_handler(commands=['admin'])
async def cmd_admin(message: types.Message):
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')  # Пароль для админки
    command_parts = message.text.split()
    
    if len(command_parts) != 2 or command_parts[1] != admin_password:
        await message.answer("Неверный пароль!")
        return
    
    user_id = message.from_user.id
    db.set_admin_status(user_id, 1)
    
    await message.answer(
        "Вы успешно назначены администратором.",
        reply_markup=get_main_keyboard(user_id)
    )

# Обработчик для выбора города
@dp.message_handler(Text(equals='🌆 Выбрать город'))
async def choose_city(message: types.Message):
    cities = db.get_all_cities()
    
    if not cities:
        await message.answer("В базе данных нет городов. Попросите администратора добавить города.")
        return
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    for city in cities:
        keyboard.add(InlineKeyboardButton(city['name'], callback_data=f"city_{city['id']}"))
    
    await message.answer("Выберите ваш город:", reply_markup=keyboard)
    await Form.city.set()

# Обработчик для нажатия на кнопку выбора города
@dp.callback_query_handler(lambda c: c.data.startswith('city_'), state=Form.city)
async def process_city_choice(callback_query: types.CallbackQuery, state: FSMContext):
    city_id = int(callback_query.data.split('_')[1])
    user_id = callback_query.from_user.id
    
    db.update_user_city(user_id, city_id)
    
    city = next((c for c in db.get_all_cities() if c['id'] == city_id), None)
    city_name = city['name'] if city else 'Неизвестный город'
    
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(
        user_id,
        f"Вы выбрали город: {city_name}. Теперь вы будете получать скидки и акции из этого города."
    )
    
    await state.finish()

# Обработчик для показа статистики
@dp.message_handler(Text(equals='📊 Статистика'))
async def show_stats(message: types.Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if not user or not user['city_id']:
        await message.answer("Сначала выберите город.")
        return
    
    channels = db.get_channels_by_city(user['city_id'])
    keywords = db.get_all_keywords()
    
    stats_text = f"📊 Статистика для города {user['city_name']}:\n\n"
    stats_text += f"📢 Каналы ({len(channels)}):\n"
    
    for i, channel in enumerate(channels[:10], 1):  # Ограничиваем до 10 каналов
        stats_text += f"{i}. {channel['channel_name']} (@{channel['channel_username']})\n"
    
    if len(channels) > 10:
        stats_text += f"... и еще {len(channels) - 10} каналов\n"
    
    stats_text += f"\n🔎 Ключевые слова ({len(keywords)}):\n"
    keywords_str = ", ".join([k['word'] for k in keywords[:20]])  # Ограничиваем до 20 слов
    
    if len(keywords) > 20:
        stats_text += f"{keywords_str}... и еще {len(keywords) - 20} слов"
    else:
        stats_text += keywords_str
    
    await message.answer(stats_text)

# Обработчики для добавления канала (только для админов)
@dp.message_handler(Text(equals='➕ Добавить канал'))
async def add_channel_start(message: types.Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if not user or user['is_admin'] != 1:
        await message.answer("У вас нет прав для этой операции.")
        return
    
    await message.answer(
        "Укажите ссылку на канал, его имя и город в формате:\n"
        "<ID канала> | <Имя канала> | <Username канала> | <ID города>\n\n"
        "Например: -1001234567890 | Скидки Москва | moscow_sales | 1"
    )
    
    await Form.add_channel.set()

@dp.message_handler(state=Form.add_channel)
async def add_channel_process(message: types.Message, state: FSMContext):
    try:
        parts = message.text.split('|')
        if len(parts) != 4:
            await message.answer("Неверный формат. Попробуйте еще раз.")
            return
        
        channel_id = parts[0].strip()
        channel_name = parts[1].strip()
        channel_username = parts[2].strip()
        city_id = int(parts[3].strip())
        
        result = db.add_channel(channel_id, channel_name, channel_username, city_id)
        
        if result:
            await message.answer(f"Канал {channel_name} успешно добавлен.")
        else:
            await message.answer("Ошибка при добавлении канала. Возможно, он уже существует.")
    
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")
    
    await state.finish()

# Обработчики для добавления ключевого слова (только для админов)
@dp.message_handler(Text(equals='➕ Добавить ключевое слово'))
async def add_keyword_start(message: types.Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if not user or user['is_admin'] != 1:
        await message.answer("У вас нет прав для этой операции.")
        return
    
    await message.answer("Введите ключевое слово для фильтрации сообщений:")
    await Form.add_keyword.set()

@dp.message_handler(state=Form.add_keyword)
async def add_keyword_process(message: types.Message, state: FSMContext):
    keyword = message.text.strip().lower()
    
    if not keyword:
        await message.answer("Ключевое слово не может быть пустым.")
        return
    
    result = db.add_keyword(keyword)
    
    if result:
        await message.answer(f"Ключевое слово '{keyword}' успешно добавлено.")
    else:
        await message.answer("Ошибка при добавлении ключевого слова. Возможно, оно уже существует.")
    
    await state.finish()

# Обработчики для добавления города (только для админов)
@dp.message_handler(Text(equals='➕ Добавить город'))
async def add_city_start(message: types.Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if not user or user['is_admin'] != 1:
        await message.answer("У вас нет прав для этой операции.")
        return
    
    await message.answer("Введите название города:")
    await Form.add_city.set()

@dp.message_handler(state=Form.add_city)
async def add_city_process(message: types.Message, state: FSMContext):
    city_name = message.text.strip()
    
    if not city_name:
        await message.answer("Название города не может быть пустым.")
        return
    
    result = db.add_city(city_name)
    
    if result:
        await message.answer(f"Город '{city_name}' успешно добавлен.")
    else:
        await message.answer("Ошибка при добавлении города. Возможно, он уже существует.")
    
    await state.finish()

# Обработчики для удаления канала (только для админов)
@dp.message_handler(Text(equals='❌ Удалить канал'))
async def delete_channel_start(message: types.Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if not user or user['is_admin'] != 1:
        await message.answer("У вас нет прав для этой операции.")
        return
    
    channels = db.get_channels_by_city()
    
    if not channels:
        await message.answer("В базе данных нет каналов.")
        return
    
    keyboard = InlineKeyboardMarkup(row_width=1)
    for channel in channels:
        keyboard.add(InlineKeyboardButton(
            f"{channel['channel_name']} (@{channel['channel_username']})",
            callback_data=f"del_channel_{channel['channel_id']}"
        ))
    
    await message.answer("Выберите канал для удаления:", reply_markup=keyboard)
    await Form.delete_channel.set()

@dp.callback_query_handler(lambda c: c.data.startswith('del_channel_'), state=Form.delete_channel)
async def delete_channel_process(callback_query: types.CallbackQuery, state: FSMContext):
    channel_id = callback_query.data.split('_')[2]
    
    db.delete_channel(channel_id)
    
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(
        callback_query.from_user.id,
        f"Канал успешно удален."
    )
    
    await state.finish()

# Обработчики для удаления ключевого слова (только для админов)
@dp.message_handler(Text(equals='❌ Удалить ключевое слово'))
async def delete_keyword_start(message: types.Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if not user or user['is_admin'] != 1:
        await message.answer("У вас нет прав для этой операции.")
        return
    
    keywords = db.get_all_keywords(active_only=False)
    
    if not keywords:
        await message.answer("В базе данных нет ключевых слов.")
        return
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    for keyword in keywords:
        keyboard.add(InlineKeyboardButton(
            keyword['word'],
            callback_data=f"del_keyword_{keyword['id']}"
        ))
    
    await message.answer("Выберите ключевое слово для удаления:", reply_markup=keyboard)
    await Form.delete_keyword.set()

@dp.callback_query_handler(lambda c: c.data.startswith('del_keyword_'), state=Form.delete_keyword)
async def delete_keyword_process(callback_query: types.CallbackQuery, state: FSMContext):
    keyword_id = int(callback_query.data.split('_')[2])
    
    db.delete_keyword(keyword_id)
    
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(
        callback_query.from_user.id,
        f"Ключевое слово успешно удалено."
    )
    
    await state.finish()

# Обработчики для поиска
@dp.message_handler(Text(equals='🔍 Поиск'))
async def search_start(message: types.Message):
    await message.answer("Введите запрос для поиска:")
    await Form.search.set()

@dp.message_handler(state=Form.search)
async def search_process(message: types.Message, state: FSMContext):
    # В простой версии поиска пока не реализован, но место для его расширения есть
    await message.answer("Функция поиска пока находится в разработке.")
    await state.finish()

# Обработчик для неизвестных сообщений
@dp.message_handler()
async def unknown_message(message: types.Message):
    await message.answer("Не понимаю эту команду. Используйте меню для взаимодействия.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True) 