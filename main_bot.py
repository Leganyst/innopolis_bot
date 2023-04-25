# Link to the bot: https://t.me/innopolis_testing_bot

from config import TOKEN

from aiogram.dispatcher import FSMContext
from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram.dispatcher import filters
from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.utils.exceptions import BadRequest
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters.builtin import ChatType
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.filters.state import State, StatesGroup

import random
import sqlite3


# Создаем соединение с базой данных
conn = sqlite3.connect("users_telegram.db")

# Создаем курсор для выполнения SQL-запросов
cur = conn.cursor()


# ############################################################################################################################################
# ############################################################################################################################################
# БАЗА ДАННЫХ БАЗА ДАННЫХ БАЗА ДАННЫХ БАЗА ДАННЫХ БАЗА ДАННЫХ БАЗА ДАННЫХ БАЗА ДАННЫХ БАЗА ДАННЫХ БАЗА ДАННЫХ БАЗА ДАННЫХ БАЗА ДАННЫХ БАЗА
# ############################################################################################################################################
# ############################################################################################################################################


# Создаем таблицу users, если она еще не существует
cur.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, nickname TEXT, blacklist bool)")

# Функция проверки нахождения юзера в бд
def check_user_in_db(user_id):
    # Проверяем, есть ли уже такой пользователь в таблице
    cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cur.fetchone()
    if user is None:
        return False
    return True


# Функция для записи данных пользователя в таблицу
def insert_user_db(user_id, nickname):
    # Проверяем, есть ли уже такой пользователь в таблице
    cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cur.fetchone()
    if user is None:
        # Если нет, то добавляем его в таблицу
        cur.execute("INSERT INTO users (user_id, nickname) VALUES (?, ?)", (user_id, nickname))
        conn.commit()
        print(f"Пользователь {nickname} добавлен в базу данных.")
    else:
        # Если есть, то выводим сообщение об ошибке
        print(f"Пользователь {nickname} уже есть в базе данных.")

# Функция для удаления данных пользователя из таблицы
def delete_user_db(user_id):
    # Проверяем, есть ли такой пользователь в таблице
    cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cur.fetchone()
    if user is not None:
        # Если есть, то удаляем его из таблицы
        cur.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()
        print(f"Пользователь {user[1]} удален из базы данных.")
    else:
        # Если нет, то выводим сообщение об ошибке
        print(f"Пользователя с таким id нет в базе данных.")

# Функция для обновления данных пользователя в таблице
def update_user_db(user_id, new_nickname):
    # Проверяем, есть ли такой пользователь в таблице
    cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cur.fetchone()
    if user is not None:
        # Если есть, то обновляем его никнейм в таблице
        cur.execute("UPDATE users SET nickname = ? WHERE user_id = ?", (new_nickname, user_id))
        conn.commit()
        print(f"Пользователь {user[1]} обновлен на {new_nickname}.")
    else:
        # Если нет, то выводим сообщение об ошибке
        print(f"Пользователя с таким id нет в базе данных.")

