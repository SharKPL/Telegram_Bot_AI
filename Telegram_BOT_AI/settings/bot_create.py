from settings.data import TOKEN
from aiogram import Bot, Dispatcher

try:
    bot = Bot(token=TOKEN)
except:
    raise SystemExit('Неверный токен')
dp = Dispatcher(bot=bot)

