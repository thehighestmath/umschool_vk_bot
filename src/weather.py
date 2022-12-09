import datetime
import os

import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get("WEATHER_TOKEN")


def get_city_id(city):
    data = requests.get(
        "http://api.openweathermap.org/data/2.5/find",
        params={
            'q': f'{city},RU',
            'type': 'like',
            'units': 'metric',
            'APPID': TOKEN
        }
    ).json()
    return data['list'][0]['id']


def get_weather_today(city_id):
    data = requests.get(
        "http://api.openweathermap.org/data/2.5/weather",
        params={
            'id': city_id,
            'units': 'metric',
            'lang': 'ru',
            'APPID': TOKEN
        }
    ).json()
    return data['main']['temp']


def get_weather_tomorrow(city_id):
    data = requests.get(
        "http://api.openweathermap.org/data/2.5/forecast",
        params={
            'id': city_id,
            'units': 'metric',
            'lang': 'ru',
            'APPID': TOKEN
        }
    ).json()
    tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
    tomorrow_str = tomorrow.strftime('%Y-%m-%d')
    tomorrow_data = list(
        map(
            lambda x: x['main']['temp'],
            filter(lambda x: x['dt_txt'].split()[0] == tomorrow_str, data['list'])
        )
    )
    return int(sum(tomorrow_data) / len(tomorrow_data))


def get_weather_in_city(city, day):
    city_id = get_city_id(city)
    if day == 'сегодня':
        return int(get_weather_today(city_id))
    if day == 'завтра':
        return int(get_weather_tomorrow(city_id))
    return 0


if __name__ == '__main__':
    print(get_weather_in_city('уфа', 'завтра'))
