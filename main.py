from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import psutil
import platform
import subprocess
from ping3 import ping
import os
from aiogram.types import InputFile
import zipfile
import logging
import io

API_TOKEN = 'ТОКЕН' #ВАШ ТОКЕН ИЗ @BOTFATHER
OWNER_ID = АЙДИ #ВАШ ТЕЛЕГРАМ АЙДИ

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


management_markup = InlineKeyboardMarkup(row_width=2)
management_markup.row(
    InlineKeyboardButton('Узнать IP 🌐', callback_data='get_ip'),
    InlineKeyboardButton('Пинг 📉', callback_data='ping')
)
management_markup.row(
    InlineKeyboardButton('Очистка кеша 🗑', callback_data='clear_cache'), 
    InlineKeyboardButton('Пользователи 👥', callback_data='list_users')
)   
management_markup.row(
    InlineKeyboardButton('Бекап 💾', callback_data='start_backup'),
    InlineKeyboardButton('Статус ⏳', callback_data='server_status')
)
management_markup.row(
    InlineKeyboardButton('❌ Отмена', callback_data='cancel_action')
)


main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.row(KeyboardButton('Статистика 📊'), KeyboardButton('Управление ⚙️'))
main_menu.row(KeyboardButton('Выполнить команду 🕹'))
main_menu.row(KeyboardButton('Логи 📋'), KeyboardButton('Помощь 📚'))


confirm_markup = InlineKeyboardMarkup(row_width=2)
confirm_markup.row(
    InlineKeyboardButton('Да ✅', callback_data='confirm_command')
)
confirm_markup.row(
    InlineKeyboardButton('Отмена ❌', callback_data='cancel_command')
)


logs_menu = InlineKeyboardMarkup(row_width=2)
logs_menu.add(
    InlineKeyboardButton('Auth 🔐', callback_data='logs_auth'),
    InlineKeyboardButton('Python 🐍', callback_data='logs_python'),
    InlineKeyboardButton('Nginx 🌐', callback_data='logs_nginx'),
    InlineKeyboardButton('Apache 🌍', callback_data='logs_apache'),
    InlineKeyboardButton('Squid 🦑', callback_data='logs_squid'),
    InlineKeyboardButton('Dante 🎭', callback_data='logs_dante'),
    InlineKeyboardButton('Отмена ❌', callback_data='cancel_action')
)


user_states = {}

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    if message.from_user.id == OWNER_ID:
        await message.answer("<b>👋 Добро пожаловать!</b>", reply_markup=main_menu, parse_mode='HTML')
    else:
        await message.answer("<b>⛔️ У вас нет доступа.</b>", parse_mode='HTML')

