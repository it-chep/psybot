import os
import pickle
import time

from psybot.celery import app
from celery import shared_task
import asyncio

from psybot import settings
from telegrambot.utils.utils import Utils
from users.utils import clean_token


# Подключение к многопоточной штуке
class Async:

    util = Utils

    @staticmethod
    @shared_task
    async def update_db(path, ):
        Async.util.create_table()
        Async.util.insert_data_from_json(path)
        registration = Async.util.repository.ram_cache.get(key='registration')

        while True:
            if not registration or registration == 0:
                Async.util.repository.ram_cache.set(key='registration', value=-100)

                Async.util.delete_table()
                Async.util.rename_table()

                Async.util.repository.ram_cache.delete(key='registration')
                break
            await asyncio.sleep(60)

    @staticmethod
    def excel_to_json(path):
        Async.util.excel_to_json(os.path.join(settings.BASE_DIR, 'tables', path))


@app.task
def token_delay(pk):

    print('[+]CELERY START')
    time.sleep(400)
    clean_token(pk)
    print('[+]CELERY END')
    return {'status': 'success'}


