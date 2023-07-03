# from .services import Service
import os
import textwrap

from PIL import Image, ImageFont, ImageDraw

from psybot import settings
from .markup import Markup
from telegrambot.repository.repository import Repository


class Training:
    repository = Repository

    Q_START = str(0)  # Начало карточки
    Q_STEP_1 = str(1)
    Q_STEP_2 = str(2)
    Q_STEP_3 = str(3)
    Q_END = str(4)

    states = [Q_START, Q_STEP_1, Q_STEP_2, Q_STEP_3, Q_END]

    @staticmethod
    def get_message(card_number, msg_id, schema):
        messages = {
            # '1': f'*НОМЕР КАРТОЧКИ {card_number}*\n\n'
            '1': f'Шаг 1: Амортизация\n\n'
                 f'Что бы вы сказали?\n\n',
            '2': 'Шаг 2: Речевой прием\n\n'
                 f'Схема ответа: {schema}\n\n'
                 f'Что бы вы сказали? \n\n',
            '3': f'Шаг 3: Перехват инициативы\n\n'
                 f'Что бы вы сказали? \n\n',
            '4': f'Гость доволен!'
        }
        return messages[msg_id]

    @staticmethod
    def start_training(messages, markups, photos, card_number, cache, message, photo_name):
        messages.append(Training.get_message(card_number, '1', schema=0))
        markups.append(Markup.training_markup(cache, card_number, '1'))
        photos.append(Training.work_with_img(photo_name, message.chat.id))

        return messages, markups, photos

    @staticmethod
    def __clear(user_data, value):
        user_data.user_status = Repository.statuses.objects.filter(status_value=value).get()
        user_data.level += 1
        user_data.expirience = 0
        user_data.quality = 0
        return

    @staticmethod
    def contyinue_and_end_training(messages, markups, photos, card_number, cache, message, photo_name, coefficient,
                                   state):

        state = str(int(state) + 1)
        Training.repository.ram_cache.set(key=str(message.chat.id),
                                         value=f'{state},{card_number},{photo_name},{coefficient}',
                                         version=None)
        schema = \
            list(Training.repository.cards.objects.filter(pk=card_number).values_list("schemas", flat=True))[0]
        messages.append(Training.get_message(card_number, state, schema))

        if state == Training.Q_END:
            photos.append(f"photos/{photo_name}/{photo_name}_good.png")
            user_data = Training.repository.profiles.objects.get(tg_id=str(message.chat.id))
            user_data.expirience += 1
            user_data.quality += float(coefficient)
            user_data.last_used_card = card_number
            # ур 0 5 карт прошел - exp = 5 5 // 5 ==  + 1
            if user_data.expirience % 5 == 0 and user_data.expirience // 5 == (user_data.level + 1):
                #
                # Обновляем рейтинг
                #
                value = 5 * (user_data.level + 1)
                Training.__clear(user_data, value)

            elif user_data.expirience % 5 == 0 and user_data.level == 0:

                Training.__clear(user_data, 5)

            user_data.save()
            right_answers = [cache.get(key=f"right_answer_{card_number}_1"),
                             cache.get(key=f"right_answer_{card_number}_2"),
                             cache.get(key=f"right_answer_{card_number}_3")]
            Training.repository.ram_cache.delete(key=str(message.chat.id), version=None)

            quality = round(float(coefficient), 2) * 100

            messages.append(f'Качество вашего обслуживания {quality}%')
            markups.append('')
            messages.append(
                f'Запрос гостя: \n{list(Training.repository.cards.objects.filter(pk=card_number).values_list("name", flat=True))[0]}\n\n'  ##########!!!!!!!!!!!!!!##########
                f'Ваш ответ: \n{right_answers[0]}\n\n{right_answers[1]}\n\n{right_answers[2]}')
            markups.append('')
            markups.append(Markup.end_training_markup())
            return messages, markups, photos

        markups.append(Markup.training_markup(Training.repository.ram_cache, card_number, state))

        return messages, markups, photos

    @staticmethod
    def split_text(text, font, max_width):
        words = text.split()
        lines = []
        current_line = words[0]
        for word in words[1:]:
            if font.getsize(current_line + ' ' + word)[0] <= max_width:
                current_line += ' ' + word
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)
        return '\n'.join(lines)

    @staticmethod
    def work_with_img(ph_id, user_id):
        image_path = os.path.join(settings.BASE_DIR, f'photos/{ph_id}/{ph_id}_Q.png')

        if os.path.isfile(image_path):
            img = Image.open(image_path)
            line_number = Training.repository.ram_cache.get(key=str(user_id)).split(',')[1]

            phrase = Training.repository.cards.objects.filter(pk=line_number).values_list("name", flat=True)[0]  # берем фразу

            font = ImageFont.truetype(os.path.join(settings.BASE_DIR, "OrelegaOne-Regular.ttf"),
                                      70)  # Устанавливаем шрифт
            color = (0, 0, 0)  # Выбираем цвет шрифта

            draw = ImageDraw.Draw(img)  # Создаем объект, на котором рисуем
            new_phrase = textwrap.wrap(phrase, width=20)

            pad = 10
            current_h = 700 + (700 / 1 / len(new_phrase)) // 2

            for line in new_phrase:
                w, h = draw.textsize(line, font=font)
                draw.text(((850 - w) / 2, current_h), line, fill=color, font=font)
                current_h += h + pad

            new_photo_path = f'NEW_photos/NEW_{ph_id}.png'  # Указываем путь, по которому будем мсохранять фото
            img.save(new_photo_path)  # Сохранили фото
            return new_photo_path
        else:
            print(f"Файл {image_path} не найден")