import json
import logging
from django.views import View
from django.http import JsonResponse
from telegram import Update

from dtb.celery import app
from dtb.settings import DEBUG
from tgbot.dispatcher import dispatcher
from tgbot.main import bot

logger = logging.getLogger(__name__)


@app.task(ignore_result=True)
def process_telegram_event(update_json):
    update = Update.de_json(update_json, bot)
    dispatcher.process_update(update)


def index(request):
    return JsonResponse({"ошибка": "Неверная ссылка!"})


class TelegramBotWebhookView(View):
    # ВНИМАНИЕ: в случае неудачи - Telegram webhook будет доставлен снова.
    # Можно исправить с помощью асинхронного выполнения задачи celery.
    def post(self, request, *args, **kwargs):
        if DEBUG:
            process_telegram_event(json.loads(request.body))
        else:
            # Обработка Telegram-события в обработчике Celery (асинхронно)
            # Не забудьте запустить его и Redis (брокера сообщений для Celery)!
            # Локально, Вы можете запускать все эти сервисы через docker-compose.yml
            process_telegram_event.delay(json.loads(request.body))

        # к примеру: удалить кнопки, введя событие
        return JsonResponse({"ok": "POST-запрос обработан"})

    def get(self, request, *args, **kwargs):  # for debug
        return JsonResponse({"ok": "Запрос получен! Но ничего не сделано"})
