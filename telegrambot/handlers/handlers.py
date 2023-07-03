import json
import os, sys

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from requests.exceptions import ConnectionError, ReadTimeout

from django.core.management.base import BaseCommand
import telebot
from django.conf import settings

from telegrambot.service.services import Service

bot = telebot.TeleBot(settings.BOT_TOKEN)


@csrf_exempt
def telegram_webhook(request):
    if request.method == 'POST':
        update = telebot.types.Update.de_json(request.body.decode('utf-8'))
        bot.process_new_updates([update])
    return HttpResponse(status=200)


class Handler:
    service = Service()
    bot = bot

    @staticmethod
    @bot.message_handler(commands=['start'])
    @bot.message_handler(commands=['menu'])
    @bot.message_handler(regexp='Главное меню')
    def start_message(message):
        state, markup = Handler.service.registered_or_not(message)
        if state:
            bot.send_message(message.chat.id, f'Приветствую тебя в главном меню. '
                                              f'Ты можешь выбрать раздел, который хочешь посетить. 👇',
                             reply_markup=markup)
            bot.send_message(message.chat.id,
                             'P.s Если у тебя не появились кнопки, нажми на значок в виде окна слева у '
                             'микрофона на клавиатуре.')
        else:
            bot.send_message(message.chat.id, 'Вы не зарегистрированны, чтобы зарегистрироваться, нажмите '
                                              'кнопку на клавиатуре', reply_markup=markup)
        Handler.service.clean_markup()

    @staticmethod
    @bot.message_handler(commands=['statistic'])
    def my_statistic_message(message, ):
        registred, markup = Handler.service.registered_or_not(message, flag=True)
        if registred:
            level, status, exp, quality = Handler.service.get_status(message)
            markup = Handler.service.get_main_menu_markup()
            bot.send_message(message.chat.id, f'Ваш уровень: {level}\n\n'
                                              f'На этом уровне пройдено карт: {exp}\n\n'
                                              f'Качество выполнения {quality}\n\n'
                                              f'Ваш статус: "{status}"', reply_markup=markup)
        else:
            bot.send_message(message.chat.id, 'Вы не зарегистрированны, чтобы зарегистрироваться, нажмите '
                                              'кнопку на клавиатуре', reply_markup=markup)

        Handler.service.clean_markup()

    @staticmethod
    @bot.message_handler(commands=['moving_db.json'])
    def update_db(message):
        bot.send_message(message.chat.id, 'Приступил к обновлению бд')
        Handler.service.update_db('moving_db.json')
        bot.send_message(message.chat.id, 'Обновления завершены')
        Handler.service.clean_markup()

    @staticmethod
    @bot.message_handler(commands=['drop_db'])
    def update_db(message):
        bot.send_message(message.chat.id, 'Приступил к удалению бд')
        Handler.service.delete_table()
        bot.send_message(message.chat.id, 'Удаление завершены')
        Handler.service.clean_markup()

    @staticmethod
    @bot.message_handler(regexp='Начать регистрацию')
    def start_registration(message, ):
        status = Handler.service.registration_on()

        if status:
            markup = Handler.service.get_contact_markup()
            bot.send_message(message.chat.id,
                             'Добро пожаловать в ТРЕНАЖЁР СЧАСТЬЯ!\n\nЧтобы я смог Вас опознать, '
                             'укажите ваш номер телефона. \n\nТакже вы можете поделиться номером'
                             ' телефона нажав на кнопку на клавиатуре, '
                             'НО ТОЛЬКО ЕСЛИ ваш ЛИЧНЫЙ номер совпадает с РАБОЧИМ номером',
                             reply_markup=markup)
        else:
            _, markup = Handler.service.registered_or_not(message)
            bot.send_message(message.chat.id, 'Сейчас мы обновляем базу данных ...\n\n'
                                              'Подождите буквально минутку и нажмите кнопку еще раз 😇',
                             reply_markup=markup)
        Handler.service.clean_markup()

    @staticmethod
    @bot.message_handler(content_types=['contact'])
    def check_phone(message, ):
        markup = Handler.service.yes_or_not_markup()
        bot.send_message(message.chat.id,
                         f'Ваш номер телефона: {message.contact.phone_number}, верно?',  # телефон в кэшик
                         reply_markup=markup)
        Handler.service.set_phone_in_ram(message)
        Handler.service.clean_markup()

    @staticmethod
    @bot.message_handler(regexp='Да, продолжаем')
    def check_user_data(message, ):
        bot.send_message(message.chat.id, 'Пару секунд, ищу вас в Базе Сотрудников ...')

        messages, markup, [] = Service.check_in_base(message)

        bot.send_message(message.chat.id, messages[0], reply_markup=markup[0])
        Handler.service.clean_markup()

    @staticmethod
    @bot.message_handler(regexp='Нет, я хочу поменять')
    def change_number(message, ):
        Handler.start_registration(message)
        Handler.service.clean_markup()

    @staticmethod
    @bot.message_handler(regexp='Дело техники')
    def tech_deal(message, ):

        registered, markup = Handler.service.registered_or_not(message, flag=True)
        if registered:
            markup = Handler.service.get_main_menu_markup()
            bot.send_message(message.chat.id, "<b>Алгоритм ответа на конфликтную ситуацию:</b> \n\n"
                                              "Шаг 1: Амортизация (Дать понять, что гостя услышали, "
                                              "поблагодарить, если уместно)\n"
                                              "Шаг 2: Речевой прием “Несмотря на X, иногда бывает Y”\n"
                                              "Шаг 3: Перехват инициативы. (Открытый вопрос с позитивным "
                                              "допущением)\n\n"
                                              "https://youtu.be/qg_LQ-GdlsI\n\n"
                                              "*Данные речевые конструкции не применимы в тех случаях, когда "
                                              "действительно есть серьезное нарушение и необходимо пригласить "
                                              "метрдотеля.",
                             reply_markup=markup,
                             parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, 'Вы не зарегистрированны, чтобы зарегистрироваться, нажмите '
                                              'кнопку на клавиатуре', reply_markup=markup)
        Handler.service.clean_markup()

    @staticmethod
    @bot.message_handler(regexp='Почему важно разрешать конфликты умно')
    def tech_deal(message, ):
        registered, markup = Handler.service.registered_or_not(message, flag=True)
        if registered:
            markup = Handler.service.get_main_menu_markup()
            bot.send_message(message.chat.id,
                             "<b>Зачем решать конфликты умно</b>\n\n"
                             "Этот тренажер позволит вам выйти “сухим из воды”. Нейтрализуйте возмущение гостя, "
                             "его желание вас зацепить с помощью простых приемов.\n\n"
                             "Тем не менее, помните: лучшее разрешение конфликта – это его предупреждение.\n\n"
                             "https://youtu.be/_Du6wK3tSnc",
                             reply_markup=markup, parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, 'Вы не зарегистрированны, чтобы зарегистрироваться, нажмите '
                                              'кнопку на клавиатуре', reply_markup=markup)
        Handler.service.clean_markup()

    @staticmethod
    @bot.message_handler(regexp='Продолжить тренироваться')
    @bot.message_handler(regexp='ТРЕНАЖЁР')
    def send_card_preview(message, ):
        registred, markup = Handler.service.registered_or_not(message, flag=True)
        # print(registred, markup)
        if registred:
            bot.send_message(message.chat.id, "Пару секунд, подбираю ситуацию ...")
            Handler.service.send_card(message)
            Handler.send_some_message(message, )
        else:
            bot.send_message(message.chat.id, 'Вы не зарегистрированны, чтобы зарегистрироваться, нажмите '
                                              'кнопку на клавиатуре', reply_markup=markup)
        Handler.service.clean_markup()

    @staticmethod
    @bot.message_handler(content_types=['document'])
    def get_table(message, ):
        if Handler.service.check_the_admin(message):
            data_type, path = Handler.service.download_table(bot, message)
            if data_type == 'xlsx':
                bot.send_message(message.chat.id, 'Табличку скушал')
                bot.send_message(message.chat.id, 'Начинаю работать с табличкой')
                Handler.service.excel_to_json(path)
            elif data_type == 'json':
                bot.send_message(message.chat.id, 'Кушаю Json')
                Handler.service.rename_json(path)
                bot.send_message(message.chat.id, 'Переименовал его, можно и базу обновить')
            else:
                bot.send_message(message.chat.id, 'Я не могу обработать этот документ')
        else:
            bot.send_message(message.chat.id, 'Доступ запрещен')

        Handler.service.clean_markup()

    @staticmethod
    @bot.message_handler(commands=['form'])
    def send_form(message):
        registered, markup = Handler.service.registered_or_not(message, flag=True)

        if registered:
            Handler.service.set_form_state(message)

            bot.send_message(message.chat.id, 'Вижу, что вы хотите улучшить работу нашего '
                                              'бота и тренажера в целом. Подскажите, какая у вас возникла идея ?')

    @staticmethod
    @bot.message_handler(commands=['spam_mailing'])
    def spam_mailing(message):
        registered, markup = Handler.service.registered_or_not(message, flag=True)
        if registered:
            Handler.service.set_mailing_state(message, "MAIL")

            bot.send_message(message.chat.id, 'Введите текст рассылки')

    @staticmethod
    @bot.message_handler(commands=['test_mailing'])
    def test_mailing(message):
        registered, markup = Handler.service.registered_or_not(message, flag=True)
        if registered:
            Handler.service.set_mailing_state(message, "TEST_MAIL")

            bot.send_message(message.chat.id, '[+]ТЕСТИРОВАНИЕ РАССЫЛКИ[+]\n\nВведите текст рассылки')

    @staticmethod
    @bot.message_handler(commands=['mood'])
    def send_mood_notice(message):

        markup = Service().get_mood_markup()

        sent_message = bot.send_message(message.chat.id, 'Привет, мне очень важно ваше ежедневное состояние, пожалуйста'
                                                         ' расскажите мне какое оно. \n\n Оцените его по шкале от 1 до 10,'
                                                         ' где 10 - супер-пупер, а 1 - очень плохо',
                                        reply_markup=markup)

        Service().save_message_id(message.from_user.id, sent_message.message_id)

        Handler.service.clean_markup()

    @staticmethod
    @bot.callback_query_handler(func=lambda message: True)
    def handle_multiple_values_callback(message):

        Handler.service.clean_markup()

        markup = Service().write_mood_in_base(message.from_user.id, message.data)
        message_id = Service().get_message_id(message.from_user.id)
        bot.delete_message(message.from_user.id, message_id)
        bot.send_message(message.from_user.id, f'Ответ записан )', reply_markup=markup)

        Handler.service.clean_markup()


    ######################################

    ######################################

    @staticmethod
    @bot.message_handler(func=lambda message: True)
    def send_some_message(message):
        if not(Handler.service.get_day_mood_state(message)):
            Handler.send_mood_notice(message)
            return
        messages, markups, photos = Handler.service.fork(message)

        if photos:
            for photo_name in photos:
                bot.send_photo(message.chat.id, photo=open(photo_name, 'rb'))

                if os.path.exists(photo_name) and 'NEW' in photo_name:
                    os.remove(os.path.join(settings.BASE_DIR, photo_name))
        # print(markups, messages)
        for markup, msg in zip(markups, messages):
            bot.send_message(message.chat.id, msg, reply_markup=markup)
        for ids in markups:
            if type(ids) == list:
                for tg_id in ids:
                    # print(tg_id)
                    bot.send_message(tg_id, message.text)
                bot.send_message(message.chat.id, "Рассылка завершена !")

        Handler.service.clean_markup()
        Handler.service.clean_markup()
