from celery.utils.log import get_task_logger
from telegram.ext import ConversationHandler

logger = get_task_logger(__name__)


def cancel(update, _):
    user = update.message.from_user
    logger.info("Пользователь %s отменил диалог.", user.first_name)
    return ConversationHandler.END
