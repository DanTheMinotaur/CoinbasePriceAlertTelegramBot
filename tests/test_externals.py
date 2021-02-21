from app.coinbase import get_price
from app.execptions import CoinbaseResponseException
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

