"""
    Celery tasks. Some of them will be launched periodically from admin panel via django-celery-beat
"""

import time
from typing import Union, List, Optional, Dict
from random import randint

import telegram

from dtb.celery import app
from celery.utils.log import get_task_logger
from tgbot.handlers.broadcast_message.utils import (
    send_one_message,
    from_celery_entities_to_entities,
    from_celery_markup_to_markup,
)
from tgbot.handlers.onboarding import static_text
from users.models import User, UserMeeting

logger = get_task_logger(__name__)


@app.task(ignore_result=True)
def broadcast_message(
    user_ids: List[Union[str, int]],
    text: str,
    entities: Optional[List[Dict]] = None,
    reply_markup: Optional[List[List[Dict]]] = None,
    sleep_between: float = 0.4,
    parse_mode: Optional[str] = 'HTML',
) -> None:
    """ It's used to broadcast message to big amount of users """
    logger.info(f"Going to send message: '{text}' to {len(user_ids)} users")

    entities_ = from_celery_entities_to_entities(entities)
    reply_markup_ = from_celery_markup_to_markup(reply_markup)
    for user_id in user_ids:
        try:
            send_one_message(
                user_id=user_id,
                text=text,
                entities=entities_,
                parse_mode=parse_mode,
                reply_markup=reply_markup_,
            )
            logger.info(f"Broadcast message was sent to {user_id}")
        except Exception as e:
            logger.error(f"Failed to send message to {user_id}, reason: {e}")
        time.sleep(max(sleep_between, 0.1))

    logger.info("Broadcast finished!")


@app.task
def pre_game_survey():
    players_via_city = {}
    for user in User.objects.filter(activity='game'):
        players_via_city[user.city] = players_via_city.get(user.city, []) + [user]

    previous_meetings = [(met.user_1_id, met.user_2_id) for met in UserMeeting.objects.all()]
    new_meetings = []

    for city_users in players_via_city.values():
        while len(city_users) > 1:
            user_1 = city_users.pop(0)
            for user_2_index in range(len(city_users)):
                if (
                    (user_1.id, city_users[user_2_index].id) not in previous_meetings
                    or (city_users[user_2_index].id, user_1.id) not in previous_meetings
                ):
                    user_2 = city_users.pop(user_2_index)
                    break
            else:
                user_2 = city_users.pop(randint(0, len(city_users)))

            new_meetings.append(UserMeeting(user_1=user_1, user_2=user_2))
            send_one_message(
                user_1.user_id,
                text=static_text.start_game_message.format(fio=user_2.username, email=user_2.user_email)
            )
            send_one_message(
                user_2.user_id,
                text=static_text.start_game_message.format(fio=user_1.username, email=user_1.user_email)
            )

        if len(city_users) == 1:
            admin = User.admins.first()
            new_meetings.append(UserMeeting(user_1=city_users[0], user_2=admin))
            send_one_message(
                city_users[0].user_id,
                text=static_text.start_game_message.format(fio=admin.username, email=admin.user_email)
            )
            send_one_message(
                admin.user_id,
                text=static_text.start_game_message.format(fio=city_users[0].username, email=city_users[0].user_email)
            )

    UserMeeting.objects.bulk_create(new_meetings, batch_size=500)


@app.task
def start_game():
    users = User.objects.filter(activity='game')
    for user in users:
        send_one_message(
            user.user_id,
            text=static_text.start_game_message,
        )
    users.objects.update(activity='pause')


@app.task
def post_game_survey():
    users = User.objects.filter(activity='game')
    for user in users:
        send_one_message(
            user.user_id,
            text=static_text.end_game_message1,
        )
    users.objects.update(activity='pause')
