from telegram import Update
from telegram.ext import CallbackContext
import random
import string
import time
import smtplib
import re
from tgbot.handlers.onboarding import static_text
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

ALLOWED_DOMAINS = ['syssoft.ru']
ACTIVE_EMAILS = {'a.novoseltsev@syssoft.ru': 'active', 'askerov@syssoft.ru': 'inactive'}
user_email = {}
codes = {}
times = {}


def start(update: Update, context: CallbackContext) -> None:
    # укажите свой адрес электронной почты
    update.message.reply_text(text=static_text.registration_message)


def is_valid_email(email):
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))


def check_email(update: Update, context: CallbackContext) -> None:
    global user_email, codes, times
    user_email = update.message.text.lower()
    # Check if the message contains a valid email address
    if not is_valid_email(user_email):
        # Неверный адрес электронной почты
        update.message.reply_text(text=static_text.invalid_email)
        return

    user_domain = user_email.split("@")[-1]

    # Check if the domain is allowed for registration
    if user_domain not in ALLOWED_DOMAINS:
        # Домен не разрешен для регистрации!
        update.message.reply_text(text=static_text.domain_message)
        return

    # Check if the email is active
    if user_email in ACTIVE_EMAILS and ACTIVE_EMAILS[user_email] == "active":
        # По вашему адресу отправлен код подтверждения
        send_email(user_email)
        update.message.reply_text(text=static_text.code_message)
    else:
        # Адрес не активен!
        update.message.reply_text(text=static_text.email_message)


def send_email(user_email):
    global codes, times
    # Генерируем случайный код подтверждения
    code = ''.join(random.choice(string.digits) for _ in range(6))
    # Запоминаем код в словаре codes
    codes[user_email] = code
    # Запоминаем время отправки кода в словаре times
    times[user_email] = time.time()

    smtp_username = "@gmail.com"
    smtp_password = ""

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
        update.message.reply_text(text=static_text.result_success)
    else:
        # Неверный код подтверждения
        update.message.reply_text(text=static_text.code_wrong)
