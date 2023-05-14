from enum import IntFlag, auto

from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from tgbot.handlers.onboarding import static_text
from tgbot.handlers.onboarding import registration


class RegistrationStates(IntFlag):
    CHECK_EMAIL = auto()
    CHECK_CODE = auto()


def command_start(update: Update, context: CallbackContext) -> int:
    text = static_text.registration_message.format(
        first_name=update.message.from_user.first_name
    )
    update.message.reply_text(text=text)
    return RegistrationStates.CHECK_EMAIL


def check_email_handler(update: Update, context: CallbackContext) -> int:
    # Ask the user to enter their email address
    registration.check_email(update, context)
    return RegistrationStates.CHECK_CODE


def check_code_handler(update: Update, context: CallbackContext) -> None:
    # Change conversation state to ENTER_EMAIL
    registration.check_code(update, context)
    return ConversationHandler.END