@dp.message_handler(lambda message: message.text == 'Статистика 📊')
async def send_statistics(message: types.Message):
    if message.from_user.id == OWNER_ID:
        
        system_info = platform.uname()
        cpu_usage = psutil.cpu_percent(interval=0.1)  
        cpu_count = psutil.cpu_count()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        uptime_seconds = psutil.boot_time()
        uptime_hours = int((psutil.time.time() - uptime_seconds) // 3600)

        
        try:
            ping_result = ping('google.com')
            ping_time = f"{round(ping_result * 1000)} мс" if ping_result else "Не удалось измерить пинг"
        except Exception:
            ping_time = "Не удалось измерить пинг"

        
        statistics = (
            f"<b>🖥 Система:</b> {system_info.system} {system_info.release}\n"
            f"<b>📝 Версия:</b> {system_info.version}\n"
            f"<b>💻 Процессор:</b> {cpu_count} ядер, загрузка {cpu_usage}%\n"
            f"<b>🕰 Время работы:</b> {uptime_hours} часов\n"
            f"<b>💾 RAM:</b> {memory.available // (1024 ** 2)} MB из {memory.total // (1024 ** 2)} MB\n"
            f"<b>💽 SSD:</b> {disk.free // (1024 ** 3)} GB из {disk.total // (1024 ** 3)} GB\n"
            f"<b>📶 Пинг:</b> {ping_time}\n"
        )
        await message.answer(statistics, parse_mode='HTML')
    else:
        await message.answer("<b>⛔️ У вас нет доступа.</b>", parse_mode='HTML')




@dp.message_handler(lambda message: message.text == 'Управление ⚙️')
async def show_management_options(message: types.Message):
    if message.from_user.id == OWNER_ID:
        await message.answer("<b>⚙️ Выберите что будем делать:</b>", parse_mode='HTML', reply_markup=management_markup)
    else:
        await message.answer("<b>⛔️ У вас нет доступа.</b>", parse_mode='HTML')

@dp.callback_query_handler(lambda c: c.data in ['get_ip', 'ping', 'list_users', 'clear_cache', 'start_backup', 'server_status', 'cancel_action'])
async def handle_management_action(callback_query: types.CallbackQuery):
    action = callback_query.data
    chat_id = callback_query.message.chat.id

    if action == 'cancel_action':
        await bot.delete_message(chat_id=chat_id, message_id=callback_query.message.message_id)
        await bot.send_message(chat_id=chat_id, text="<b>❌ Действие отменено.</b>", parse_mode='HTML')
        return

    await bot.delete_message(chat_id=chat_id, message_id=callback_query.message.message_id)

    if action == 'get_ip':
        ip_info = subprocess.run("hostname -I", shell=True, capture_output=True, text=True).stdout.strip()
        await bot.send_message(chat_id=chat_id, text=f"<b>🌐 IP адрес:</b> {ip_info}", parse_mode='HTML')
    elif action == 'ping':
        ping_result = ping('google.com')
        ping_time = f"{round(ping_result * 1000)} мс" if ping_result else "Не удалось измерить пинг"
        await bot.send_message(chat_id=chat_id, text=f"<b>📉 Пинг до google.com:</b> {ping_time}", parse_mode='HTML')
    elif action == 'clear_cache':
        cache_clear = subprocess.run("sudo apt clean", shell=True, capture_output=True, text=True).stdout.strip()
        await bot.send_message(chat_id=chat_id, text=f"<b>🗑 Кеш очищен:</b> {cache_clear}", parse_mode='HTML')
    elif action == 'list_users':
        users_list = subprocess.run("cut -d: -f1 /etc/passwd", shell=True, capture_output=True, text=True).stdout.strip()
        await bot.send_message(chat_id=chat_id, text=f"<b>👥 Список пользователей:</b>\n<pre>{users_list}</pre>", parse_mode='HTML')
    elif action == 'start_backup':
        backup_path = '/root_backup.tar.gz'
        try:
            subprocess.run(f'tar -czvf {backup_path} /root', shell=True, check=True)
            with open(backup_path, 'rb') as backup_file:
                await bot.send_document(chat_id=callback_query.message.chat.id, document=backup_file, caption="<b>📦 Бэкап директории /root:</b>", parse_mode='HTML')
            
            subprocess.run(f'rm {backup_path}', shell=True, check=True)
        except Exception as e:
            await callback_query.message.answer(f"<b>❌ Ошибка при создании бэкапа:</b> {e}", parse_mode='HTML')
    elif action == 'server_status':
        server_status = subprocess.run("uptime", shell=True, capture_output=True, text=True).stdout.strip()
        await bot.send_message(chat_id=chat_id, text=f"<b>⏳ Статус сервера:</b>\n<pre>{server_status}</pre>", parse_mode='HTML')

@dp.message_handler(lambda message: message.text == 'Логи 📋')
async def show_logs(message: types.Message):
    if message.from_user.id == OWNER_ID:
        
        await message.answer("<b>📚 Выберите что будем смотреть:</b>", reply_markup=logs_menu, parse_mode='HTML')
    else:
        await message.answer("<b>⛔️ У вас нет доступа.</b>", parse_mode='HTML')


@dp.callback_query_handler(lambda c: c.data.startswith('logs_'))
async def handle_logs(callback_query: types.CallbackQuery):
    log_type = callback_query.data[len('logs_'):]

    
    LOG_FILES = {
        'nginx': '/var/log/nginx/access.log',
        'apache': '/var/log/apache2/access.log',
        'auth': '/var/log/auth.log',
        'python': '/var/log/python.log',
        'squid': '/var/log/squid/access.log',
        'dante': '/var/log/dante.log'
    }

    log_file_path = LOG_FILES.get(log_type)

    
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)

    if log_file_path and os.path.exists(log_file_path):
        try:
            
            zip_buffer = io.BytesIO()


            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.write(log_file_path, os.path.basename(log_file_path))

            
            zip_buffer.seek(0)


            zip_file_input = InputFile(zip_buffer, filename=f"{log_type}_logs.zip")

            
            await bot.send_document(
                chat_id=callback_query.message.chat.id,
                document=zip_file_input,
                caption=f"<b>📄 Логи:</b> {log_type}",
                parse_mode='HTML'
            )
        except Exception as e:
            
            await callback_query.message.answer("<b>❌ Ошибка при отправке логов.</b>", parse_mode='HTML')
    else:
        await callback_query.message.answer("<b>❌ Лог файл не найден.</b>", parse_mode='HTML')


