from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, MessageHandler, Filters

from tgbot.handlers.onboarding import static_text
from tgbot.handlers.onboarding import registration

ALLOWED_DOMAINS = ['syssoft.ru']
ACTIVE_EMAILS = {'a.novoseltsev@syssoft.ru': 'active', 'askerov@syssoft.ru': 'inactive'}
user_email = {}
codes = {}
times = {}


def command_start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    first_name = user.first_name
    text = static_text.registration_message.format(first_name=first_name)
    update.message.reply_text(text=text)

    # Ask the user to enter their email address
    registration.check_email(update, context)

    # Change conversation state to ENTER_EMAIL
    registration.check_code(update, context)
