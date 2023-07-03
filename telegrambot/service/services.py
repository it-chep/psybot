import os.path
import random
import textwrap
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

from psybot import settings
from telegrambot.models import *
from telegrambot.repository.repository import Repository
from telegrambot.utils.utils import Utils
from .markup import Markup
from .training import Training
from ..async_work.async_work import Async


class Registration:
    R_START = 'R_0'
    R_NAME = 'R_N'  # Фамилия Имя
    R_PHONE = 'R_P'  # Номер телефона
    R_WORK = 'R_W'  # Ресторан
    R_JOB = 'R_J'  # Должность
    R_END = 'R_E'  # Конец

    states = [R_START, R_NAME, R_PHONE, R_WORK, R_JOB, R_END]

    @staticmethod
    def start_registration(message):
        pass


class Service:
    repository = Repository
    training = Training
    registration = Registration
    utils = Utils
    asya = Async

    @staticmethod
    def fork(message, ):
        cache = Service.repository.ram_cache
        # print(Service.registered_or_not(message, flag=True))

        registered, _ = Service.registered_or_not(message, flag=True)
        if registered:
            if not cache.get(str(message.chat.id)):
                messages = ['К сожалению, вы слишком долго проходили карточку и мне пришлось сбросить ваш прогресс, '
                            'но вы можете пройти другую 🤖\n\n'
                            'Нажмите на кнопку и продолжайте тренироваться.\n\n'
                            'Если вам нужна техническая помощь, нажмите /tech_support']
                markups = [Markup.end_training_markup()]
                return messages, markups, []
        else:
            try:
                int(message.text)
                number = message.text
                # print(number)
                Service.repository.ram_cache.set(key=str(message.chat.id), value=f'{number}', timeout=60 * 15)
                return Service.check_in_base(message)

            except Exception as ex:
                messages = ['Я не понимаю ваше сообщение, пожалуйста напишите в техническую поддержку. Нажмите на '
                            'кнопку /tech_support, или на кнопку на клавиатуре']
                markups = [Markup.tech_support_markup()]
                return messages, markups, []

        cache_data = cache.get(str(message.chat.id)).split(',')
        state = cache_data[0]

        messages = []
        markups = []
        photos = []

        training_states = Training.states

        # if not state:
        #     state = Training.Q_START

        if state in training_states:

            state = cache_data[0]
            card_number = cache_data[1]
            photo_name = cache_data[2]
            coefficient = cache_data[3]

            if state == Training.Q_START:
                messages, markups, photos = Training.start_training(messages, markups, photos, card_number, cache,
                                                                    message, photo_name)
                Service.repository.ram_cache.set(key=str(message.chat.id),
                                                 value=f'1,{card_number},{photo_name},{coefficient}',
                                                 version=None)
                return messages, markups, photos

            if message.text == 'Попробовать ещё раз' or Service.validate_answer(message, card_number, state):

                messages, markups, photos = Training.contyinue_and_end_training(messages, markups, photos, card_number,
                                                                                cache, message, photo_name, coefficient,
                                                                                state)
                return messages, markups, photos
            else:
                messages, markups, photos = Service.wrong_answer(message, state, card_number, photo_name, coefficient)
                return messages, markups, photos

        if state == 'FB':

            Service.repository.feedback.objects.create(
                user=Profile.objects.filter(tg_id=message.chat.id).get(),
                text=message.text
            )

            messages.append('Записал вашу идею )')
            markups.append(Markup.start_markup())
            Service.repository.ram_cache.delete(key=str(message.chat.id))

        if state == 'MAIL':
            ids = list(Profile.objects.all().values_list('tg_id', flat=True))

            Service.pre_mailing(ids, message, messages, markups)

        if state == 'TEST_MAIL':
            ids = [243807051, 5534266099, 422165917]
            Service.pre_mailing(ids, message, messages, markups)

        return messages, markups, photos

    @staticmethod
    def pre_mailing(ids, message, messages, markups):

        messages.append('Рассылка запущена ...')
        markups.append('')
        markups.append(ids)
        Service.repository.ram_cache.delete(key=str(message.chat.id))

        return messages, markups

    @staticmethod
    def registered_or_not(message, flag=None):
        first_name = message.from_user.first_name if message.from_user.first_name else ''
        last_name = message.from_user.last_name if message.from_user.last_name else ''
        #
        usrs = list(Service.repository.profiles.objects.values_list('tg_id', flat=True))
        #
        if message.chat.id in usrs:
            if flag:
                return True, ''
            return True, Markup.start_markup()
        else:
            return False, Markup.registration_markup()
            #
            # Profile.objects.get_or_create(
            #     tg_id=message.chat.id,
            #     name=first_name + ' ' + last_name,
            #     # username=self.from_user.username,
            #     level=0,
            #     expirience=0,
            #     quality=0,
            #     last_used_card='0',
            #     user_status=Status.objects.get(pk=1),
            # )

        # if flag:
        #     return True, ''
        # return True, Markup.start_markup()

    @staticmethod
    def set_phone_in_ram(message):
        phone = Service.repository.ram_cache.get(key=str(message.chat.id))
        if phone:
            return
        else:
            phone = message.contact.phone_number[1:]
            Service.repository.ram_cache.set(key=str(message.chat.id), value=f'{phone}', timeout=60 * 15)
            return

    @staticmethod
    def check_in_base(message):  # В базе именно excel или json

        phone = Service.repository.ram_cache.get(key=str(message.chat.id))

        if not phone:
            return ['К сожалению, Вы слишком долго проходили регистрацию, и я забыл\n'
                    'Ваш номер телефона 😔\n\n'
                    'Нажмите на кнопку на клавиатуре "Начать регистрацию" и никуда не отходите', ], \
                [Markup.registration_markup()], []

        if '+7' in phone:
            phone = phone[2:]
        if phone[0] == '7' or phone[0] == '8':
            phone = phone[1:]
        print(phone)
        phone_numbers = list(Service.repository.workers.objects.values_list('phone_number', flat=True))
        # print('[+][+] message', message, sep='\n')
        for number in phone_numbers:
            print(number)
            if phone in number:
                if Service.repository.profiles.objects.filter(phone__icontains=phone).exists():
                    break
                try:
                    username = message.from_user.username
                except Exception as ex:
                    username = ' '

                new_person = Service.repository.workers.objects.filter(phone_number__icontains=phone).first()

                user = Service.repository.profiles.objects.create(
                    tg_id=int(message.chat.id),
                    name=new_person.name,
                    username=username,
                    phone=str(new_person.phone_number),
                    job_title=new_person.job_title,
                    job_place=new_person.job_place,
                    level=int(0),
                    expirience=int(0),
                    quality=float(0),
                    user_status=Service.repository.statuses.objects.get(status_value=0),
                )

                Service.registration_off()
                Service.repository.ram_cache.delete(key=str(message.chat.id))
                return ['Супер, нашел вас в Базе, приятного изучения бота 😇\n\n'
                        'Чтобы попасть в главное меню, '
                        'нажмите на кнопку на клавиатуре или на /menu'], \
                    [Markup.main_menu_markup()], []
        Service.repository.ram_cache.delete(key=str(message.chat.id))
        return ['К сожалению сотрудника с таким номером нет, или номер уже занят. Вы можете указать '
                'другой номер или в случае, если ваш номер телефона занят, написать @maxim_jordan, он поможет'],\
            [Markup.registration_markup()], []

    @staticmethod
    def get_status(message):

        user_data = Repository.profiles.objects.get(tg_id=str(message.chat.id))

        level = user_data.level
        exp = user_data.expirience
        quality = user_data.quality
        status = user_data.user_status

        if exp == 0:
            exp = 0
            quality = 0
        else:
            quality = round(float(quality / exp), 2)

        return level, status, exp, quality

    @staticmethod
    def get_main_menu_markup():
        return Markup.main_menu_markup()

    @staticmethod
    def clean_markup(flag=None):
        return Markup.clean_markup(flag)

    @staticmethod
    def yes_or_not_markup():
        return Markup.yes_or_not_markup()

    @staticmethod
    def send_card(message):
        cache = Service.repository.ram_cache

        if cache.get('card_count'):
            card_count = cache.get('card_count')
        else:
            card_count = Card.objects.count()
            cache.set(key='card_count', value=card_count)
        #
        card_number = random.randint(1, int(card_count))
        # card_number = str(int(
        #     list(Profile.objects.filter(tg_id=str(message.chat.id)).values_list("last_used_card", flat=True))[0]) + 1)

        # Берем фоточку
        photo_name = random.choice(
            list(Service.repository.photos_for_cards.objects.all().values_list(f'name', flat=True)))
        coefficient = '1'
        # print(message.chat.id)
        # Запоминаем номер карточки и ставим шаг 1 в кэше
        if not cache.get(str(message.chat.id)):
            cache.set(key=str(message.chat.id),
                      value=f'{Service.training.Q_START},{card_number},{photo_name},{coefficient}',
                      version=None)

        Service.clean_markup()

    @staticmethod
    def validate_answer(message, card_number, step):
        cached_right_answer = Service.repository.ram_cache.get(f'right_answers_{card_number}_{step}')

        if cached_right_answer:
            right_answer = cached_right_answer

        else:
            right_answer = Service.repository.cards.objects.values_list(f'right_answer_{step}', flat=True).filter(
                pk=card_number).get()
            Service.repository.ram_cache.set(f'right_answer_{card_number}_{step}', right_answer.encode('utf-8'),
                                             timeout=60 * 60 * 1)

        return True if message.text == right_answer else False

    @staticmethod
    def wrong_answer(message, step, card_number, photo_name, coefficient):

        step = str(int(step) - 1)
        coefficient = str(float(coefficient) - 1 / 12)

        Service.repository.ram_cache.set(key=str(message.chat.id),
                                         value=f'{step},{card_number},{photo_name},{coefficient}',
                                         version=None)

        msg = ['Вы допустили ошибку']
        markups = [Markup.mistake_markup()]
        photos = [os.path.join(settings.BASE_DIR, 'photos', photo_name, f'{photo_name}_bad.png')]

        return msg, markups, photos

    @staticmethod
    def get_contact_markup():
        return Markup.phone_markup()

    @staticmethod
    def registration_on():
        ram_cache = Service.repository.ram_cache
        if ram_cache.get(key='registration') == -100:  # проверка на мьютекс
            return False
        with ram_cache.client.pipeline() as pipe:
            while True:
                try:
                    pipe.watch('registration')
                    value = pipe.get('registration')
                    value = int(value) if value else 0
                    value += 1
                    pipe.multi()
                    pipe.set('registration', value)
                    pipe.execute()
                    break
                except Service.repository.red_is.WatchError:
                    continue
        return True

    @staticmethod
    def registration_off():
        ram_cache = Service.repository.ram_cache
        with ram_cache.client.pipeline() as pipe:
            while True:
                try:
                    pipe.watch('registration')
                    value = pipe.get('registration')
                    value = int(value) if value else 0
                    value -= 1
                    if value < 0:
                        value = 0
                    pipe.multi()
                    pipe.set('registration', value)
                    pipe.execute()
                    break
                except Service.repository.red_is.WatchError:
                    continue


    @staticmethod
    def download_table(bot, message):
        if 'json' in message.document.file_name or 'xlsx' in message.document.file_name:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            src = os.path.join(settings.BASE_DIR, 'tables', f'{message.document.file_name}')
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file)
            if 'xlsx' in message.document.file_name:
                return 'xlsx', src
            elif 'json' in message.document.file_name:
                return 'json', src
        return 'None', 'None'

    @staticmethod
    def excel_to_json(path):
        Service.asya.excel_to_json(os.path.join(settings.BASE_DIR, 'tables', path))

    @staticmethod
    def update_db(path):
        Service.asya.update_db.apply_async(args=(path,))

    @staticmethod
    def delete_table():
        Service.utils.delete_table()

    @staticmethod
    def rename_json(path):
        Service.utils.rename_json(path)

    @staticmethod
    def set_form_state(message):
        Service.repository.ram_cache.delete(key=str(message.chat.id))
        Service.repository.ram_cache.set(key=str(message.chat.id), value='FB')

    @staticmethod
    def set_mailing_state(message, state):
        Service.repository.ram_cache.delete(key=str(message.chat.id))
        Service.repository.ram_cache.set(key=str(message.chat.id), value=state)

    @staticmethod
    def check_the_admin(message):
        if message.chat.id in [243807051, 422165917]:  # ДОВЕСТИ ДО УМА
            return True
        else:
            return False

    @staticmethod
    def get_mood_markup():
        return Markup.get_mood_markup()

    @staticmethod
    def write_mood_in_base(chat_id, grade):

        if '10' in grade:
            grade = 10
        elif '1' in grade:
            grade = 1

        user = Service.repository.profiles.objects.filter(tg_id=chat_id).get()
        Service.repository.mood.objects.create(
            user=user,
            grade=int(grade)
        )

        last_mood = Service.repository.last_day_mood.objects.filter(user=user)
        if last_mood.first():
            last_user_mood = last_mood.get()
            last_user_mood.last_reminder_date = datetime.today()
            last_user_mood.save()
        else:
            Service.repository.last_day_mood.objects.create(
                user=user,
                last_reminder_date=datetime.today()
            )

        return Markup.start_markup()

    @staticmethod
    def save_message_id(chat_id, message_id):
        Service.repository.ram_cache.set(f'mood_{chat_id}', message_id)

    @staticmethod
    def get_message_id(chat_id):
        Service.repository.ram_cache.set(f'day_mood_{chat_id}', '1', timeout=24*60*60)
        return Service.repository.ram_cache.get(f'mood_{chat_id}')

    @staticmethod
    def get_day_mood_state(message):
        Service.repository.ram_cache.delete(f'mood_{message.chat.id}')
        return Service.repository.ram_cache.get(f'day_mood_{message.chat.id}')

