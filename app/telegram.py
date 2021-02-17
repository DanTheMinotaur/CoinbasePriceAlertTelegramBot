import aiohttp
from urllib.parse import urljoin
from app.execptions import TelegramResponseException, raise_for_response


class TelegramMessaging:
    def __init__(self, api_token: str):
        self.__token = api_token
        self._session = aiohttp.ClientSession()

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

    async def send_message(self, message: str, chat_id: str or int) -> dict:
        response = await self._request('sendMessage', json={
            'chat_id': chat_id,
            'text': message.replace('.', r'\.'),
            'parse_mode': 'MarkdownV2'
        })
        return await response.json()

