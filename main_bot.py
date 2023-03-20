import logging
from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = '6273983990:AAGNUQpjEen2GKcfJYtcHygvolZkzxg8Fpk' # замените на токен вашего бота
WEBHOOK_HOST = 'https://185.159.130.232' # адрес вашего сервера
WEBHOOK_PATH = '/webhook/' # путь для вебхука
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler()
async def echo(message: types.Message):
    # Отправляем обратно то же самое сообщение
    await message.answer(message.text)

async def on_startup(dp):
    # Устанавливаем вебхук
    await bot.set_webhook(WEBHOOK_URL, certificate=open(r'/etc/ssl/private/server.key', 'rb'))

async def on_shutdown(dp):
    # Удаляем вебхук при остановке бота
    await bot.delete_webhook()

if __name__ == '__main__':
    # Запускаем веб-сервер для приема запросов от телеграма
    executor.start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host='0.0.0.0', # слушаем все адреса на сервере
        port=8443 # порт для веб-сервера (можно выбрать любой свободный)
    )