# Создаем функцию для получения никнейма из базы данных по user_id
def get_nickname_db(user_id):
    # Создаем подключение к базе данных
    # Пытаемся найти запись в таблице users по user_id
    cur.execute("SELECT nickname FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    # Если запись найдена, возвращаем никнейм
    if row:
        nickname = row[0]
        return nickname
    # Если запись не найдена, возвращаем None
    else:
        return None
    
# Функция для проверки, находится ли пользователь в черном списке
async def is_banned(user_id):
    # Формируем SQL-запрос для получения значения столбца blacklist по user_id
    sql = f"SELECT blacklist FROM users WHERE user_id = {user_id};"
    # Выполняем запрос и получаем результат
    cur.execute(sql)
    result = cur.fetchone()
    # Если результат не пустой, возвращаем значение столбца blacklist (True или False)
    if result:
        return result[0]
    # Иначе возвращаем False, так как пользователь не находится в базе данных
    else:
        return False

# Функция для добавления пользователя в черный список
async def ban_user(user_id):
    # Проверяем, есть ли пользователь в базе данных
    if await is_banned(user_id) is False:
        # Если нет, то добавляем его в таблицу users с значением столбца blacklist в True
        sql = f"INSERT INTO users (user_id, blacklist) VALUES ({user_id}, True);"
        cur.execute(sql)
        conn.commit()
    else:
        # Если есть, то обновляем значение столбца blacklist в True
        sql = f"UPDATE users SET blacklist = True WHERE user_id = {user_id};"
        cur.execute(sql)
        conn.commit()


# Функция для удаления пользователя из черного списка
async def unban_user(user_id):
    # Проверяем, есть ли пользователь в базе данных
    if await is_banned(user_id):
        # Если есть, то обновляем значение столбца blacklist в False
        sql = f"UPDATE users SET blacklist = False WHERE user_id = {user_id};"
        cur.execute(sql)
        conn.commit()

# ############################################################################################################################################
# ############################################################################################################################################
#
# ############################################################################################################################################
# ############################################################################################################################################



# ############################################################################################################################################
# ############################################################################################################################################
# БОТ БОТ БОТ БОТ БОТ БОТ БОТ БОТ БОТ БОТ БОТ БОТ БОТ БОТ БОТ БОТ БОТ БОТ БОТ БОТ БОТ БОТ БОТ БОТ БОТ БОТ БОТ БОТ БОТ БОТ БОТ БОТ БОТ БОТ БОТ
# ############################################################################################################################################
# ############################################################################################################################################


'''Инициализация бота''' 
bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


'''Меню команд по одному из уроков.'''
# Меню команд 
async def set_default_commands(bot: Bot):
    commands = [
        BotCommand('start', 'Команда запуска бота'),
        BotCommand('get', 'Получение информации о себе из базы данных'),
        BotCommand('update', 'Обновление информации о себе в базе данных'),
        BotCommand('write', 'Записать информацию о себе в базу данных'),
        BotCommand('delete', 'Удалить информацию о себе из базы данных'),
        BotCommand('about', 'Информация о боте'),
        BotCommand('films', 'Список любимых фильмов/сериалов/аниме автора'),
        BotCommand('location', "Отправить геолокацию"),
        BotCommand('keyboard', 'Вызвать клавиатуру с двумя кнопками :)')
    ]
    return await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())
                                     

"""Создаём миддлвари для черного списка. Каждый обработчик после будет проверять, находится ли человек в ЧС бота или нет."""
# Класс миддлвари для проверки черного списка
class BlacklistMiddleware(BaseMiddleware):
    # Метод для обработки входящих сообщений
    async def on_process_message(self, message: types.Message, data: dict):
        # Проверяем, находится ли пользователь в черном списке
        if await is_banned(message.from_user.id):
            # Если да, то прерываем цепочку обработки сообщения
            raise CancelHandler()
        # Иначе продолжаем обработку сообщения как обычно

# Регистрируем миддлварь в диспетчере
dp.middleware.setup(BlacklistMiddleware())

"""Служебная функция для чатов"""
# Функция для проверки, является ли пользователь администратором группы
async def is_admin(chat_id, user_id):
    member = await bot.get_chat_member(chat_id, user_id)
    return member.is_chat_admin()


# ---------------------------
'''Чёрный список и команды'''
# ---------------------------

# Хэндлер для команды /ban
@dp.message_handler(commands=["ban"], chat_type=[ChatType.GROUP, ChatType.SUPERGROUP])
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

# --------------------------------
"""Конец блока с чёрным списком"""
# --------------------------------


# --------------------------------
"""Рядовые команды"""
# --------------------------------
@dp.message_handler(commands=['about'])
async def send_about(message: types.Message):

    text = (r'<b>Привет.</b> Я пет-проект являющийся ботом в телеграм реализованный <a href="https://t.me/legannyst/">Марком Клавишиным</a>' 
        ' по курсу "<i>Код будущего</i>" от университета Иннополис.\nТы можешь получить информацию о командах введя <code>/help *команда*</code>.'
        r' В принципе, ничего особенного - я просто могу записать твой user_id и nickname в базу'
        ' и выслать их обратно тебе.\nНу и в случае чего - я имею функцию при которой админы группы заставят меня тебя игнорировать. Так что будь аккуратен.')
    await message.answer(text)


