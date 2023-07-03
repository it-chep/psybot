from hashlib import sha256

from django.http import HttpResponse
from django_telegram_login.authentication import verify_telegram_authentication
from django_telegram_login.errors import TelegramDataIsOutdatedError, NotTelegramDataError
from django_telegram_login.widgets.constants import (
    SMALL,
    MEDIUM,
    LARGE,
    DISABLE_USER_PHOTO,
)
from django_telegram_login.widgets.generator import (
    create_callback_login_widget,
    create_redirect_login_widget,
)

import requests
import telebot
from django.contrib.auth import logout
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.utils.crypto import get_random_string
from django.utils.decorators import method_decorator
from rest_framework import generics, serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
import string
import random
from telegrambot.models import Profile
import psybot.settings
from .decorators import UserDecorator
from .serializers import *

bot = telebot.TeleBot(token=psybot.settings.BOT_TOKEN)
from django.conf import settings

bot_name = settings.BOT_NAME
bot_token = settings.BOT_TOKEN
redirect_url = settings.TELEGRAM_LOGIN_REDIRECT_URL

# telegram_login_widget = create_callback_login_widget(bot_name, corner_radius=10, size=MEDIUM)

telegram_login_widget = create_redirect_login_widget(redirect_url, bot_name, size=LARGE, user_photo=DISABLE_USER_PHOTO)


