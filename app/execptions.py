from aiohttp import ClientResponse


class ResponseException(Exception):
    def __init__(self, status: int, response_content):
        super().__init__(f' Bad response status: {status}, content "{response_content}"')


class TelegramResponseException(ResponseException):
    def __init__(self, *args):
        super().__init__(*args)


class CoinbaseResponseException(ResponseException):
    def __init__(self, *args):
        super().__init__(*args)


def raise_for_response(exception):
    def decorator(func):
        async def wrap(*args, **kwargs) -> ClientResponse:
            resp: ClientResponse = await func(*args, **kwargs)
            if resp.status != 200:
                raise exception(resp.status, await resp.json())
            return resp

        return wrap
    return decorator
