from enum import IntFlag, auto

from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from tgbot.handlers.onboarding import static_text, registration


class RegistrationStates(IntFlag):
    CHECK_EMAIL = auto()
    CHECK_CODE = auto()


def command_start(update: Update, context: CallbackContext):
    text = static_text.registration_message.format(
        first_name=update.message.from_user.first_name
    )
    update.message.reply_text(text=text)
    return RegistrationStates.CHECK_EMAIL


def check_email_handler(update: Update, context: CallbackContext):
    """
    Validate email and send code
    """
    try:
        registration.check_email(update, context)
    except registration.HandledError:
        return ConversationHandler.END

    return RegistrationStates.CHECK_CODE


def check_code_handler(update: Update, context: CallbackContext):
    """
    Validate code and create User
    """
    try:
        registration.check_code(update, context)
    except registration.HandledError:
        return RegistrationStates.CHECK_CODE

    return ConversationHandler.END
