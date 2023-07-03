# Generated by Django 4.1.5 on 2023-04-02 16:02

from django.db import migrations, models
import django.db.models.deletion
import telegrambot.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WorkersDooble',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='ФИ(О)')),
                ('phone_number', models.CharField(max_length=18, verbose_name='Номер телефона')),
                ('job_place', models.CharField(max_length=50, verbose_name='Место работы')),
                ('job_title', models.CharField(max_length=50, verbose_name='Должность')),
            ],
            options={
                'db_table': 'workers_dooble',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(verbose_name='Название')),
                ('right_answer_1', models.TextField(verbose_name='Правильный ответ первый вопрос')),
                ('answers_1', models.TextField(verbose_name='Ответы первый')),
                ('right_answer_2', models.TextField(verbose_name='Правильный ответ второй вопрос')),
                ('answers_2', models.TextField(verbose_name='Ответы второй')),
                ('schemas', models.TextField(verbose_name='Схема ответа 2')),
                ('right_answer_3', models.TextField(verbose_name='Правильный ответ третий вопрос')),
                ('answers_3', models.TextField(verbose_name='Ответы третий')),
            ],
            options={
                'verbose_name': 'Карточка',
                'verbose_name_plural': 'Карточки',
            },
        ),
        migrations.CreateModel(
            name='PhotoForCards',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название фото')),
                ('question', models.ImageField(upload_to=telegrambot.models.get_upload_path, verbose_name='Вопросительное фото')),
                ('good', models.ImageField(upload_to=telegrambot.models.get_upload_path, verbose_name='Веселое фото')),
                ('bad', models.ImageField(upload_to=telegrambot.models.get_upload_path, verbose_name='Грустное фото')),
            ],
            options={
                'verbose_name': 'Фото для карточек',
            },
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=100, verbose_name='Статус')),
                ('status_value', models.IntegerField(verbose_name='Вес статуса')),
            ],
            options={
                'verbose_name': 'Статус',
                'verbose_name_plural': 'Статусы',
                'ordering': ['status_value'],
            },
        ),
        migrations.CreateModel(
            name='Workers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='ФИ(О)')),
                ('phone_number', models.CharField(max_length=18, verbose_name='Номер телефона')),
                ('job_place', models.CharField(max_length=50, verbose_name='Место работы')),
                ('job_title', models.CharField(max_length=50, verbose_name='Должность')),
            ],
            options={
                'verbose_name': 'Сотрудник',
                'verbose_name_plural': 'Сотрудники',
                'db_table': 'workers',
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tg_id', models.IntegerField(verbose_name='tg_id')),
                ('name', models.CharField(max_length=225, verbose_name='Имя пользователя')),
                ('username', models.CharField(max_length=225, null=True, verbose_name='Username пользователя')),
                ('phone', models.CharField(max_length=18, null=True, verbose_name='Номер телефона')),
                ('job_place', models.CharField(max_length=50, null=True, verbose_name='Местро работы')),
                ('job_title', models.CharField(max_length=50, null=True, verbose_name='Должность')),
                ('state', models.CharField(max_length=255, null=True, verbose_name='Состояние пользователя, где находится')),
                ('last_used_card', models.CharField(max_length=255, null=True, verbose_name='Последняя карточка, которую тренил')),
                ('level', models.IntegerField(null=True, verbose_name='Уровень')),
                ('expirience', models.IntegerField(null=True, verbose_name='Пройденные карточки')),
                ('quality', models.FloatField(null=True, verbose_name='Качество прохождения')),
                ('user_status', models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, to='telegrambot.status')),
            ],
            options={
                'verbose_name': 'Профиль',
                'verbose_name_plural': 'Профили',
            },
        ),
        migrations.CreateModel(
            name='Messages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message_text', models.TextField(verbose_name='Сообщение пользователя')),
                ('sending_time', models.DateTimeField(auto_now_add=True, verbose_name='Время отправки')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='telegrambot.profile', verbose_name='Профиль')),
            ],
            options={
                'verbose_name': 'Сообщение',
                'verbose_name_plural': 'Сообщения',
            },
        ),
    ]