import os
from celery import Celery

# установить модуль настроек Django по умолчанию для программы 'celery'.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dtb.settings')

app = Celery('dtb')

# Использование здесь строки означает,
# что рабочему процессу не нужно сериализовать объект конфигурации в дочерние процессы.
# - namespace='CELERY' означает, что все ключи конфигурации,
# связанные с celery, должны иметь префикс `CELERY_`.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Загрузить модули задач из всех зарегистрированных конфигураций приложения Django.
app.autodiscover_tasks()
app.conf.enable_utc = False

    