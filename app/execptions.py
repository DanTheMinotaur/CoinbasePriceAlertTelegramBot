from aiohttp import ClientResponse
from app.util import logger


class ResponseException(Exception):
    def __init__(self, status: int, response_content: str, _self):
        message = f'{self.get_class_name(_self)}; Bad response status: {status}, content "{response_content}"'
        logger.error(message)
        super().__init__(message)

    @staticmethod
    def get_class_name(instance):
        return instance.__class__.__name__


class TelegramResponseException(ResponseException):
    def __init__(self, status: int, response_content: dict):
        super().__init__(status, response_content['description'], self)


class CoinbaseResponseException(ResponseException):
    def __init__(self, status: int, response_content: dict):
        super().__init__(status, ', '.join([e['message'] for e in response_content['errors']]), self)


def raise_for_response(exception):
    def decorator(func):
        async def wrap(*args, **kwargs) -> ClientResponse:
            resp: ClientResponse = await func(*args, **kwargs)
            if resp.status != 200:
                raise exception(resp.status, await resp.json())
            return resp

        return wrap
    return decorator
