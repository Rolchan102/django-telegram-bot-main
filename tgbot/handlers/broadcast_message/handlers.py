import re

import telegram
from telegram import Update
from telegram.ext import CallbackContext

from dtb.settings import DEBUG
from .manage_data import CONFIRM_DECLINE_BROADCAST, CONFIRM_BROADCAST
from .keyboards import keyboard_confirm_decline_broadcasting
from .static_text import broadcast_command, broadcast_wrong_format, broadcast_no_access, error_with_html, \
    message_is_sent, declined_message_broadcasting
from users.models import User
from users.tasks import broadcast_message


def broadcast_command_with_message(update: Update, context: CallbackContext):
    """Введите /broadcast <some_text>. Затем проверьте свое сообщение в формате HTML и транслируйте его пользователям."""
    u = User.get_user(update, context)

    if not u.is_admin:
        update.message.reply_text(
            text=broadcast_no_access,
        )
    else:
        if update.message.text == broadcast_command:
            # только пользовательская команда без текста для сообщения.
            update.message.reply_text(
                text=broadcast_wrong_format,
                parse_mode=telegram.ParseMode.HTML,
            )
            return

        text = f"{update.message.text.replace(f'{broadcast_command} ', '')}"
        markup = keyboard_confirm_decline_broadcasting()

        try:
            update.message.reply_text(
                text=text,
                parse_mode=telegram.ParseMode.HTML,
                reply_markup=markup,
            )
        except telegram.error.BadRequest as e:
            update.message.reply_text(
                text=error_with_html.format(reason=e),
                parse_mode=telegram.ParseMode.HTML,
            )


def broadcast_decision_handler(update: Update, context: CallbackContext) -> None:
    # callback_data: CONFIRM_DECLINE_BROADCAST переменную из manage_data.py
    """ Введен /broadcast <some_text>.
        Показывает текст в стиле HTML с двумя кнопками:
        Подтвердить и Отменить
    """
    broadcast_decision = update.callback_query.data[len(CONFIRM_DECLINE_BROADCAST):]

    entities_for_celery = update.callback_query.message.to_dict().get('entities')
    entities, text = update.callback_query.message.entities, update.callback_query.message.text

    if broadcast_decision == CONFIRM_BROADCAST:
        admin_text = message_is_sent
        user_ids = list(User.objects.all().values_list('user_id', flat=True))

        if DEBUG:
            broadcast_message(
                user_ids=user_ids,
                text=text,
                entities=entities_for_celery,
            )
        else:
            # send in async mode via celery
            broadcast_message.delay(
                user_ids=user_ids,
                text=text,
                entities=entities_for_celery,
            )
    else:
        context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text=declined_message_broadcasting,
        )
        admin_text = text

    context.bot.edit_message_text(
        text=admin_text,
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        entities=None if broadcast_decision == CONFIRM_BROADCAST else entities,
    )
