from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


off = KeyboardButton('выключить')
screen = KeyboardButton('скрин')
cancel = KeyboardButton('отмена')
web = KeyboardButton('снимок')
myId = KeyboardButton('id')
coms_list = KeyboardButton('список команд')
com_kb = ReplyKeyboardMarkup(resize_keyboard=True)
com_kb.row(off, cancel, coms_list)
#com_kb.add(screen)
com_kb.row(screen, web, myId)
