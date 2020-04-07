import unittest
from app.telegram_connection import TelegramBot
from dotenv import load_dotenv
from os import environ
from telegram import ParseMode

load_dotenv('../.env')

TOKEN = environ['BOT_API_KEY']
CHANNEL_ID = environ['CHANNEL_ID']


class TestBotConnectivity(unittest.TestCase):
    bot = TelegramBot(TOKEN, CHANNEL_ID)

    def test_bot_creation(self):
        self.assertTrue('username' in self.bot.bot_details)

    def test_send_plain_message(self):
        self.assertTrue('message_id' in self.bot.send_message('Hello World [Testing]'))

    def test_send_md_message(self):
        self.assertTrue('message_id' in self.bot.send_message('*Bold* [Testing]', parse_mode=ParseMode.MARKDOWN_V2))


if __name__ == '__main__':
    unittest.main()
