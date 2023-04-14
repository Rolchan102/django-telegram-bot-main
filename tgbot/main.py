import logging
import sys

import telegram
from telegram import Bot

from dtb.settings import TELEGRAM_TOKEN


bot = Bot(TELEGRAM_TOKEN)
TELEGRAM_BOT_USERNAME = bot.get_me()["username"]
# Глобальная переменная - лучший способ, который я нашел для инициализации Telegram бота
try:
    pass
except telegram.error.Unauthorized:
    logging.error("Invalid TELEGRAM_TOKEN.")
    sys.exit(1)
