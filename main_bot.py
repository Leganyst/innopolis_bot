import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.executor import start_webhook

API_TOKEN = '6273983990:AAGNUQpjEen2GKcfJYtcHygvolZkzxg8Fpk'

# настройки вебхука
WEBHOOK_HOST = 'https://innopolis-bot-meyld.run-eu-central1.goorm.site'
WEBHOOK_PATH = '/webhook'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# настройки веб-сервера
WEBAPP_HOST = '3.70.135.253' # или ip
WEBAPP_PORT = 8443

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    Этот обработчик будет вызван, когда пользователь отправит команду `/start` или `/help`
    """
    await message.reply("Привет!\nЯ EchoBot!\nРаботаю на aiogram.")

@dp.message_handler()
async def echo(message: types.Message):
    # старый способ:
    # await bot.send_message(message.chat.id, message.text)

    await message.answer(message.text)

async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    # вставьте здесь код для запуска после старта

async def on_shutdown(dp):
    logging.warning('Выключение..')

    # вставьте здесь код для запуска перед выключением

    # Удалить вебхук (необязательно)
    await bot.delete_webhook()

    # Закрыть соединение с БД (если используется)
    await dp.storage.close()
    await dp.storage.wait_closed()

    logging.warning('Пока!')

if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )



# У меня имеется следующий код: import logging from aiogram import Bot, Dispatcher, executor, types from aiogram.utils.executor import start_webhook API_TOKEN = '6273983990:AAGNUQpjEen2GKcfJYtcHygvolZkzxg8Fpk' # настройки вебхука WEBHOOK_HOST = 'https://innopolis-bot-meyld.run-eu-central1.goorm.site' WEBHOOK_PATH = '/webhook' WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}" # настройки веб-сервера WEBAPP_HOST = '172.17.0.21' # или ip WEBAPP_PORT = 8443 logging.basicConfig(level=logging.INFO) bot = Bot(token=API_TOKEN) dp = Dispatcher(bot) @dp.message_handler(commands=['start', 'help']) async def send_welcome(message: types.Message): """ Этот обработчик будет вызван, когда пользователь отправит команду `/start` или `/help` """ await message.reply("Привет!\nЯ EchoBot!\nРаботаю на aiogram.") @dp.message_handler() async def echo(message: types.Message): # старый способ: # await bot.send_message(message.chat.id, message.text) await message.answer(message.text) async def on_startup(dp): await bot.set_webhook(WEBHOOK_URL) # вставьте здесь код для запуска после старта async def on_shutdown(dp): logging.warning('Выключение..') # вставьте здесь код для запуска перед выключением # Удалить вебхук (необязательно) await bot.delete_webhook() # Закрыть соединение с БД (если используется) await dp.storage.close() await dp.storage.wait_closed() logging.warning('Пока!') if __name__ == '__main__': start_webhook( dispatcher=dp, webhook_path=WEBHOOK_PATH, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True, host=WEBAPP_HOST, port=WEBAPP_PORT, ) Однако при выполнении этого кода на своём VDS сервере я получил ошибку: 