from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser, models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, unique=True)
    job_place = models.CharField(max_length=50)
    job_title = models.CharField(max_length=50)
    password = models.CharField(max_length=255)
    verified_email = models.BooleanField(verbose_name='Email настоящий')
    email_verification_token = models.CharField(max_length=20)
    username = models.CharField(max_length=150, unique=False, default='')
    # REQUIRED_FIELDS = ['phone_number']
    USERNAME_FIELD = 'phone_number'

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Пользователь сайта'
        verbose_name_plural = 'Пользователи сайта'
