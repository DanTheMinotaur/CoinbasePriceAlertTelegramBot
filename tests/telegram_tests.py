import unittest
from dotenv import load_dotenv
from os import environ
from app.controller import TelegramCommunication

load_dotenv('../.env')

TOKEN = environ['BOT_API_KEY']
CHANNEL_ID = environ['CHAT_ID']


class TestBotConnectivity(unittest.TestCase):
    bot = TelegramCommunication(TOKEN, CHANNEL_ID)

    def test_connection(self):
        r = self.bot.get_me()
        self.assertTrue(r['ok'])

    def test_send_message(self):
        r = self.bot.send_message('This is a test')
        self.assertTrue(r['ok'])


if __name__ == '__main__':
    unittest.main()
