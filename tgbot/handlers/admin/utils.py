import io
import csv

from datetime import datetime
from django.db.models import QuerySet
from typing import Dict


def _get_csv_from_qs_values(queryset: QuerySet[Dict], filename: str = 'users'):
    keys = queryset[0].keys()

    # csv-модуль может записывать данные только в буфер io.StringIO
    s = io.StringIO()
    dict_writer = csv.DictWriter(s, fieldnames=keys, encoding='utf-8')
    dict_writer.writeheader()
    dict_writer.writerows(queryset)
    s.seek(0)

    # библиотека python-telegram-bot отправляет файлы только из буфера io.BytesIO
    # we need to convert StringIO to BytesIO
    buf = io.BytesIO()

    # извлекаем csv-строку, конвертируем в байты и записываем в буфер
    buf.write(s.getvalue().encode())
    buf.seek(0)

    # устанавливаем имя и расширение файла
    buf.name = f"{filename}__{datetime.now().strftime('%Y.%m.%d.%H.%M')}.csv"

    return buf
