from telegram import Update
from telegram.ext import CallbackContext
import random
import string
import time
import smtplib
import re
from users.models import User
from tgbot.handlers.onboarding import static_text
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

ALLOWED_DOMAINS = ['syssoft.ru']
ACTIVE_EMAILS = {'a.novoseltsev@syssoft.ru': 'active', 'askerov@syssoft.ru': 'inactive'}
user_email = {}
codes = {}
times = {}


def is_valid_email(email):
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))


def check_email(update, context):
    email = context.user_data.get('email')
    codes = context.user_data.setdefault('codes', {})
    times = context.user_data.setdefault('times', {})

    # Check if the domain is allowed for registration
    user_domain = email.split("@")[-1]
    if user_domain not in ALLOWED_DOMAINS:
        # Домен не разрешен для регистрации!
        update.message.reply_text(text=static_text.domain_message)
        return

    # Check if the email is active
    if email in ACTIVE_EMAILS and ACTIVE_EMAILS[email] == "active":
        # По вашему адресу отправлен код подтверждения
        send_email(email, codes, times)
        update.message.reply_text(text=static_text.code_message)
    else:
        # Адрес не активен!
        update.message.reply_text(text=static_text.email_message)


def send_email(email, codes, times):
    # Генерируем случайный код подтверждения
    code = ''.join(random.choice(string.digits) for _ in range(6))
    # Запоминаем код в словаре codes
    codes[email] = code
    # Запоминаем время отправки кода в словаре times
    times[email] = time.time()

    smtp_username = "novosltsev2010@gmail.com"
    smtp_password = "uvxhzvmfpvdhkhoo"

    try:
        smtp_conn = smtplib.SMTP('smtp.gmail.com: 587')
        smtp_conn.starttls()
        smtp_conn.login(smtp_username, smtp_password)

        message = MIMEMultipart()
        message['From'] = smtp_username
        message['To'] = user_email
        message['Subject'] = 'Код подтверждения'

        # Отправляем код на почту пользователя
        code_message = f"Код подтверждения: {code}. Введите его в боте для подтверждения регистрации."
        message.attach(MIMEText(code_message, 'plain'))
        smtp_conn.sendmail(smtp_username, user_email, message.as_string())
    except Exception as e:
        print(f"Error sending email: {e}")
    finally:
        smtp_conn.quit()


def check_code(update: Update, context: CallbackContext) -> None:
    global user_email, codes, times
    message_text = update.message.text

    if user_email not in times:
        # Нет записи о времени отправки кода подтверждения. Попробуйте еще раз.
        update.message.reply_text(text=static_text.code_unsuccess_1)
        return
    if times[user_email] + 1200 < time.time():
        # Время жизни кода (20 минут) истекло. Попробуйте еще раз
        update.message.reply_text(text=static_text.code_unsuccess_2)
        return
    if codes[user_email] == message_text:
        # Поздравляем! Вы зарегистрированы
        user = User(email=user_email)
        user.save()
        update.message.reply_text(text=static_text.result_success)
    else:
        # Неверный код подтверждения
        update.message.reply_text(text=static_text.code_wrong)
