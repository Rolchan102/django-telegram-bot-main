"""
Конфигурация ASGI для проекта dtb.

Она использует ASGI вызовы как переменную уровня модуля с именем ``приложение``.

Дополнительные сведения об этом файле по ссылке:
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dtb.settings')

application = get_asgi_application()
