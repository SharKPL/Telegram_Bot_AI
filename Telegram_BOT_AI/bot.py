from settings.bot_settings import *


def bot_start():
    executor.start_polling(dp)

#
# def bot_stop():
#     dp.stop_polling()


if __name__ == '__main__':
    bot_start()