class SignUpView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer
    template_name = 'users/signup.html'
    telegram_login_widget = create_callback_login_widget(bot_name, size=SMALL)

    @staticmethod
    def get(request):
        if not request.user.is_anonymous:
            return redirect('logout')
        return render(request, SignUpView.template_name, {'telegram_login_widget': telegram_login_widget})

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.create(serializer.validated_data)
            login(request, user)
            return Response({'status': 200, 'message': 'Супер, теперь осталось подтвердить свой email'},
                            status=status.HTTP_200_OK)

        else:
            errors = serializer.errors
            if 'phone_number' in errors:
                phone_errors = errors['phone_number']

                if 'not_unique' in phone_errors:
                    return redirect('login')

                elif 'invalid' in phone_errors:
                    # return redirect('phone_not_found')
                    return Response({'status': 'error', 'message': 'Такого телефона нет в базе сотрудников, '
                                                                   'попробуйте другой'},
                                    status=status.HTTP_400_BAD_REQUEST)
            return Response({'status': 'fatal_error', 'message': 'Ошибка сервера'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CheckEmail(APIView):
    template_name = ''

    def get(self, request):
        return render(request, self.template_name)


class LoginView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer
    template_name = 'users/login.html'

    def get(self, request):
        if not request.user.is_anonymous:
            return redirect('logout')
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            return redirect('raiting')
        else:
            errors = serializer.errors
            if 'user' in errors:
                user_errors = errors['user']

                if 'non_phone' in user_errors:
                    return Response({'status': 'error', 'message': 'Такого телефона нет в базе сотрудников, '
                                                                   'попробуйте другой'},
                                    status=status.HTTP_400_BAD_REQUEST)
                if 'invalid_data' in user_errors:
                    return Response({'status': 'invalid_data', 'message': 'Что-то пошло не так'},
                                    status=status.HTTP_400_BAD_REQUEST)
            if 'phone_number' in errors:
                return Response({'status': 'not_phone', 'message': 'Такого телефона нет в базе сотрудников, '
                                                                   'попробуйте другой'},
                                status=status.HTTP_400_BAD_REQUEST)

            return redirect('signup')


@method_decorator(UserDecorator.validate, name='dispatch')
class LogoutView(APIView):
    # Работает без JS
    permission_classes = (IsAuthenticated,)
    template_name = 'users/logout.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        logout(request)
        return redirect('homepage')


class VerificationEmail(APIView):

    def get(self):
        pass

    def post(self):
        pass


class GetToken(APIView):

    def get(self, request):
        token = request.GET.get('token')

        user = CustomUser.objects.filter(email_verification_token=token).get()

        if user:
            user.verified_email = True
            user.save()
            return redirect('raiting')
        else:
            return redirect('invalid_token')


class ForgotPassword(APIView):
    template_name = 'users/forgot_password.html'
    permission_classes = (AllowAny,)
    serializer_class = ForgotPasswordSerializer

    def get(self, request):
        if not request.user.is_anonymous:
            return redirect('logout')
        return render(request, self.template_name)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            return Response({'status': 200}, status=status.HTTP_200_OK)
        else:
            errors = serializer.errors
            if 'email' in errors:
                user_errors = errors['email']
                if 'not_exist' in user_errors:
                    return Response({'status': 'error', 'message': 'Плохой email'},
                                    status=status.HTTP_400_BAD_REQUEST)

            return redirect('signup')


class NotInBase(APIView):

    def get(self, request):
        return render(request, 'users/not_in_base.html')


class ValidateToken(APIView):
    template_name = 'users/validate_token.html'

    def get(self, request, ):
        token = request.GET.get('token')

        user = CustomUser.objects.filter(email_verification_token=token).first()

        if user:
            return redirect(reverse_lazy('change_password') + f'?token={token}')
        else:
            return redirect('invalid_token')


class ChangePassword(APIView):
    permission_classes = (AllowAny,)
    serializer_class = ChangePasswordSerializer
    template_name = 'users/change_password.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid()
        if serializer.is_valid():
            user = CustomUser.objects.filter(email_verification_token=request.GET.get('token')).get()
            print(user, user.password, )
            login(request, user)
            return redirect('raiting')

        else:
            print('post error')
            errors = serializer.errors
            return redirect('raiting')


class InvalidToken(APIView):
    template_name = 'users/invalid_token.html'

    def get(self, request):
        return render(request, self.template_name)


# '6084181152:AAEjV1FR6SyuZx-FOyWVdGc3xJJSIwdisB0'
class TelegramSignIN(APIView):
    template_name = 'users/telegram_signup.html'

    def get(self, request):
        if not request.GET.get('hash'):
            return HttpResponse('Handle the missing Telegram data in the response.')

        try:
            result = verify_telegram_authentication(
                bot_token=bot_token, request_data=request.GET
            )

        except TelegramDataIsOutdatedError:
            return HttpResponse('Authentication was received more than a day ago.')

        except NotTelegramDataError:
            return HttpResponse('The data is not related to Telegram!')

        return render(request, self.template_name)

    def post(self, request):

        tg_id = request.data.get('id')

        user = CustomUser.objects.filter(user_id=tg_id).exists()
        if not user:
            name = request.data.get('name')
            user_name = request.data.get('user_name')
            try:
                phone_number = Profile.objects.filter(tg_id=tg_id).values_list('phone', flat=True)
            except Profile.DoesNotExist:
                return Response({'status': 'not_phone', 'message': 'Такого телефона нет в базе сотрудников, '
                                                                   'попробуйте другой'},
                                status=status.HTTP_400_BAD_REQUEST)

            user = CustomUser.objects.create(
                user_id=tg_id,
                name=name,
                password=get_random_string(20),
                email='',
                phone_number=phone_number,
                verified_email=True,
                job_place='',
                job_title='',
                user_name=user_name
            )

        login(request, user)
        return redirect('raiting')
        #
        # # telegram_user = request.data.get('telegram_user')
        # # if not telegram_user:
        # #     return Response({'error': 'Telegram user data not provided'},
        # #                     status=status.HTTP_400_BAD_REQUEST)
        # #
        # # # Проверяем, что состояние CSRF-токена соответствует сохраненному в сессии
        # # if request.data.get('state') != request.session.get('telegram_login_state'):
        # #     return Response({'error': 'Invalid state parameter'},
        # #                     status=status.HTTP_403_FORBIDDEN)
        # #
        # # # Получаем информацию о пользователе из Telegram API
        # # response = requests.get(
        # #     'https://api.telegram.org/bot{}/getChatMember?chat_id={}&user_id={}'.format(
        # #         psybot.settings.BOT_TOKEN,
        # #         telegram_user['chat_id'],
        # #         telegram_user['id']
        # #     )
        # # )
        # #
        # # if response.status_code != 200:
        # #     return Response({'error': 'Error getting user information from Telegram'},
        # #                     status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # #
        # # user_data = response.json()['result']
        # # user_profile, created = CustomUser.objects.get_or_create(user_id=user_data['user']['id'])
        # # user_profile.username = user_data['user'].get('username')
        # # user_profile.first_name = user_data['user'].get('first_name')
        # # user_profile.last_name = user_data['user'].get('last_name')
        # # user_profile.save()
        #
        # return Response({'message': 'User authenticated successfully'})

