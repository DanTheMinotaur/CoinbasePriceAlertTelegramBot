from os import environ
import json
from json.decoder import JSONDecodeError
from datetime import datetime
from time import sleep
from urllib.parse import urljoin
import requests
from jsonschema import validate
from app.schema import CONFIG_SCHEMA

VALID_PRICE_TYPES = ['spot', 'buy', 'sell']


class TelegramConnectionException(Exception):
    def __init__(self, response: requests.Response):
        super().__init__(f'Bad Telegram response status {response.status_code}, "{response.json()}"')


class TelegramCommunication:
    DEBUG = True

    def __init__(self, api_token: str, chat_id: int or str = None):
        self.token = api_token
        self.chat_id: str or int = chat_id

    def request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        config = {
            'method': method,
            'url': urljoin(f'https://api.telegram.org/bot{self.token}/', endpoint)
        }
        if kwargs:
            config.update(kwargs)
        response = requests.request(**config)
        if response.status_code == 200:
            return response
        else:
            raise TelegramConnectionException(response)

    def get_me(self) -> dict:
        return self.request('GET', 'getMe').json()

    def send_message(self, message: str) -> dict:
        if self.DEBUG:
            print(f'DEBUG: "{message}" sent to Telegram')
        else:
            print(f'Message "{message}" Sent to Telegram')
            return self.request('POST', 'sendMessage', **{
                'headers': {
                    'Content-Type': 'application/json'
                },
                'data': json.dumps({
                    'chat_id': self.chat_id,
                    'text': message.replace('.', r'\.'),
                    'parse_mode': 'MarkdownV2'
                })
            }).json()


class CoinbaseConnectionException(Exception):
    def __init__(self, response: requests.Response):
        super().__init__(f'Bad Coinbase response status {response.status_code}, "{response.json()}"')


def get_coinbase(endpoint: str) -> requests.Response:
    response = requests.get(f'https://api.coinbase.com/v2/{endpoint}')
    if response.status_code == 200:
        return response
    raise CoinbaseConnectionException(response)


def get_valid_currency_codes() -> dict:
    currency_codes = set([code['id'] for code in get_coinbase('currencies').json()['data']])
    all_currency_codes = set(get_coinbase('exchange-rates').json()['data']['rates'].keys())
    return {
        "crypto_codes": all_currency_codes.difference(currency_codes),
        "currency_codes": currency_codes
    }


def get_price(from_currency_code: str, to_currency_code: str, price_type: str = 'spot') -> dict:
    if price_type not in VALID_PRICE_TYPES:
        raise ValueError(f'Price type {price_type} is not valid, used [f{", ".join(VALID_PRICE_TYPES)}]')
    return get_coinbase(f'prices/{from_currency_code}-{to_currency_code}/{price_type}').json()['data']


class CoinbaseBotController:
    @staticmethod
    def load_config(file: str) -> dict:
        with open(file, 'r') as f:
            config = json.loads(f.read())

        validate(instance=config, schema=CONFIG_SCHEMA)

        return config

    @staticmethod
    def to_list(obj) -> list:
        return list(obj) if not isinstance(obj, list) else obj

    def set_alerts(self, config: dict):
        config = config['alerts']
        if 'price_alerts' in config:
            self.price_change_increment = self.to_list(config['price_alerts'])
        if 'price_increments' in config:
            self.price_change_increment = self.to_list(config['price_increments'])

    def __init__(self, config_file: str = './config.json'):
        config = self.load_config(config_file)
        self.td_bot = TelegramCommunication(
            api_token=config['credentials']['bot_key'], chat_id=config['credentials']['chat_id'])
        self.check_every = config['prices']['check']
        self.price_change_increment = None
        self.price_alert = None
        self.currency_code = None
        self.crypto_code = None
        self.set_alerts(config)
        self.set_alerts(config)
        self.__set_currency_codes(config)
        self.last_price_data: float = 0.0

    def start(self):
        while True:
            if self.last_price_data == 0.0:
                self.last_price_data = get_price(self.crypto_code, self.currency_code)['amount']
                self.td_bot.send_message(f'Bot Started: Current {self.crypto_code} price is: {self.last_price_data}{self.currency_code}')
            self.check_price(get_price(self.crypto_code, self.currency_code)['amount'])
            sleep(self.check_every)

    @staticmethod
    def round_two(amount: float or int or str) -> float:
        return round(float(amount), 2)

    def __set_currency_codes(self, config):
        config = config['prices']
        valid_currencies = get_valid_currency_codes()

        def check_code(variable: str):
            code = config[variable]
            cur_type = variable.split('_')[0].lower()
            key = f'{cur_type}_codes'
            if code in valid_currencies[key]:
                return code
            else:
                raise ValueError(
                    f'{cur_type.title()} Code [{code}] is not valid use: [{", ".join(valid_currencies[key])}]')

        self.currency_code = check_code('currency_code')
        self.crypto_code = check_code('crypto_code')

    def check_price(self, current_price: float or int) -> float:
        current_amount = self.round_two(current_price)
        print(f"Current Price {current_amount} \nLast Stored Price {self.last_price_data}")
        if self.check_price_alert(current_amount) or self.check_price_increment(current_amount):
            self.last_price_data = current_amount
        return current_amount

    def check_price_increment(self, current_amount: int or float):
        if self.price_change_increment:
            price_change = None
            for increment in self.price_change_increment:
                if int(current_amount) >= int(self.last_price_data + increment):
                    price_change = 'increased'
                elif int(current_amount) <= int(self.last_price_data - increment):
                    price_change = 'decreased'

                if price_change:
                    message = "{} {} by _{}_ is now *{}{}*".format(
                        self.crypto_code,
                        price_change,
                        self.round_two(abs(current_amount - self.last_price_data)),
                        current_amount,
                        self.currency_code
                    )
                    self.td_bot.send_message(message)
                    return True
        return False

    def check_price_alert(self, current_amount: int or float):
        if self.price_alert:
            for price in self.price_alert:
                if current_amount >= price > self.last_price_data or current_amount <= price < self.last_price_data:
                    self.td_bot.send_message('*Price Alert!* {} just hit {} and is now {}{}!'.format(
                        self.crypto_code,
                        price,
                        current_amount,
                        self.currency_code
                    ))
                    return True
        return False








