from datetime import timedelta

from django.utils import timezone
from telegram import Update
from telegram.ext import CallbackContext
import random
import string
import smtplib
import re

from users.models import User, Email, EmailCode
from tgbot.handlers.onboarding import static_text
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings


class HandledError(Exception):
    pass


def is_valid_email(email):
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))


def check_email(update: Update, context):
    email = update.message.text

    # Validate email
    if '@' not in email:
        update.message.reply_text(text=static_text.invalid_email)
        raise HandledError

    # Домен не разрешен для регистрации!
    user_domain = email.split("@")[-1]
    if user_domain not in settings.ALLOWED_DOMAINS:
        update.message.reply_text(text=static_text.domain_message)
        raise HandledError

    # Адрес не активен!
    if not Email.objects.filter(email=email, is_active=True).exists():
        update.message.reply_text(text=static_text.email_message)
        raise HandledError

    # По вашему адресу отправлен код подтверждения
    context.user_data['email'] = email
    send_email(email)
    update.message.reply_text(text=static_text.code_message)


def send_email(email: str):
    # Генерируем случайный код подтверждения
    code = ''.join(random.choice(string.digits) for _ in range(6))
    # Сохраниение кода активации
    EmailCode.objects.create(
        email=email,
        code=code,
    )
    smtp_username = "@gmail.com"
    smtp_password = ""

    try:
        smtp_conn = smtplib.SMTP('smtp.gmail.com: 587')
        smtp_conn.starttls()
        smtp_conn.login(smtp_username, smtp_password)

        message = MIMEMultipart()
        message['From'] = smtp_username
        message['To'] = email
        message['Subject'] = 'Код подтверждения'

        # Отправляем код на почту пользователя
        code_message = f"Код подтверждения: {code}. Введите его в боте для подтверждения регистрации."
        message.attach(MIMEText(code_message, 'plain'))
        smtp_conn.sendmail(smtp_username, email, message.as_string())
    except Exception as e:
        print(f"Error sending email: {e}")
    finally:
        smtp_conn.quit()


def check_code(update: Update, context: CallbackContext) -> None:
    email_code_object = EmailCode.objects.filter(email=context.user_data['email'], is_used=False).last()

    if not email_code_object:
        # Нет записи об отправке кода подтверждения. Попробуйте еще раз.
        update.message.reply_text(text=static_text.code_unsuccess_1)
        raise HandledError
    if email_code_object.created_at < timezone.now() - timedelta(minutes=20):
        # Время жизни кода (20 минут) истекло. Попробуйте еще раз
        update.message.reply_text(text=static_text.code_unsuccess_2)
        raise HandledError
    if email_code_object.code != update.message.text:
        # Неверный код подтверждения
        update.message.reply_text(text=static_text.code_wrong)
        raise HandledError

    # Поздравляем! Вы зарегистрированы
    email_code_object.is_used = True
    email_code_object.save()

    User.objects.create(user_email=email_code_object.email, user_id=update.message.from_user.id)
    update.message.reply_text(text=static_text.result_success)
