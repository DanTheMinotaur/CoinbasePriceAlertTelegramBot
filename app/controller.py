from app.coinbase_connection import get_valid_currency_codes, get_price
from app.telegram_connection import TelegramBot
from os import environ
import json
from json.decoder import JSONDecodeError
from datetime import datetime
from time import sleep


def check_config():
    for var in ['BOT_API_KEY', 'CHAT_ID', 'CURRENCY_CODE', 'CRYPTO_CODE', 'CHECK_EVERY', 'PRICE_CHANGE_INCREMENT']:
        try:
            environ[var]
        except KeyError:
            raise EnvironmentError(f'Environmental Variable "{var}" is not set.')


class CoinbaseBotController:
    PRICE_FILE = './data/last_price.json'

    def __init__(self):
        check_config()
        self.td_bot = TelegramBot(api_token=environ['BOT_API_KEY'], chat_id=environ['CHAT_ID'])
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
                self.td_bot.send_message(message, parse_mode='MarkdownV2')
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