@dp.message_handler(lambda message: message.text == 'Помощь 📚')
async def show_help(message: types.Message):
    if message.from_user.id == OWNER_ID:
        help_text = (
            "<b>📚 Информация о командах:</b>\n\n"
            "<b>📊 Статистика</b> - Показывает текущее состояние системы: загрузка процессора, использование памяти, пинг и информация о сетевых интерфейсах.\n\n"
            "<b>⚙️ Управление</b> - Позволяет выполнять различные системные действия, такие как очистка кеша, проверка пинга, получение IP-адреса и создание резервных копий.\n\n"
            "<b>📋 Логи</b> - Позволяет выбрать и просмотреть логи различных сервисов, таких как Auth, Python, Nginx, Apache, Squid и Dante.\n\n"
            "<b>🕹 Выполнить команду</b> - Отправляет команду на выполнение в терминале и возвращает результат.\n\n"
            "<b>📚 Помощь</b> - Показывает это сообщение с описанием доступных команд."
        )
        
        await message.answer(help_text, parse_mode='HTML')
    else:
        await message.answer("<b>⛔️ Доступ запрещен.</b>", parse_mode='HTML')

@dp.callback_query_handler(lambda c: c.data == 'close_help')
async def close_help(callback_query: types.CallbackQuery):
    
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)

@dp.message_handler(lambda message: message.text == 'Выполнить команду 🕹')
async def ask_command(message: types.Message):
    if message.from_user.id == OWNER_ID:

        user_states[message.from_user.id] = 'waiting_for_command'
        await message.answer("<b>🕹 Пожалуйста, отправьте команду для выполнения.</b>", parse_mode='HTML')
    else:
        await message.answer("<b>⛔️ У вас нет доступа.</b>", parse_mode='HTML')

@dp.message_handler(lambda message: message.text and message.from_user.id in user_states and user_states[message.from_user.id] == 'waiting_for_command')
async def handle_command(message: types.Message):
    command = message.text
    user_states[message.from_user.id] = command  
    await message.answer(
        f"<b>🕹 Выполняем команду:</b>\n<pre>{command}</pre>",
        parse_mode='HTML',
        reply_markup=confirm_markup
    )

@dp.callback_query_handler(lambda c: c.data in ['confirm_command', 'cancel_command'])
async def process_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    command = user_states.get(user_id, None)

    if callback_query.data == 'confirm_command' and command:
        
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
        try:
            
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                output = result.stdout.strip() or "Команда выполнена без вывода."
                await callback_query.message.answer(f"<b>✅ Вывод:</b>\n<pre>{output}</pre>", parse_mode='HTML')
            else:
                error = result.stderr.strip() or "Неизвестная ошибка."
                await callback_query.message.answer(f"<b>❌ Ошибка:</b>\n<pre>{error}</pre>", parse_mode='HTML')
        except Exception as e:
            await callback_query.message.answer(f"<b>❌ Ошибка при выполнении команды:</b> {e}", parse_mode='HTML')
    elif callback_query.data == 'cancel_command':
        
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
        
        await callback_query.message.answer("<b>❌ Действие отменено.</b>", parse_mode='HTML')
    

    user_states[user_id] = None



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)