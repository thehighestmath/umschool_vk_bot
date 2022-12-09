import os
from typing import Dict

import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get("CURRENCY_TOKEN")

headers = {'apikey': TOKEN}


def get_currency_rates() -> Dict[str, float]:
    currencies = ['USD', 'EUR', 'AUD', 'AZN', 'AMD']
    d = {}
    for currency in currencies:
        params = {
            'amount': 1,
            'from': currency,
            'to': 'RUB'
        }
        r = requests.get(
            'https://api.apilayer.com/currency_data/convert',
            params=params, headers=headers
        ).json()
        d[currency] = r.get('result', 0)
    return d


if __name__ == '__main__':
    r = get_currency_rates()
    print(r)
