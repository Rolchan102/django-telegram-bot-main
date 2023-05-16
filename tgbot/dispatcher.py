"""
    Telegram event handlers
"""
from datetime import time

from telegram.ext import (
    Dispatcher,
    Filters,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
)

from dtb.settings import DEBUG
from tgbot.handlers.broadcast_message.manage_data import CONFIRM_DECLINE_BROADCAST
from tgbot.handlers.broadcast_message.static_text import broadcast_command

from tgbot.handlers.utils.filters import TimeFilter
from tgbot.handlers.utils import files, error
from tgbot.handlers.onboarding.handlers import (
    RegistrationStates,
    command_start,
    check_code_handler,
    check_email_handler, is_player_in_game_handler, is_met_handler, command_game
)
from tgbot.handlers.onboarding import registration as onboarding_registration
from tgbot.handlers.onboarding import coffee
from tgbot.handlers.broadcast_message import handlers as broadcast_handlers
from tgbot.handlers.utils.cancel import cancel
from tgbot.main import bot


def setup_dispatcher(dp):
    """
    Добавление обработчиков событий из Telegram
    """
    # start and registration
    dp.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("start", command_start)],
            states={
                RegistrationStates.CHECK_EMAIL: [MessageHandler(Filters.text & ~Filters.command, check_email_handler)],
                RegistrationStates.CHECK_CODE: [MessageHandler(Filters.text & ~Filters.command, check_code_handler)],
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )
    )
    dp.add_handler(CommandHandler("game", command_game))
    dp.add_handler(
        MessageHandler(
            filters=TimeFilter(time_start=time(hour=9), time_end=time(hour=9, minute=15), weekday=0),
            callback=is_player_in_game_handler,
        )
    )
    dp.add_handler(
        ConversationHandler(
            entry_points=[
                MessageHandler(
                    filters=TimeFilter(time_start=time(hour=17), weekday=4),
                    callback=is_met_handler,
                )
            ],
            states={
                RegistrationStates.CHECK_EMAIL: [MessageHandler(Filters.text & ~Filters.command, check_email_handler)],
                RegistrationStates.CHECK_CODE: [MessageHandler(Filters.text & ~Filters.command, check_code_handler)],
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )
    )

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
