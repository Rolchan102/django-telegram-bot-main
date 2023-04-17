from __future__ import annotations

from typing import Union, Optional, Tuple

from django.db import models
from django.db.models import QuerySet, Manager
from telegram import Update
from telegram.ext import CallbackContext

from tgbot.handlers.utils.info import extract_user_data_from_update
from utils.models import CreateUpdateTracker, nb, CreateTracker, GetOrNoneManager


class AdminUserManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_admin=True)


class User(CreateUpdateTracker):
    """Содержит данные о пользователе"""
    user_id = models.PositiveBigIntegerField(primary_key=True)  # telegram_id
    username = models.CharField(max_length=32, **nb)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256, **nb)
    email = models.CharField(max_length=256, **nb)
    CITY_CHOICES = (
        ('Moscow', 'Москва'),
        ('Volgograd', 'Волгоград'),
    )
    city = models.CharField(max_length=256, choices=CITY_CHOICES, **nb)
    MAIL_STATUS_CHOICES = (
        ('active', 'Активна'),
        ('inactive', 'Отключена'),
    )
    mail_status = models.CharField(max_length=256, choices=MAIL_STATUS_CHOICES, **nb)
    ACTIVITY_CHOICES = (
        ('registered', 'Зарегистрирован'),
        ('game', 'Играет'),
        ('pause', 'Пауза'),
        ('removed', 'Удален'),
    )
    activity = models.CharField(max_length=256, choices=ACTIVITY_CHOICES, **nb)
    language_code = models.CharField(max_length=8, help_text="Язык пользователя Telegram", **nb)
    deep_link = models.CharField(max_length=64, **nb)

    is_blocked_bot = models.BooleanField(default=False)

    is_admin = models.BooleanField(default=False)

    objects = GetOrNoneManager()  # user = User.objects.get_or_none(user_id=<some_id>)
    admins = AdminUserManager()  # User.admins.all()

    def __str__(self):
        return f'@{self.username}' if self.username is not None else f'{self.user_id}'

    @classmethod
    def get_user_and_created(cls, update: Update, context: CallbackContext) -> Tuple[User, bool]:
        """Проверяет, был ли пользователь только что создан, или он уже существовал"""
        data = extract_user_data_from_update(update)
        u, created = cls.objects.update_or_create(user_id=data["user_id"], defaults=data)

        if created:
            # Save deep_link to User model
            if context is not None and context.args is not None and len(context.args) > 0:
                payload = context.args[0]
                if str(payload).strip() != str(data["user_id"]).strip():  # you can't invite yourself
                    u.deep_link = payload
                    u.save()

        return u, created

    @classmethod
    def get_user(cls, update: Update, context: CallbackContext) -> User:
        u, _ = cls.get_user_and_created(update, context)
        return u

    @classmethod
    def get_user_by_username_or_user_id(cls, username_or_user_id: Union[str, int]) -> Optional[User]:
        """Поиск пользователя в БД, возвращает User или None, если не найден"""
        username = str(username_or_user_id).replace("@", "").strip().lower()
        if username.isdigit():  # user_id
            return cls.objects.filter(user_id=int(username)).first()
        return cls.objects.filter(username__iexact=username).first()

    @property
    def invited_users(self) -> QuerySet[User]:
        return User.objects.filter(deep_link=str(self.user_id), created_at__gt=self.created_at)

    @property
    def tg_str(self) -> str:
        if self.username:
            return f'@{self.username}'
        return f"{self.first_name} {self.last_name}" if self.last_name else f"{self.first_name}"

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


# class Location(CreateTracker):
#     """Содержит данные о географическом местоположении"""
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     latitude = models.FloatField()
#     longitude = models.FloatField()
#
#     objects = GetOrNoneManager()
#
#     def __str__(self):
#         return f"user: {self.user}, created at {self.created_at.strftime('(%H:%M, %d %B %Y)')}"
#
#     class Meta:
#         verbose_name = 'Местоположение'
#         verbose_name_plural = 'Местоположение'


class UserActionLog(CreateUpdateTracker):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=128)
    text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"user: {self.user}, made: {self.action}, created at {self.created_at.strftime('(%H:%M, %d %B %Y)')}"
