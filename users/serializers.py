import asyncio
import pickle
from abc import ABC
import random
import string
from asyncio import sleep
from telegrambot.async_work.async_work import token_delay

# from .utils import forgot_password
from django.core.mail import send_mail
from django.db.utils import ProgrammingError
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from telegrambot.repository.repository import Workers
from users.models import CustomUser
from .forms import SignUpForm


class RegistrationSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField()

    def validate(self, data):

        if CustomUser.objects.filter(phone_number__icontains=data['phone_number']).exists():
            raise serializers.ValidationError({'phone_number': 'not_unique'})

        try:
            Workers.objects.filter(phone_number__icontains=data['phone_number']).get()
        except Workers.DoesNotExist:
            raise serializers.ValidationError({'phone_number': 'invalid'})
        except ProgrammingError:
            raise serializers.ValidationError({'program': 'error'})

        print('[+][+]', data)

        return data

    def create(self, validated_data):
        phone_number = validated_data['phone_number']
        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=15))

        user_data = Workers.objects.filter(phone_number__icontains=validated_data['phone_number']).get()
        user = CustomUser.objects.create(
            phone_number='8' + phone_number,
            password=make_password(validated_data['password']),
            job_title=user_data.job_title,
            job_place=user_data.job_place,
            name=user_data.name,
            email=validated_data['email'],
            email_verification_token=random_string,
            verified_email=False
        )

        send_mail(
            'Подтверждение email',
            'Привет, Вы только что зарегистрировались на сайте Тренажер Счастья. '
            'Но чтобы получить доступ к закрытым материалам, нам нужно проверить вашу почту. Чтобы пройти проверку,'
            f' нажмите на кнопку    '
            f'<a href="https://happinesstrainer.ru/users/verificate_email/get_token/?token={random_string}" '
            'style="display: inline-block; background-color: #007bff; color: #fff; padding: 10px; " \
                  "text-decoration: none; border-radius: 5px;">Подтвердить почту</a>',
            'happinesstrainer@yandex.ru',
            [f'{validated_data["email"]}'],
            fail_silently=False,
            html_message='Привет, Вы только что зарегистрировались на сайте Тренажер Счастья. '
                         'Но чтобы получить доступ к закрытым материалам, нам нужно проверить вашу почту. Чтобы пройти проверку,'
                         f' нажмите на кнопку    '
                         f'<a href="https://happinesstrainer.ru/users/verificate_email/get_token/?token={random_string}" '
                         'style="display: inline-block; background-color: #007bff; color: #fff; padding: 10px; " \
                               "text-decoration: none; border-radius: 5px;">Подтвердить почту</a>',
        )

        # authenticate(phone_number=phone_number, password=validated_data['password'])
        # validated_data['user'] = user

        return user


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):

        phone_number = '8' + data.get('phone_number')
        password = data.get('password')

        if phone_number and password:
            user = authenticate(phone_number=phone_number, password=password)
            if user:
                data['user'] = user
            else:
                try:
                    Workers.objects.filter(phone_number__icontains=phone_number).get()
                except Workers.DoesNotExist:
                    raise serializers.ValidationError({'user': 'non_phone'})
                raise serializers.ValidationError({'user': 'invalid_data'})
        else:
            raise serializers.ValidationError({'user': 'incomplete'})

        return data


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        email = data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=15))

            user = CustomUser.objects.filter(email=email).get()
            pk = user.pk
            user.email_verification_token = random_string
            user.save()

            # asya = AsyncUsers()
            token_delay.delay(pk)

            send_mail(
                'Восстановление пароля',
                'Привет, вижу, что вы забыли пароль 🙁'
                'Чтобы восстановить доступ к аккунту нажмите на кнопку '
                             f'<a href="https://happinesstrainer.ru/users/forgot_password/validate_token/?token={random_string}" '
                'style="display: inline-block; background-color: #007bff; color: #fff; padding: 10px; " \
                  "text-decoration: none; border-radius: 5px;">Восстановить пароль</a>',
                'happinesstrainer@yandex.ru',
                [email],
                fail_silently=False,
                html_message='Привет, вижу, что вы забыли пароль 🙁'
                             'Чтобы восстановить доступ к аккунту нажмите на кнопку '
                             f'<a href='
                             f'"https://happinesstrainer.ru/users/forgot_password/validate_token/?token={random_string}" '
                             'style="display: inline-block; background-color: #007bff; color: #fff; padding: 10px; " \
                               "text-decoration: none; border-radius: 5px;">Восстановить пароль</a>',
            )

        else:
            raise serializers.ValidationError({'email': 'not_exist'})

        return data


class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField()
    token = serializers.CharField()

    def validate(self, data):
        # Поменять пароль и вернуть пользователя, чтобы залогинить его
        # print(password)
        if CustomUser.objects.filter(email_verification_token=data['token']).exists():
            user = CustomUser.objects.filter(email_verification_token=data['token']).get()
            user.set_password(data['password'])
            # user.password = data['password']
            user.save()
            return user
        else:
            raise serializers.ValidationError({'error': 'invalid_serializer'})

