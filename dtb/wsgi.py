"""
Конфигурация WSGI для проекта dtb.

Она использует WSGI вызовы как переменную уровня модуля с именем ``приложение``.

Дополнительные сведения об этом файле по ссылке:
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dtb.settings')

application = get_wsgi_application()
