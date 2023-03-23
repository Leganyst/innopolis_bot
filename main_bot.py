# Link to the bot: https://t.me/innopolis_testing_bot
import sys
import locale

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

# Импортируем функции из файла с базой данных
from database import insert_user_db, delete_user_db, update_user_db, get_nickname_db


TOKEN = "6273983990:AAGNUQpjEen2GKcfJYtcHygvolZkzxg8Fpk"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

sys.setdefaultencoding ('utf8')
locale.setlocale (locale.LC_ALL, 'en_US.UTF-8')


@dp.message_handler(commands=["start"])
async def send_welcome(msg: types.Message):
    await msg.reply(f"Я бот. Меня написал Марк Клавишин. Я работаю круглосуточно, так как установлен на VDS хостинге.")

@dp.message_handler(commands=["записать"])
async def record_user(msg: types.Message):
    # Получаем id и никнейм пользователя из сообщения
    user_id = msg.from_user.id
    nickname = msg.from_user.username

    # Вызываем функцию для записи данных пользователя в таблицу
    insert_user_db(user_id, nickname)

    # Отправляем сообщение пользователю о результате операции
    await msg.reply(f"Вы попытались записать свои данные в базу данных.")

@dp.message_handler(commands=["удалить"])
async def delete_user(msg: types.Message):
    # Получаем id пользователя из сообщения
    user_id = msg.from_user.id

    # Вызываем функцию для удаления данных пользователя из таблицы
    delete_user_db(user_id)

    # Отправляем сообщение пользователю о результате операции
    await msg.reply(f"Вы попытались удалить свои данные из базы данных.")

@dp.message_handler(commands=["обновить"])
async def update_user(msg: types.Message):
    # Получаем id и никнейм пользователя из сообщения
    user_id = msg.from_user.id
    new_nickname = msg.from_user.username

    # Вызываем функцию для обновления данных пользователя в таблице
    update_user_db(user_id, new_nickname)

    # Отправляем сообщение пользователю о результате операции
    await msg.reply(f"Вы попытались обновить свои данные в базе данных.")


# Создаем обработчик команды /получить
@dp.message_handler(commands=["получить"])
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


@dp.message_handler(commands=["help"])
async def send_help(msg: types.Message):
    # Формируем текст справки по командам бота
    help_text = """
    Я бот, который работает с базой данных пользователей Telegram.
    Вот список команд, которые я понимаю:
    /start - поздороваться со мной и узнать, кто меня написал
    /записать - записать свой id и никнейм в базу данных
    /удалить - удалить свой id и никнейм из базы данных
    /обновить - обновить свой никнейм в базе данных
    /help - получить эту справку по командам
    /получить - получить свои данные
    """

    # Отправляем сообщение пользователю с текстом справки
    await msg.reply(help_text)


if __name__ == "__main__":
    executor.start_polling(dp)