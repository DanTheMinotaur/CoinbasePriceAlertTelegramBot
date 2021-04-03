import aiohttp
from urllib.parse import urljoin
from cryptoprices.execptions import TelegramResponseException, raise_for_response
import logging
from cryptoprices.messaging.abstract import Messaging


class TelegramMessaging(Messaging):
    def __init__(self, api_token: str, chat_id: int or None = None):
        self.__token = api_token
        self._session = aiohttp.ClientSession()
        self._chat_id = chat_id

    @property
    def chat_id(self):
        return self._chat_id

    @chat_id.setter
    def chat_id(self, chat_id: int):
        self._chat_id = chat_id

    @raise_for_response(TelegramResponseException)
    async def _request(self, endpoint: str, **kwargs) -> aiohttp.ClientResponse:
        method = kwargs.get('method', 'POST')
        json = kwargs.get('json', {})
        url = urljoin(f'https://api.telegram.org/bot{self.__token}/', endpoint)
        return await self._session.request(method, url, json=json)

    async def close(self):
        await self._session.close()

    async def get_me(self):
        response = await self._request('getMe', method='GET')
        return await response.json()

    async def send_message(self, message: str, chat_id: str or int = None) -> dict:
        if chat_id is None and self._chat_id:
            chat_id = self._chat_id
        elif chat_id is None and self._chat_id is None:
            raise ValueError('No Telegram Chat ID set.')

        logging.info(f'Sending Telegram Message: {message}')

        response = await self._request('sendMessage', json={
            'chat_id': chat_id,
            'text': message.replace('.', r'\.'),
            'parse_mode': 'MarkdownV2'
        })
        res = await response.json()
        return res
