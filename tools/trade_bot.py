import logging
import time
from typing import Any, Dict, Tuple

import requests
from requests.exceptions import HTTPError, Timeout

words = ['apple', 'coin', 'lite', 'strong', 'gold', 'silver', 'trust', 'happy']

base_url: str = 'http://localhost:5000'

logging.basicConfig(filename='bot.log')

Response = requests.models.Response


def action(
    rates: Dict[str, Any],
    old_rates: Dict[str, Any],
    balance: Dict[str, Any],
    token: str,
) -> None:
    for currency, rate in rates.items():
        amount = 1 if balance[currency] == 0 else int(balance[currency] / 2)
        if rates[currency] <= old_rates[currency]:
            payload = {
                'action': 'buy',
                'currency': currency,
                'amount': amount,
                'rate': rate,
            }
            requests.get(base_url + '/' + token, params=payload)
            logging.info('Looking to %s. Rate is %s, buying...', currency, rate)
        else:
            payload = {
                'action': 'sell',
                'currency': currency,
                'amount': amount,
                'rate': rate,
            }
            requests.get(base_url + '/' + token, params=payload)
            logging.info('Looking to %s. Rate is %s, selling...', currency, rate)


def setup() -> Tuple[str, Dict[str, Any], Dict[str, Any]]:
    token: str = requests.get(base_url + '/register').text
    old_rates: Dict[str, Any] = requests.get(base_url + '/rates').json()
    for currency, rate in old_rates.items():
        payload: Dict[str, Any] = {
            'action': 'buy',
            'currency': currency,
            'amount': 3,
            'rate': rate,
        }
        requests.get(base_url + '/' + token, params=payload)
    balance: Dict[str, Any] = requests.get(base_url + '/' + token + '/balance').json()
    return token, old_rates, balance


def loop(token: str, old_rates: Dict[str, Any], balance: Dict[str, Any]) -> None:
    try:
        while True:
            rates: Dict[str, Any] = requests.get(base_url + '/rates').json()
            logging.info('Got rates: %s', rates)
            action(rates, old_rates, balance, token)
            balance = requests.get(base_url + '/' + token + '/balance').json()
            logging.info(
                'Wheel of Samsara made another turn and balance is: \n%s ', balance
            )
            old_rates = rates
            time.sleep(10)
    except (ConnectionError, HTTPError, Timeout) as e:
        logging.warning('Error has occured: %s', e)


if __name__ == '__main__':
    t, old_r, bal = setup()
    loop(t, old_r, bal)
