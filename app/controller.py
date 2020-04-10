from os import environ
import json
from json.decoder import JSONDecodeError
from datetime import datetime
from time import sleep
from urllib.parse import urljoin
import requests
from jsonschema import validate

VALID_PRICE_TYPES = ['spot', 'buy', 'sell']


class TelegramConnectionException(Exception):
    def __init__(self, response: requests.Response):
        super().__init__(f'Bad Telegram response status {response.status_code}, "{response.json()}"')


class TelegramCommunication:
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


def check_config():
    for var in ['BOT_API_KEY', 'CHAT_ID', 'CURRENCY_CODE', 'CRYPTO_CODE', 'CHECK_EVERY', 'PRICE_CHANGE_INCREMENT']:
        try:
            environ[var]
        except KeyError:
            raise EnvironmentError(f'Environmental Variable "{var}" is not set.')


class CoinbaseBotController:
    PRICE_FILE = './data/last_price.json'

    @staticmethod
    def load_config(file: str) -> dict:
        with open('../config_schema.json') as f:
            schema = json.loads(f.read())
        with open(file, 'r') as f:
            config = json.loads(f.read())

        validate(instance=config, schema=schema)

        return config

    def __init__(self):
        check_config()
        self.td_bot = TelegramCommunication(api_token=environ['BOT_API_KEY'], chat_id=environ['CHAT_ID'])
        self.check_every = int(environ['CHECK_EVERY'])
        self.price_change_increment = self.round_two(environ['PRICE_CHANGE_INCREMENT'])
        self.currency_code = None
        self.crypto_code = None
        self.__set_currency_codes()
        self.last_price_data: float = self.load_price_from_file()['price']

    def start(self):
        while True:
            self.check_price()
            sleep(self.check_every)

    @staticmethod
    def round_two(amount: float or int or str) -> float:
        return round(float(amount), 2)

    def __set_currency_codes(self):
        valid_currencies = get_valid_currency_codes()

        def check_code(variable: str):
            code = environ[variable]
            cur_type = variable.split('_')[0].lower()
            key = f'{cur_type}_codes'
            if code in valid_currencies[key]:
                return code
            else:
                raise ValueError(
                    f'{cur_type.title()} Code [{code}] is not valid use: [{", ".join(valid_currencies[key])}]')

        self.currency_code = check_code('CURRENCY_CODE')
        self.crypto_code = check_code('CRYPTO_CODE')

    def check_price(self, check: bool = True):
        price_data = get_price(self.crypto_code, self.currency_code)
        if check:
            current_amount = self.round_two(price_data['amount'])
            price_change = None
            print(f"Current Price {current_amount} \n Last Stored Price {self.last_price_data}")
            if int(current_amount) >= int(self.last_price_data + self.price_change_increment):
                price_change = 'increased'
            elif int(current_amount) <= int(self.last_price_data - self.price_change_increment):
                price_change = 'decreased'

            if price_change:
                message = "{} {} by _{}_ is now *{}{}*".format(
                    self.crypto_code,
                    price_change,
                    self.round_two(abs(current_amount - self.last_price_data)),
                    current_amount,
                    self.currency_code
                )
                # message = f'{self.crypto_code} {price_change} by _{self.price_change_increment}_ is now' \
                #           f' *{current_amount}{self.currency_code}*\nPrevious Price: {self.last_price_data}'
                self.td_bot.send_message(message)
                self.last_price_data = self.write_price_to_file(current_amount)['price']

        return price_data

    def write_price_to_file(self, price: float or str) -> dict:
        data = {
            "price": float(price),
            "time": datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
        }
        with open(self.PRICE_FILE, 'w') as f:
            f.write(json.dumps(data))

        return data

    def load_price_from_file(self) -> dict:
        pricing_data = {"price": None, "time": None}
        try:
            with open(self.PRICE_FILE, 'r') as f:
                price_file_data = json.loads(f.read())
        except JSONDecodeError:
            price_file_data = {"Default": ""}

        for key in pricing_data.keys():
            if key not in price_file_data:
                return self.write_price_to_file(self.check_price(False)['amount'])

        return price_file_data




