# Link to the bot: https://t.me/innopolis_testing_bot
import sys
import locale
import re


from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram.dispatcher import filters
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.utils.exceptions import BadRequest
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.builtin import ChatType
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler



# Импортируем функции из файла с базой данных
from database import insert_user_db, delete_user_db, update_user_db, get_nickname_db, is_banned, ban_user, unban_user


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
                                     

# Класс миддлвари для проверки черного списка
class BlacklistMiddleware(BaseMiddleware):
    # Метод для обработки входящих сообщений
    async def on_process_message(self, message: types.Message, data: dict):
        # Проверяем, находится ли пользователь в черном списке
        if await is_banned(message.from_user.id):
            # Если да, то прерываем цепочку обработки сообщения
            try:
                raise CancelHandler()
            except Exception:
                pass
        # Иначе продолжаем обработку сообщения как обычно

# Регистрируем миддлварь в диспетчере
dp.middleware.setup(BlacklistMiddleware())


# Функция для проверки, является ли пользователь администратором группы
async def is_admin(chat_id, user_id):
    member = await bot.get_chat_member(chat_id, user_id)
    return member.is_chat_admin()

# Хэндлер для команды /ban
@dp.message_handler(commands=["ban"])
async def ban_command(message: types.Message):
    # Проверяем, является ли отправитель команды администратором группы
    if await is_admin(message.chat.id, message.from_user.id):
        # Проверяем, есть ли упомянутый пользователь в сообщении
        if message.reply_to_message:
            # Получаем user_id упомянутого пользователя
            user_id = message.reply_to_message.from_user.id
            # Проверяем, не является ли он администратором группы
            if not await is_admin(message.chat.id, user_id):
                # Добавляем пользователя в черный список
                await ban_user(user_id)
                # Пытаемся забанить пользователя в группе навсегда
                try:
                    # await bot.kick_chat_member(message.chat.id, user_id)
                    await message.reply(f"Пользователь {user_id} забанен.")
                except BadRequest:
                    await message.reply(f"Не удалось забанить пользователя {user_id} в группе. Возможно, он уже покинул ее.")
            else:
                await message.reply("Нельзя забанить администратора группы.")
        else:
            await message.reply("Вы должны упомянуть пользователя, которого хотите забанить.")
    else:
        await message.reply("Вы не являетесь администратором группы.")


# Хэндлер для команды /unban
@dp.message_handler(commands=["unban"], chat_type=[ChatType.GROUP, ChatType.SUPERGROUP])
async def unban_command(message: types.Message):
    # Проверяем, является ли отправитель команды администратором группы
    if await is_admin(message.chat.id, message.from_user.id):
        # Проверяем, есть ли упомянутый пользователь в сообщении
        if message.reply_to_message:
            # Получаем user_id упомянутого пользователя
            user_id = message.reply_to_message.from_user.id
            # Проверяем, находится ли он в черном списке
            if await is_banned(user_id):
                # Удаляем пользователя из черного списка
                await unban_user(user_id)
                # Пытаемся разбанить пользователя в группе
                try:
                    # await bot.unban_chat_member(message.chat.id, user_id)
                    await message.reply(f"Пользователь {user_id} разбанен.")
                except BadRequest:
                    await message.reply(f"Не удалось разбанить пользователя {user_id} в группе. Возможно, он уже покинул ее.")
            else:
                await message.reply("Этот пользователь не находится в черном списке.")
        else:
            await message.reply("Вы должны упомянуть пользователя, которого хотите разбанить.")
    else:
        await message.reply("Вы не являетесь администратором группы.")

# Хэндлер для команды /checkban
@dp.message_handler(commands=["checkban"], chat_type=[ChatType.GROUP, ChatType.SUPERGROUP])
async def checkban_command(message: types.Message):
    # Проверяем, является ли отправитель команды администратором группы
    if await is_admin(message.chat.id, message.from_user.id):
        # Проверяем, есть ли упомянутый пользователь в сообщении
        if message.reply_to_message:
            # Получаем user_id упомянутого пользователя
            user_id = message.reply_to_message.from_user.id
            # Проверяем, находится ли он в черном списке
            if await is_banned(user_id):
                await message.reply(f"Пользователь {user_id} находится в черном списке.")
            else:
                await message.reply(f"Пользователь {user_id} не находится в черном списке.")
        else:
            await message.reply("Вы должны упомянуть пользователя, статус которого хотите проверить.")
    else:
        await message.reply("Вы не являетесь администратором группы.")



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