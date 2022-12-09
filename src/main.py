import json
import os
import random

import vk_api as vk
from dotenv import load_dotenv
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from database import DataBase
from weather import get_weather_in_city
from curencies import get_currency_rates
import google_sheets

load_dotenv()

TOKEN = os.environ.get("TOKEN")
GROUP_ID = os.environ.get("GROUP_ID")

change_city_in_progress = False


def request_to_fill_user_city(user_id, vk_api):
    global change_city_in_progress
    change_city_in_progress = True
    send_message(vk_api, user_id, 'Кажется у вас нет города, напишите его ниже :)')


def init_user_city(user_id, vk_api):
    response = get_user_city(vk_api, user_id)
    if response:
        city = response['title']
        keyboard = VkKeyboard(inline=True)
        keyboard.add_button('Да', color=VkKeyboardColor.POSITIVE, payload={'type': 'city', 'answer': 'yes'})
        keyboard.add_button('Нет', color=VkKeyboardColor.NEGATIVE, payload={'type': 'city', 'answer': 'no'})
        send_message(vk_api, user_id, f"Ваш город {city}?", keyboard)
    else:
        request_to_fill_user_city(user_id, vk_api)


def get_user_city(vk_api, user_id):
    return vk_api.users.get(user_ids=user_id, fields='city')[0].get('city')


def send_message(vk_api, user_id, message, keyboard=None):
    options = dict(
        peer_id=user_id,
        message=message,
        random_id=random.getrandbits(32)
    )
    if keyboard:
        options['keyboard'] = keyboard.get_keyboard()
    vk_api.messages.send(**options)


def start(event, vk_api):
    user_id = event.object.message['from_id']
    city = DataBase.get_user_city(user_id)
    if city is None:
        init_user_city(user_id, vk_api)
    else:
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('Погода', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Пробка', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Афиша', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Валюта', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Изменить город', color=VkKeyboardColor.SECONDARY)
        user_id = event.object.message['from_id']
        send_message(vk_api, user_id, "Привет", keyboard)


def get_weather(event, vk_api):
    keyboard = VkKeyboard(inline=True)
    keyboard.add_button('Сегодня', color=VkKeyboardColor.POSITIVE, payload={'type': 'weather', 'day': 'сегодня'})
    keyboard.add_button('Завтра', color=VkKeyboardColor.POSITIVE, payload={'type': 'weather', 'day': 'завтра'})
    user_id = event.object.message['from_id']
    send_message(vk_api, user_id, "Выберите день, за который хотите получить погоду", keyboard)


def get_detail_weather(event, vk_api, day):
    user_id = event.object.message['from_id']
    city = DataBase.get_user_city(user_id)
    if city is None:
        request_to_fill_user_city(user_id, vk_api)
        return
    weather = get_weather_in_city(city)
    send_message(vk_api, user_id, f'В городе {weather} градусов {"тепла" if weather > 0 else "холода"}')


def get_poster(event, vk_api):
    keyboard = VkKeyboard(inline=True)
    keyboard.add_button('Сегодня', color=VkKeyboardColor.POSITIVE, payload={'type': 'poster', 'day': 'сегодня'})
    keyboard.add_button('Завтра', color=VkKeyboardColor.POSITIVE, payload={'type': 'poster', 'day': 'завтра'})
    user_id = event.object.message['from_id']
    send_message(vk_api, user_id, "Выберите день, за который хотите получить афишу", keyboard)


def get_detail_poster(event, vk_api, day):
    user_id = event.object.message['from_id']
    city = DataBase.get_user_city(user_id)
    if city is None:
        request_to_fill_user_city(user_id, vk_api)
        return
    posters = google_sheets.get_posters(city, day)
    out = []
    for poster in posters:
        out.append(f"{poster['event']}\n{poster['price']}\n{poster['link']}")
    send_message(vk_api, user_id, 'Афиша\n\n' + '\n\n'.join(out))


def get_currency(event, vk_api):
    user_id = event.object.message['from_id']
    currencies = get_currency_rates()
    out = []
    for k, v in currencies.items():
        out.append(f"1 {k} = {v} RUB")
    send_message(vk_api, user_id, 'Курсы валют\n' + '\n'.join(out))


def get_traffic_status(event, vk_api):
    user_id = event.object.message['from_id']
    city = DataBase.get_user_city(user_id)
    if city is None:
        request_to_fill_user_city(user_id, vk_api)
        return
    status = google_sheets.get_traffic_status(city)
    send_message(vk_api, user_id, f"В городе пробки {status} баллов")


def update_user_city(event, vk_api):
    global change_city_in_progress

    user_id = event.object.message['from_id']
    city = event.object.message['text']
    DataBase.update_user_city(user_id, city)
    change_city_in_progress = False
    send_message(vk_api, user_id, f"Город обновлён")


def process_city_answer(event, vk_api, answer):
    user_id = event.object.message['from_id']
    if answer == 'yes':
        city = get_user_city(vk_api, user_id)['title']
        DataBase.update_user_city(user_id, city)
        send_message(vk_api, user_id, f"Город обновлён")
    elif answer == 'no':
        request_to_fill_user_city(user_id, vk_api)
    else:
        raise Exception('Unexpected state')


def change_city(event, vk_api):
    global change_city_in_progress
    user_id = event.object.message['from_id']
    change_city_in_progress = True
    send_message(vk_api, user_id, 'Введите новый город ниже')


def main():
    vk_session = vk.VkApi(token=TOKEN)
    vk_api = vk_session.get_api()
    long_poll = VkBotLongPoll(vk_session, GROUP_ID)

    for event in long_poll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            if 'payload' in event.object.message:
                payload = json.loads(event.object.message['payload'])
                payload_type = payload.get('type')
                if payload_type == 'weather':
                    day = payload['day']
                    get_detail_weather(event, vk_api, day)
                elif payload_type == 'poster':
                    day = payload['day']
                    get_detail_poster(event, vk_api, day)
                elif payload_type == 'city':
                    answer = payload['answer']
                    process_city_answer(event, vk_api, answer)

            elif change_city_in_progress:
                update_user_city(event, vk_api)

            message_text = event.object.message['text'].lower()
            if message_text == 'начать':
                start(event, vk_api)
            elif message_text == 'пробка':
                get_traffic_status(event, vk_api)
            elif message_text == 'погода':
                get_weather(event, vk_api)
            elif message_text == 'афиша':
                get_poster(event, vk_api)
            elif message_text == 'валюта':
                get_currency(event, vk_api)
            elif message_text == 'изменить город':
                change_city(event, vk_api)


if __name__ == '__main__':
    main()
