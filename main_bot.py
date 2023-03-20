import logging
import flask # добавил импорт flask
from aiogram import Bot, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.webhook import SendMessage
from aiogram.utils.executor import start_webhook
import telebot # добавил импорт telebot

API_TOKEN = '6273983990:AAGNUQpjEen2GKcfJYtcHygvolZkzxg8Fpk'

# webhook settings
WEBHOOK_HOST = 'https://185.159.130.232' # ваш IP адрес здесь
WEBHOOK_PATH = '/path/to/api'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
WEBHOOK_URL_PATH = f"/{API_TOKEN}/" # добавил определение WEBHOOK_URL_PATH

# webserver settings
WEBAPP_HOST = 'localhost' # or ip
WEBAPP_PORT = 3001

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

@dp.message_handler()
async def echo(message: types.Message):
    # Regular request
    await bot.send_message(message.chat.id, message.text)

    # or reply INTO webhook
    return SendMessage(message.chat.id, message.text)


async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    # insert code here to run it after start


async def on_shutdown(dp):
    logging.warning('Shutting down..')

    # insert code here to run it before shutdown

    # Remove webhook (not acceptable in some cases)
    await bot.delete_webhook()

    # Close DB connection (if used)
    await dp.storage.close()
    await dp.storage.wait_closed()

    logging.warning('Bye!')

# Запускаем Flask сервер внутри кода бота    
app = flask.Flask(__name__)

@app.route('/')
def index():
  return ''

@app.route(WEBHOOK_URL_PATH, methods=['GET', 'POST'])
def webhook():
  if flask.request.headers.get('content-type') == 'application/json':
      json_string = flask.request.get_data().decode('utf-8')
      update = telebot.types.Update.de_json(json_string)
      bot.process_new_updates([update])
      return ''
  else:
      print('You NOT made it!')
      flask.abort(403)

if __name__ == '__main__':
  app.run(host=WEBAPP_HOST, port=WEBAPP_PORT)  