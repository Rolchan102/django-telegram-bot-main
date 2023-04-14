from telegram import ReplyKeyboardMarkup, KeyboardButton

from tgbot.handlers.location.static_text import SEND_LOCATION


def send_location_keyboard() -> ReplyKeyboardMarkup:
    # (resize_keyboard=False) - эта кнопка появится на половине экрана (станет очень большой).
    # Скорее всего, это повысит конверсию кликов, но может снизить качество UX.
    return ReplyKeyboardMarkup(
        [[KeyboardButton(text=SEND_LOCATION, request_location=True)]],
        resize_keyboard=True
    )
