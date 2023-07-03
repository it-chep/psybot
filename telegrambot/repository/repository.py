import json

from django.db import connection

from telegrambot.models import *
from telegrambot.cache import RedisCache


class Repository:
    profiles = Profile
    statuses = Status
    messages = Messages
    cards = Card
    photos_for_cards = PhotoForCards
    workers = Workers
    ram_cache = RedisCache(None, {})
    red_is = RedisCache.red_is
    feedback = Feedback
    mood = Mood
    last_day_mood = LastMoodNotice


class SQL:

    @staticmethod
    def create_table():
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE workers_dooble (
                    id serial PRIMARY KEY,
                    name varchar(100),
                    phone_number varchar(18),
                    job_place varchar(50),
                    job_title varchar(50)
                );
            """)

    @staticmethod
    def insert_data_from_json(path):
        with open(path) as f:
            data = json.load(f)
        with connection.cursor() as cursor:
            for worker in data:
                name = worker['Фамилия'] + ' ' + worker['Имя']
                cursor.execute("""
                    INSERT INTO workers_dooble (name, phone_number, job_place, job_title)
                    VALUES (%s, %s, %s, %s);
                """, (name, worker['Телефон'][1:], worker['Ресторан'], worker['Должность']))

    @staticmethod
    def delete_table():
        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE workers_dooble;")

    @staticmethod
    def rename_table():
        with connection.cursor() as cursor:
            cursor.execute("ALTER TABLE workers_dooble RENAME TO workers;")