@dp.message_handler(commands=["start"])
async def send_welcome(msg: types.Message):
    await msg.reply(f"Я бот. Меня написал Марк Клавишин. Подробнее - /about ")
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
# -----------------------------
'Конец блока рядовых команд'
# -----------------------------



# ----------------------------
"Блок команд с регулярными выражениями. Выводят чуть более детальную справку по каждой команде."
# ----------------------------

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

# -----------------------------------
"Конец блока с регулярными выражениями"
# -----------------------------------



# -----------------------------------
"Клавиатура!!!"
# -----------------------------------

# Создаем клавиатуру с двумя кнопками "ДА" и "НЕТ"
keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add("ДА", "НЕТ")

# создаем класс состояний
class Form(StatesGroup):
    waiting_for_confirmation = State()
    waiting_for_location = State()


# Регистрируем обработчик команды /keyboard
@dp.message_handler(commands=["keyboard"])
async def send_keyboard(message: types.Message, state: FSMContext):
    # Отправляем сообщение с клавиатурой и переходим в состояние waiting_for_confirmation
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text="ДА"), types.KeyboardButton(text="НЕТ"))
    await message.answer("Вы хотите продолжить?", reply_markup=keyboard)
    await Form.waiting_for_confirmation.set()

# Регистрируем обработчик нажатия кнопок
@dp.message_handler(state=Form.waiting_for_confirmation)
async def handle_buttons(message: types.Message, state: FSMContext):
    # Проверяем текст сообщения
    if message.text == "ДА":
        # Отправляем сообщение "ДА" и скрываем клавиатуру, затем переходим в начальное состояние
        await message.reply("ДА", reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
    elif message.text == "НЕТ":
        # Отправляем сообщение "НЕТ" и скрываем клавиатуру, затем переходим в начальное состояние
        await message.reply("НЕТ", reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
    else:
        # Отправляем сообщение "Не понимаю"
        await message.reply("Не понимаю")


# Начало блока с геолокацией
"Клавиша для отправки геолокации и реакция на отправку геолокации"
# функция, которая отправляет геолокацию боту
@dp.message_handler(commands=['location'])
async def send_location(message: types.Message, state: FSMContext):
    # создаем объект клавиатуры
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    # добавляем кнопку для отправки геолокации
    button = types.KeyboardButton(text="Отправить геолокацию", request_location=True)
    keyboard.add(button)
    # отправляем сообщение с клавиатурой
    await message.answer("Нажмите на кнопку, чтобы отправить геолокацию", reply_markup=keyboard)
    await Form.waiting_for_location.set()

# Регистрируем обработчик при состоянии ожидания локации
@dp.message_handler(content_types=types.ContentType.LOCATION, state=Form.waiting_for_location)
async def answer_location(message: types.Message, state: FSMContext):
    # Отвечаем и удаляем клавиатуру, сбрасываем состояние.
    await message.answer('Геолокация принята. Спасибо!', reply_markup=types.ReplyKeyboardRemove())
    await state.finish()

# Конец блока с геолокацией


# Инлайн кнопка для фильма
# Обрабатываем команду /inline
@dp.message_handler(commands=["films"])
async def inline(message: types.Message):
    # Создаем объект инлайн-клавиатуры с одной кнопкой
    keyboard = types.InlineKeyboardMarkup()
    # Добавляем кнопку с текстом "Перейти на сайт" и url-адресом
    keyboard.add(types.InlineKeyboardButton(text="Бойцовский клуб", url="https://www.kinopoisk.ru/film/361/?utm_referrer=yandex.ru"))
    keyboard.add(types.InlineKeyboardButton(text="Initial D", url="https://www.kinopoisk.ru/series/230874/"))
    keyboard.add(types.InlineKeyboardButton(text="Мир, дружба, жвачка", url="https://www.kinopoisk.ru/series/1306638/"))
    keyboard.add(types.InlineKeyboardButton(text="Blade Runner 2049", url="https://www.kinopoisk.ru/film/589290/"))
    keyboard.add(types.InlineKeyboardButton(text="Drive", url="https://www.kinopoisk.ru/film/276598/"))
    keyboard.add(types.InlineKeyboardButton(text="На игле", url="https://www.kinopoisk.ru/film/515/"))
    # Отправляем сообщение с клавиатурой в ответ на команду
    await message.reply("Нажми на кнопку, чтобы узнать подробнее о моем любимом фильме/сериале/аниме", reply_markup=keyboard)



# -----------------------------------------------
"Попытка реализовать мини-игру 'Орёл-решка' на инлайн кнопках"
# -----------------------------------------------

# Создаем обработчик команды /game

# @dp.callback_query_handler(lambda c: c.data == 'yes')
@dp.message_handler(commands=['game'])
async def game_handler(message: types.Message):
    # Создаем объект клавиатуры с двумя кнопками: Орёл и Решка
    keyboard = types.InlineKeyboardMarkup()
    button_eagle = types.InlineKeyboardButton(text='Орёл', callback_data='eagle')
    button_tails = types.InlineKeyboardButton(text='Решка', callback_data='tails')
    keyboard.row(button_eagle, button_tails)
    # Отправляем сообщение с клавиатурой пользователю
    await message.answer('Выбери: Орёл или Решка', reply_markup=keyboard)

# Создаем обработчик нажатий на кнопки клавиатуры
@dp.callback_query_handler(lambda c: c.data in ['eagle', 'tails'])
async def process_callback_game(callback_query: types.CallbackQuery):
    # Получаем выбор пользователя из данных кнопки
    user_choice = callback_query.data
    # Генерируем случайное число 0 или 1
    coin_flip = random.randint(0, 1)
    # Присваиваем результату подбрасывания монеты строку Орёл или Решка в зависимости от случайного числа
    if coin_flip == 0:
        coin_result = 'Орёл'
    else:
        coin_result = 'Решка'
    # Проверяем, совпал ли выбор пользователя с результатом подбрасывания монеты
    if user_choice == 'eagle' and coin_result == 'Орёл' or user_choice == 'tails' and coin_result == 'Решка':
        # Если да, то отправляем сообщение о победе и предлагаем сыграть ещё раз
        text = 'Ты победил. Хочешь ещё?'
    else:
        # Если нет, то отправляем сообщение о проигрыше и не предлагаем сыграть ещё раз
        text = 'Ты проиграл. Хочешь ещё?'

    # Редактируем сообщение с подбрасыванием монеты на новое сообщение с результатом и новой клавиатурой (если есть)
    # Создаем объект клавиатуры с двумя кнопками: да и нет
    keyboard = types.InlineKeyboardMarkup()
    button_yes = types.InlineKeyboardButton(text='да', callback_data='yes')
    button_no = types.InlineKeyboardButton(text='нет', callback_data='no')
    keyboard.row(button_yes, button_no)
    await bot.edit_message_text(text=text, chat_id=callback_query.message.chat.id,
                                 message_id=callback_query.message.message_id, reply_markup=keyboard)

# Создаем обработчик нажатия на кнопку да
@dp.callback_query_handler(lambda c: c.data == 'yes')
async def process_callback_game_again(callback_query: types.CallbackQuery):
    # Создаем объект клавиатуры с двумя кнопками: Орёл и Решка
    keyboard = types.InlineKeyboardMarkup()
    button_eagle = types.InlineKeyboardButton(text='Орёл', callback_data='eagle')
    button_tails = types.InlineKeyboardButton(text='Решка', callback_data='tails')
    keyboard.row(button_eagle, button_tails)
    # Редактируем сообщение с результатом на новое сообщение с подбрасыванием монеты и новой клавиатурой
    await bot.edit_message_text(text='Выбери: Орёл или Решка', chat_id=callback_query.message.chat.id,
                                 message_id=callback_query.message.message_id, reply_markup=keyboard)

# Создаём обработчик нажатия на кноику нет
@dp.callback_query_handler(lambda c: c.data == 'no')
async def cancel_game(callback_query: types.CallbackQuery):
    # нулевая клавиатура
    keyboard = None
    # редактируем сообщение
    await bot.edit_message_text(text="Ну как хочешь.", chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id, reply_markup=keyboard)



if __name__ == "__main__":
    executor.start_polling(dp)