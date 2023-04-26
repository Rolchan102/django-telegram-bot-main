"""
    Telegram event handlers
"""
from telegram.ext import (
    Dispatcher, Filters,
    CommandHandler, MessageHandler,
    CallbackQueryHandler,
)

from dtb.settings import DEBUG
from tgbot.handlers.broadcast_message.manage_data import CONFIRM_DECLINE_BROADCAST
from tgbot.handlers.broadcast_message.static_text import broadcast_command

from tgbot.handlers.utils import files, error
from tgbot.handlers.onboarding import handlers as onboarding_handlers
from tgbot.handlers.onboarding import registration as onboarding_registration
from tgbot.handlers.onboarding import coffee
from tgbot.handlers.broadcast_message import handlers as broadcast_handlers
from tgbot.main import bot


def setup_dispatcher(dp):
    """
    Добавление обработчиков событий из Telegram
    """
    # start
    dp.add_handler(CommandHandler("start", onboarding_handlers.command_start))

    # # registration
    # mail_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    # dp.add_handler(MessageHandler(Filters.regex(mail_pattern), onboarding_registration.check_email))
    #
    # # check_code
    # code_pattern = r'\d{6}'
    # dp.add_handler(MessageHandler(Filters.regex(code_pattern), onboarding_handlers.command_start))

    # game
    # dp.add_handler(CommandHandler("game", coffee.start))

    # # broadcast message
    # dp.add_handler(
    #     MessageHandler(Filters.regex(rf'^{broadcast_command}(/s)?.*'),
    #                    broadcast_handlers.broadcast_command_with_message)
    # )
    # dp.add_handler(
    #     CallbackQueryHandler(broadcast_handlers.broadcast_decision_handler, pattern=f"^{CONFIRM_DECLINE_BROADCAST}")
    # )

    # # files
    # dp.add_handler(MessageHandler(
    #     Filters.animation, files.show_file_id,
    # ))

    # handling errors
    dp.add_error_handler(error.send_stacktrace_to_tg_chat)

    return dp


n_workers = 0 if DEBUG else 4
dispatcher = setup_dispatcher(Dispatcher(bot, update_queue=None, workers=n_workers, use_context=True))
