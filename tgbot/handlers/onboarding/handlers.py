import smtplib
import random
import string
import re
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from django.utils import timezone
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, MessageHandler, Filters

from tgbot.handlers.onboarding import static_text
from tgbot.handlers.utils.info import extract_user_data_from_update
from users.models import User
from tgbot.handlers.onboarding.keyboards import make_keyboard_for_start_command

allowed_domains = ['syssoft.ru']
admin_emails = {'a.novoseltsev@syssoft.ru': 'active', 'askerov@syssoft.ru': 'inactive'}
times = {}
# Define your states
USER_EMAIL, USER_CODE = range(2)


def start(update: Update, context: CallbackContext) -> int:
    u, created = User.get_user_and_created(update, context)
    """Send a message when the command /start is issued."""
    # Укажите свой адрес электронной почты
    update.message.reply_text(text=static_text.start_message.format(first_name=u.first_name),
                              reply_markup=make_keyboard_for_start_command())
    return USER_EMAIL


def send_email(user_email):
    # Генерируем случайный код подтверждения
    code = ''.join(random.choice(string.digits) for _ in range(6))
    # Запоминаем время отправки кода в словаре times
    code_sent_time = datetime.now()
    # Отправляем код на почту пользователя
    smtp_username = "@gmail.com"
    smtp_password = ""
    smtp_conn = smtplib.SMTP('smtp.gmail.com: 587')
    smtp_conn.starttls()
    smtp_conn.login(smtp_username, smtp_password)
    message = MIMEMultipart()
    message['From'] = smtp_username
    message['To'] = user_email
    message['Subject'] = 'Код подтверждения'
    code_message = f"Код подтверждения: {code}. Введите его в боте для подтверждения регистрации."
    message.attach(MIMEText(code_message, 'plain'))
    smtp_conn.sendmail(smtp_username, user_email, message.as_string())
    smtp_conn.quit()
    return code, code_sent_time


def check_email(update: Update, context: CallbackContext) -> int:
    """Check the email entered by the user."""
    email = update.message.text
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        # Неверный адрес электронной почты!
        update.message.reply_text(text=static_text.invalid_email)
        return USER_EMAIL
    email_domain = email.split('@')[-1]
    if email_domain not in allowed_domains:
        # Домен не разрешен для регистрации!
        update.message.reply_text(text=static_text.domain_message)
        return USER_EMAIL

    if email in admin_emails and admin_emails[email] == 'active':
        # Save the email in the user's context
        context.user_data['email'] = email
        # Generate a code and send it to the user
        code, code_sent_time = send_email(email)
        context.user_data['code'] = code
        context.user_data['code_sent_time'] = code_sent_time
        # По вашему адресу отправлен код подтверждения, проверьте почту и введите код
        update.message.reply_text(text=static_text.code_message)
        return USER_CODE
    else:
        # Домен не разрешен для регистрации!
        update.message.reply_text(text=static_text.domain_message)
        return USER_EMAIL


def check_code(update: Update, context: CallbackContext) -> int:
    """Validate the code entered by the user."""
    code = update.message.text
    expected_code = context.user_data['code']

    # Check if the code has expired
    code_sent_time = context.user_data.get('code_sent_time')
    if code_sent_time and datetime.now() - code_sent_time > timedelta(minutes=20):
        # Время жизни кода (20 минут) истекло. Попробуйте еще раз
        update.message.reply_text(text=static_text.code_unsuccess)
        return USER_EMAIL

    if code == expected_code:
        # Registration successful, save the email address in the database
        email = context.user_data['email']
        user = User.objects.create(email=email)
        user.save()
        # Поздравляем! Вы зарегистрированы.
        update.message.reply_text(text=static_text.result_success)
    else:
        # Неверный код подтверждения
        update.message.reply_text(text=static_text.code_wrong)
        return USER_CODE


def cancel(update: Update, context: CallbackContext) -> int:
    """Cancel the registration process."""
    update.message.reply_text('Регистрация отменена.')
    return ConversationHandler.END


# Define your ConversationHandler
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        USER_EMAIL: [MessageHandler(Filters.text & ~Filters.command, check_email)],
        USER_CODE: [MessageHandler(Filters.text & ~Filters.command, check_code)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)


def secret_level(update: Update, context: CallbackContext) -> None:
    # callback_data: SECRET_LEVEL_BUTTON variable from manage_data.py
    """Секретные функции админа"""
    user_id = extract_user_data_from_update(update)['user_id']
    text = static_text.unlock_secret_room.format(
        user_count=User.objects.count(),
        active_24=User.objects.filter(updated_at__gte=timezone.now() - datetime.timedelta(hours=24)).count()
    )

    context.bot.edit_message_text(
        text=text,
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
        parse_mode='HTML'
    )
