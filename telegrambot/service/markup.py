import random

from telebot import types
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

# from .services  Service
from telegrambot.repository.repository import Repository


class Markup:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    repository = Repository

    @staticmethod
    def clean_markup(flag=None):
        Markup.markup.keyboard.clear()
        if flag:
            return types.ReplyKeyboardRemove()
        return

    @staticmethod
    def phone_markup():
        phone_button = types.KeyboardButton(text="Поделиться номером телефона", request_contact=True)
        Markup.markup.add(phone_button)
        return Markup.markup

    @staticmethod
    def start_markup():
        Markup.markup.add('Почему важно разрешать конфликты умно')
        Markup.markup.add('Дело техники')
        Markup.markup.add('ТРЕНАЖЁР')
        return Markup.markup

    @staticmethod
    def registration_markup():
        Markup.markup.add('Начать регистрацию')
        return Markup.markup

    @staticmethod
    def main_menu_markup():
        Markup.markup.add('Главное меню')
        return Markup.markup

    @staticmethod
    def tech_support_markup():
        Markup.markup.add('Позвать техническую поддержку')
        return Markup.markup

    @staticmethod
    def mistake_markup():
        Markup.markup.add('Попробовать ещё раз')
        return Markup.markup

    @staticmethod
    def training_markup(cache, card_number, step):

        cached_answers = cache.get(f'answers_{card_number}_{step}')

        if cached_answers:
            answers = cached_answers.split('\n')
        else:
            answers = list(Markup.repository.cards.objects.values_list(f'answers_{step}', flat=True).filter(pk=card_number))[0].split('\n')
            cache.set(f'answers_{card_number}_{step}', '\n'.join(answers).encode('utf-8'), timeout=60 * 60 * 1)

        random.shuffle(answers)

        for answer in answers:
            Markup.markup.add(answer)
        return Markup.markup

    @staticmethod
    def end_training_markup():
        Markup.markup.add('Вернуться в главное меню')
        Markup.markup.add('Продолжить тренироваться')
        return Markup.markup

    @staticmethod
    def yes_or_not_markup():
        Markup.markup.add('Да, продолжаем')
        Markup.markup.add('Нет, я хочу поменять')
        return Markup.markup

    @staticmethod
    def get_mood_markup():
        inline_markup = types.InlineKeyboardMarkup(row_width=5)

        row = [InlineKeyboardButton('10👍', callback_data=str(10))]
        for i in range(9, 1, -1):
            row.append(InlineKeyboardButton(str(i), callback_data=str(i)))
            if len(row) == 5:
                inline_markup.row(*row)
                row = []

        row.append(InlineKeyboardButton('1👎', callback_data=str(1)))
        if row:
            inline_markup.row(*row)

        return inline_markup
