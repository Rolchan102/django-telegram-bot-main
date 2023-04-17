from datetime import timedelta

from django.utils.timezone import now
from telegram import Update
from telegram.ext import CallbackContext

from tgbot.handlers.admin import static_text
from tgbot.handlers.admin.utils import _get_csv_from_qs_values
from tgbot.handlers.utils.info import send_typing_action
from users.models import User


def admin(update: Update, context: CallbackContext) -> None:
    """Проверяет, является ли пользователь администратором"""
    u = User.get_user(update, context)
    if not u.is_admin:
        update.message.reply_text(static_text.only_for_admins)
        return
    update.message.reply_text(static_text.secret_admin_commands)


def stats(update: Update, context: CallbackContext) -> None:
    """Статистика бота - кол-во пользователей и кол-во пользователей, обновивших профиль"""
    u = User.get_user(update, context)
    if not u.is_admin:
        update.message.reply_text(static_text.only_for_admins)
        return

    text = static_text.users_amount_stat.format(
        user_count=User.objects.count(),  # count может быть неэффективным, если пользователей много.
        active_24=User.objects.filter(updated_at__gte=now() - timedelta(hours=24)).count()
    )

    update.message.reply_text(
        text,
        parse_mode='HTML',
        disable_web_page_preview=True,
    )


@send_typing_action
def export_users(update: Update, context: CallbackContext) -> None:
    """Экспортирует список пользователей в CSV-файл и отправляет его"""
    u = User.get_user(update, context)
    if not u.is_admin:
        update.message.reply_text(static_text.only_for_admins)
        return

    # в аргументе значений вы можете указать, какие поля должны быть возвращены в csv-файле
    users = User.objects.all().values()
    csv_users = _get_csv_from_qs_values(users)
    context.bot.send_document(chat_id=u.user_id, document=csv_users)
