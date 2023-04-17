from django.core.exceptions import ObjectDoesNotExist
from django.db import models


nb = dict(null=True, blank=True)


class CreateTracker(models.Model):
    """Заполняет поле текущей датой и временем при создании объекта"""
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Создан')

    class Meta:
        abstract = True
        ordering = ('-created_at',)


class CreateUpdateTracker(CreateTracker):
    """Обновляет поле текущей датой и временем при сохранении объекта"""
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Изменен')

    class Meta(CreateTracker.Meta):
        abstract = True


class GetOrNoneManager(models.Manager):
    """Возвращает none, если объект не создан, иначе экземпляр модели"""
    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except ObjectDoesNotExist:
            return None
