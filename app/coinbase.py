from urllib.parse import urljoin
import aiohttp
import asyncio
from app.execptions import CoinbaseResponseException, raise_for_response


@raise_for_response(CoinbaseResponseException)
async def coinbase_request(endpoint: str, session: aiohttp.ClientSession, **kwargs) -> aiohttp.ClientResponse:
    method = kwargs.get('method', 'GET')
    json = kwargs.get('json', {})
    url = urljoin('https://api.coinbase.com/v2/', endpoint)
    return await session.request(method, url, json=json)


async def _to_json(response: aiohttp.ClientResponse) -> dict:
    return await response.json()


async def get_currency_codes(session: aiohttp.ClientSession) -> dict:
    currencies, exchange = await asyncio.gather(
        _to_json(await coinbase_request('currencies', session)),
        _to_json(await coinbase_request('exchange-rates', session))
    )
    currencies = set([code['id'] for code in currencies['data']])
    exchange = set(exchange['data']['rates'].keys())
    return {
        "crypto": exchange.difference(currencies),
        "currencies": currencies
    }


async def get_price(session: aiohttp.ClientSession, crypto: str, fiat: str, price_type: str = 'spot') -> float:
    price_types = ('spot', 'buy', 'sell',)
    if price_type not in price_types:
        raise ValueError(f'Price type {price_type} is not valid, used [f{", ".join(price_types)}]')
    resp = await coinbase_request(f'prices/{crypto}-{fiat}/{price_type}', session)
    price_data = await _to_json(resp)
    return float(price_data['data']['amount'])
