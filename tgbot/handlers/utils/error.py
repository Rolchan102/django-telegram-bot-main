import logging
import traceback
import html

import telegram
from django.utils import timezone
from telegram import Update
from telegram.ext import CallbackContext
from users.models import UserActionLog, User
from dtb.settings import TELEGRAM_LOGS_CHAT_ID


def send_stacktrace_to_tg_chat(update: Update, context: CallbackContext) -> None:
    if 'email' in context.user_data:
        u = User.get_user(update, context)

    logging.error("Исключение при обработке обновления:", exc_info=context.error)

    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    message = (
        f'Возникло исключение при обработке обновления\n'
        f'<pre>{html.escape(tb_string)}</pre>'
    )

    user_message = """
        😔 Что-то сломалось внутри бота.
        Мы постоянно улучшаем наш сервис, но иногда можем забыть протестировать некоторые базовые вещи.
        Мы уже решаем проблему.
        Перезапустите команду /start
    """
    context.bot.send_message(
        chat_id=update.message.from_user.id,
        text=user_message,
    )

    admin_message = f"⚠️⚠️⚠️ для {update.message.from_user.id}:\n{message}"[:4090]
    if TELEGRAM_LOGS_CHAT_ID:
        context.bot.send_message(
            chat_id=TELEGRAM_LOGS_CHAT_ID,
            text=admin_message,
            parse_mode=telegram.ParseMode.HTML,
        )
    else:
        logging.error(admin_message)
