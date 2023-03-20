import asyncio
import logging

from aiogram import Bot, Dispatcher, executor, types
from aiohttp import web

API_TOKEN = '6273983990:AAGNUQpjEen2GKcfJYtcHygvolZkzxg8Fpk'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler()
async def echo(message: types.Message):
    # Просто отправляем обратно то же самое сообщение
    await message.answer(message.text)


async def init_app():
    # Создаем web-приложение aiohttp
    app = web.Application()
    # Регистрируем обработчик для webhook-запросов от Telegram
    app.router.add_post('/webhook/{token}', handle_webhook)
    # Возвращаем созданное приложение
    return app

async def handle_webhook(request: web.Request):
    # Получаем токен из URL-параметра (для проверки подлинности запроса)
    token = request.match_info['token']
    if token != API_TOKEN:
        # Если токен не совпадает с нашим - возвращаем ошибку 403 Forbidden
        return web.Response(status=403)

    # Получаем данные из тела запроса (это JSON-объект Update от Telegram)
    data = await request.json()
    
    # Передаем данные диспетчеру aiogram для обработки обновления 
    await dp.process_update(data)

    # Возвращаем пустой ответ 200 OK 
    return web.Response()

async def start_webhook():

    # Получаем текущий цикл событий asyncio 
    loop = asyncio.get_event_loop()
    
    global runner
    # Создаем объект web-runner для запуска нашего приложения aiohttp 
    runner = web.AppRunner(await init_app())


    # Запускаем runner 
    await runner.setup()
    # Создаем объект сайта (site) с указанием IP-адреса и порта для прослушивания 
    site = web.TCPSite(runner=runner,
                        host='185.159.130.232',  # IP-адрес сервера
                        port=8443)  # Порт (должен быть открыт для входящих соединений)

    # Запускаем сайт 
    await site.start()

    # Формируем URL для webhook-сервера 
    webhook_url = f'https://{site.host}:{site.port}/webhook/{API_TOKEN}'

    # Устанавливаем webhook для нашего бота 
    await bot.set_webhook(webhook_url)

    # Выводим информацию о запущенном сервере 
    logging.info(f'Webhook server started at {webhook_url}')


async def stop_webhook():
    
     # Снимаем webhook с нашего бота 
     await bot.delete_webhook()

     # Останавливаем runner и освобождаем ресурсы 
     await runner.cleanup()

     # Выводим информацию об остановленном сервере 
     logging.info('Webhook server stopped')



if __name__ == '__main__':
    
     try:
         # Запускаем webhook-сервер
         asyncio.run(start_webhook())

         # Ждем нажатия Ctrl+C
         asyncio.get_event_loop().run_forever()
     
     except KeyboardInterrupt:
         # Останавливаем webhook-сервер
         asyncio.run(stop_webhook())