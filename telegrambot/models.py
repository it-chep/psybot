import os
from django.db import models

from psybot import settings

# Create your models here.

User = settings.AUTH_USER_MODEL


class Profile(models.Model):
    tg_id = models.BigIntegerField(
        verbose_name='tg_id'

    )

    name = models.CharField(
        verbose_name='Имя пользователя',
        max_length=225,
    )

    username = models.CharField(
        verbose_name='Username пользователя',
        max_length=225,
        null=True
    )

    phone = models.CharField(
        'Номер телефона',
        max_length=18,
        # unique=True
        null=True
    )

    job_place = models.CharField(
        'Местро работы',
        max_length=50,
        null=True
    )

    job_title = models.CharField(
        "Должность",
        max_length=50,
        null=True
    )

    state = models.CharField(
        max_length=255,
        verbose_name='Состояние пользователя, где находится',
        null=True
    )

    last_used_card = models.CharField(
        max_length=255,
        verbose_name='Последняя карточка, которую тренил',
        null=True,
    )

    level = models.IntegerField(
        verbose_name="Уровень",
        null=True
    )

    expirience = models.IntegerField(
        verbose_name="Пройденные карточки",
        null=True
    )
    # сумма ответов
    quality = models.FloatField(
        verbose_name="Качество прохождения",
        null=True
    )

    user_status = models.ForeignKey(
        'Status',
        on_delete=models.SET_DEFAULT,
        default=1
    )

    def __str__(self):
        return f'#{self.tg_id} {self.name}'

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
        ordering = ["name"]


class Status(models.Model):
    name = models.CharField("Статус", max_length=100, db_index=True)
    status_value = models.IntegerField("Вес статуса")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'
        ordering = ["status_value"]


class Messages(models.Model):
    profile = models.ForeignKey(
        to='telegrambot.Profile',
        verbose_name='Профиль',
        on_delete=models.PROTECT,
    )

    message_text = models.TextField(
        verbose_name='Сообщение пользователя'
    )

    sending_time = models.DateTimeField(
        verbose_name='Время отправки',
        auto_now_add=True
    )

    def __str__(self):
        return f'Сообщение {self.pk} от {self.profile}'

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'


class Card(models.Model):

    name = models.TextField('Название')
    right_answer_1 = models.TextField('Правильный ответ первый вопрос')
    answers_1 = models.TextField('Ответы первый')
    right_answer_2 = models.TextField('Правильный ответ второй вопрос')
    answers_2 = models.TextField('Ответы второй')
    schemas = models.TextField('Схема ответа 2')
    right_answer_3 = models.TextField('Правильный ответ третий вопрос')
    answers_3 = models.TextField('Ответы третий')

    class Meta:
        verbose_name = 'Карточка'
        verbose_name_plural = 'Карточки'


def get_upload_path(instance, filename):
    return os.path.join(instance.name, filename)


class PhotoForCards(models.Model):
    name = models.CharField("Название фото", max_length=255)
    question = models.ImageField("Вопросительное фото", upload_to=get_upload_path,)
    good = models.ImageField("Веселое фото", upload_to=get_upload_path, )
    bad = models.ImageField("Грустное фото", upload_to=get_upload_path, )

    class Meta:
        verbose_name = 'Фото для карточек'


class Feedback(models.Model):

    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Отзывы'


class Workers(models.Model):
    name = models.CharField('ФИ(О)', max_length=100)
    phone_number = models.CharField('Номер телефона', max_length=18)
    job_place = models.CharField('Место работы', max_length=50)
    job_title = models.CharField('Должность', max_length=50)

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
        db_table = 'workers'
        ordering = ["name"]


class WorkersDooble(models.Model):
    name = models.CharField('ФИ(О)', max_length=100)
    phone_number = models.CharField('Номер телефона', max_length=18)
    job_place = models.CharField('Место работы', max_length=50)
    job_title = models.CharField('Должность', max_length=50)

    class Meta:
        managed = False
        db_table = 'workers_dooble'


class Mood(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    date = models.DateField('Дата', auto_now_add=True)
    grade = models.IntegerField('Оценка')

    def __str__(self):
        return f'{self.date} настроение на {self.grade}'

    class Meta:
        verbose_name = 'Настроение'


class LastMoodNotice(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    last_reminder_date = models.DateField(auto_now=True)

    class Meta:
        verbose_name = 'Последнее настроение'

