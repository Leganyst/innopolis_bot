# Устанавливается ngrok
# Запускается от имени администратора
# На сайте после регистрации берётся токен
# Вводим в открывшийся консоли: ngrok authtoken <YOUR_AUTH_TOKEN>, где в <> скопированный токен
# В консоль вводится ngrok http <port_number>. Номер порта должен совпадать с тем, что в коде бота.
# Далее получаем URL адрес. Его вставляет в WEBHOOK_HOST.
# Запускаем и проверяем работу.



import logging # импортируем модуль logging для журналирования

from aiogram import executor
from aiogram import Bot, types # импортируем классы Bot и types из модуля aiogram
from aiogram.contrib.middlewares.logging import LoggingMiddleware # импортируем класс LoggingMiddleware из модуля aiogram.contrib.middlewares.logging
from aiogram.dispatcher import Dispatcher # импортируем класс Dispatcher из модуля aiogram.dispatcher
from aiogram.dispatcher.webhook import SendMessage # импортируем класс SendMessage из модуля aiogram.dispatcher.webhook
from aiogram.utils.executor import start_webhook # импортируем функцию start_webhook из модуля aiogram.utils.executor

API_TOKEN = '6273983990:AAGNUQpjEen2GKcfJYtcHygvolZkzxg8Fpk' # задаем токен бота, полученный от @BotFather

# настройки webhook
# WEBHOOK_HOST = 'https://ca10-51-158-200-114.eu.ngrok.io'  # указываем имя вашего приложения
# WEBHOOK_PATH = '/path/to/api' # указываем путь к API
# WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}" # формируем полный URL webhook

# # настройки веб-сервера
# WEBAPP_HOST = '185.159.130.232'  # или IP-адрес
# WEBAPP_PORT = 8443

logging.basicConfig(level=logging.INFO) # устанавливаем уровень журналирования INFO

bot = Bot(token=API_TOKEN) # создаем экземпляр бота с заданным токеном
dp = Dispatcher(bot) # создаем экземпляр диспетчера с заданным ботом
dp.middleware.setup(LoggingMiddleware()) # добавляем промежуточное ПО для журналирования


@dp.message_handler(commands=['start']) # регистрируем обработчик сообщений с командой /start
async def send_welcome(message: types.Message): 
    await message.reply("Привет. Я телеграм бот, и меня сделал Марк Клавишин!") # отправляем ответное сообщение с приветствием


@dp.message_handler() # регистрируем обработчик всех остальных сообщений 
async def echo(message: types.Message):
    await message.answer(message.text) # отправляем ответное сообщение с тем же текстом


# async def on_startup(dp): 
#     await bot.set_webhook(WEBHOOK_URL) # устанавливаем webhook при запуске приложения


# async def on_shutdown(dp):
#     logging.warning('Shutting down..') 

#     await bot.delete_webhook() # удаляем webhook при остановке приложения 
#     await dp.storage.close() 
#     await dp.storage.wait_closed()

#     logging.warning('Bye!')


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True)
    # start_webhook(
    #     dispatcher=dp,
    #     webhook_path=WEBHOOK_PATH,
    #     on_startup=on_startup,
    #     on_shutdown=on_shutdown,
    #     skip_updates=True,
    #     host=WEBAPP_HOST,
    #     port=WEBAPP_PORT,
    # ) 