# Link to the bot: https://t.me/innopolis_testing_bot
import sys
import locale
import re


from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram.dispatcher import filters
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext   
from aiogram.utils import executor
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from aiogram.dispatcher.filters import CommandStart, Command
from aiogram.contrib.fsm_storage.memory import MemoryStorage


# Импортируем функции из файла с базой данных
from database import insert_user_db, delete_user_db, update_user_db, get_nickname_db


TOKEN = "6273983990:AAGNUQpjEen2GKcfJYtcHygvolZkzxg8Fpk"
bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


async def set_default_commands(bot: Bot):
    commands = [
        BotCommand('start', 'Команда запуска бота'),
        BotCommand('get', 'Получение информации о себе из базы данных'),
        BotCommand('update', 'Обновление информации о себе в базе данных'),
        BotCommand('write', 'Записать информацию о себе в базу данных'),
        BotCommand('delete', 'Удалить информацию о себе из базы данных')
    ]
    return await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())
                                     

@dp.message_handler(commands=["start"])
async def send_welcome(msg: types.Message):
    await msg.reply(f"Я бот. Меня написал Марк Клавишин. Я работаю круглосуточно, так как установлен на VDS хостинге.")
    await set_default_commands(bot)

@dp.message_handler(commands=["write"])
async def record_user(msg: types.Message):
    # Получаем id и никнейм пользователя из сообщения
    user_id = msg.from_user.id
    nickname = msg.from_user.username

    # Вызываем функцию для записи данных пользователя в таблицу
    insert_user_db(user_id, nickname)

    # Отправляем сообщение пользователю о результате операции
    await msg.reply(f"Вы попытались записать свои данные в базу данных.")

@dp.message_handler(commands=["delete"])
async def delete_user(msg: types.Message):
    # Получаем id пользователя из сообщения
    user_id = msg.from_user.id

    # Вызываем функцию для удаления данных пользователя из таблицы
    delete_user_db(user_id)

    # Отправляем сообщение пользователю о результате операции
    await msg.reply(f"Вы попытались удалить свои данные из базы данных.")

@dp.message_handler(commands=["update"])
async def update_user(msg: types.Message):
    # Получаем id и никнейм пользователя из сообщения
    user_id = msg.from_user.id
    new_nickname = msg.from_user.username

    # Вызываем функцию для обновления данных пользователя в таблице
    update_user_db(user_id, new_nickname)

    # Отправляем сообщение пользователю о результате операции
    await msg.reply(f"Вы попытались обновить свои данные в базе данных.")


# Создаем обработчик команды /получить
@dp.message_handler(commands=["get"])
async def get_user_data(message: types.Message):
    # Получаем user_id из сообщения
    user_id = message.from_user.id
    # Вызываем функцию для получения никнейма из базы данных по user_id
    nickname = get_nickname_db(user_id)
    # Если никнейм не None, отправляем никнейм и user_id
    if nickname:
        await message.reply(f"Ваш никнейм: {nickname}\nВаш user_id: {user_id}")
    # Если никнейм None, отправляем сообщение об ошибке
    else:
        await message.reply("Вы не зарегистрированы в базе данных")


# Создаем фильтр с регулярным выражением для команды help
help_filter = filters.RegexpCommandsFilter(regexp_commands=['help ( [a-z]*)'])

# Фильтр для команды /start с использованием регулярного выражения
@dp.message_handler(regexp=r"^/help start$")
async def start_command(message: types.Message):
    await message.answer('/start - поздороваться со мной и узнать, кто меня написал')


# Фильтр для команды /записать с использованием регулярного выражения
@dp.message_handler(regexp=r"^/help write$")
async def record_command(message: types.Message):
    await message.answer('/write - сохранить информацию о себе в базу данных.')


# Фильтр для команды /удалить с использованием регулярного выражения
@dp.message_handler(regexp=r"^/help delete$")
async def delete_command(message: types.Message):
    await message.answer('/delete - удалить информацию о себе из базы данных.')


# Фильтр для команды /обновить с использованием регулярного выражения
@dp.message_handler(regexp=r"^/help update$")
async def update_command(message: types.Message):
    await message.answer('/update - обновить информацию о себе в базе данных.')


# Фильтр для команды /получить с использованием регулярного выражения
@dp.message_handler(regexp=r"^/help get$")
async def get_command(message: types.Message):
    await message.answer('/get - получить информацию о себе из базы данных.')

# инициализация обработчика для эхо сообщения
@dp.message_handler()
async def echo_message(message: types.Message):
    # отправка эхо текста
    await message.answer(message.text)


@dp.message_handler(content_types=["animation", "photo", "video", "document", "sticker"])
async def echo(message: types.Message):
    # Получаем тип контента и файл ID
    content_type = message.content_type
    file_id = message[content_type].file_id
    # Используем if content_type  для отправки обратно того же типа контента
    if content_type == "animation":
        await message.reply_animation(file_id)
    elif content_type == "photo":
        await message.reply_photo(file_id)
    elif content_type ==  "video":
        await message.reply_video(file_id)
    elif content_type ==  "document":
        await message.reply_document(file_id)
    elif content_type ==  "sticker":
        await message.reply_sticker(file_id)
    else:
        await message.reply("Неизвестный тип контента")


if __name__ == "__main__":
    executor.start_polling(dp)