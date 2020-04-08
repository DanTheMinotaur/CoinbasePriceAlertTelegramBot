import unittest
from app.telegram_connection import TelegramBot
from dotenv import load_dotenv
from os import environ
import telegram

load_dotenv('../.env')

TOKEN = environ['BOT_API_KEY']
CHANNEL_ID = environ['CHAT_ID']


class TestBotConnectivity(unittest.TestCase):
    bot = TelegramBot(TOKEN, CHANNEL_ID)

    def test_bot_creation(self):
        self.assertTrue('username' in self.bot.bot_details)

    def test_send_plain_message(self):
        self.assertTrue('message_id' in self.bot.send_message('Hello World [Testing]'))

    def test_send_md_message(self):
        result = self.bot.send_message("*bold* _italic_ `fixed width font` [link](http://google.com)\.", parse_mode=telegram.ParseMode.MARKDOWN_V2)
        self.assertTrue('message_id' in result)


if __name__ == '__main__':
    unittest.main()
