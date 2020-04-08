# from app.telegram_connection import TelegramBot
#
from app.controller import CoinbaseBotController
from dotenv import load_dotenv
from time import sleep
load_dotenv('.env')

c = CoinbaseBotController()

while True:
    try:
        c.check_price()
        print(c.__dict__)
        sleep(5)
    except KeyboardInterrupt:
        print("closing")

