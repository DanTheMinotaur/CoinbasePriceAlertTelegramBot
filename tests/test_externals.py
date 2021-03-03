from cryptoprices.coinbase import get_price
from cryptoprices.messaging.telegram import TelegramMessaging
from cryptoprices.execptions import CoinbaseResponseException, TelegramResponseException
from aioresponses import aioresponses
import aiohttp
import asyncio
import pytest


def test_get_price():
    async def _tester():
        session = aiohttp.ClientSession()
        with aioresponses() as mock:
            mock.get('https://api.coinbase.com/v2/prices/BTC-EUR/spot', payload={
                "data": {
                    "base": "BTC",
                    "currency": "EUR",
                    "amount": "47720.27"
                }
            })

            price = await get_price(session, 'BTC', 'EUR', 'spot')
            assert isinstance(price, float)
            assert price == 47720.27
        await session.close()

    asyncio.run(_tester())


def test_get_price_failures():
    async def _tester():
        session = aiohttp.ClientSession()
        with aioresponses() as mock:
            mock.get('https://api.coinbase.com/v2/prices/EUR-BTC/spot', payload={
                "errors": [
                    {
                        "id": "not_found",
                        "message": "Invalid currency"
                    }
                ]
            }, status=404)

            with pytest.raises(ValueError):
                await get_price(session, 'EUR', 'BTC', 'bad')

            with pytest.raises(CoinbaseResponseException):
                await get_price(session, 'EUR', 'BTC', 'spot')
        await session.close()

    asyncio.run(_tester())


def test_telegram():
    async def _tester():
        with aioresponses() as mock:
            token = 'aaa'
            tg = TelegramMessaging(api_token=token)
            valid_response = {
                "ok": True,
                "result": {
                    "message_id": 1000,
                    "sender_chat": {
                        "id": -100000000,
                        "title": "Some Chat",
                        "type": "channel"
                    },
                    "chat": {
                        "id": -100000000,
                        "title": "Some Chat",
                        "type": "channel"
                    },
                    "date": 1613947287,
                    "text": "Hello"
                }
            }
            mock.post(f'https://api.telegram.org/bot{token}/sendMessage', payload=valid_response)

            result = await tg.send_message(message='Hello', chat_id=-100000000)
            assert result == valid_response
            await tg.close()

            token = 'bbb'
            tg = TelegramMessaging(api_token=token)
            mock.post(f'https://api.telegram.org/bot{token}/sendMessage', payload={
                "ok": False,
                "error_code": 401,
                "description": "Unauthorized"
            }, status=401)

            with pytest.raises(TelegramResponseException):
                await tg.send_message('Hello', chat_id=-100000000)

            await tg.close()

    asyncio.run(_tester())
