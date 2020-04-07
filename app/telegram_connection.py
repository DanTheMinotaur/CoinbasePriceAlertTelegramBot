from telegram import Bot
from telegram.error import Unauthorized


class TelegramBot:
    def __init__(self, api_token: str, chat_id: int or str = None):
        """

        :param api_token:
        :param chat_id:
        """
        try:
            self.bot: Bot = Bot(api_token)
            self.chat_id: str or int = chat_id
            self.bot_details = self.bot.get_me().__dict__
        except Unauthorized:
            print("Invalid Telegram Bot Token")
            exit()

    def send_message(self, message: str, **kwargs):
        payload = {
            "text": message,
            "chat_id": self.chat_id
        }
        if kwargs:
            payload.update(kwargs)
        return self.bot.send_message(text=message, chat_id=self.chat_id)