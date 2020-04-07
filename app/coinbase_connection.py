import requests

VALID_PRICE_TYPES = ['spot', 'buy', 'sell']


class CoinbaseConnectionException(Exception):
    def __init__(self, response: requests.Response):
        message = f'Bad Coinbase response status {response.status_code}, "{response.json()}"'
        super().__init__(message)


def get(endpoint: str) -> requests.Response:
    response = requests.get(f'https://api.coinbase.com/v2/{endpoint}')
    if response.status_code == 200:
        return response
    raise CoinbaseConnectionException(response)


def get_valid_currency_codes() -> dict:
    currency_codes = set([code['id'] for code in get('currencies').json()['data']])
    all_currency_codes = set(get('exchange-rates').json()['data']['rates'].keys())
    return {
        "crypto_codes": all_currency_codes.difference(currency_codes),
        "currency_codes": currency_codes
    }


def get_price(from_currency_code: str, to_currency_code: str, price_type: str = 'spot') -> dict:
    if price_type not in VALID_PRICE_TYPES:
        raise ValueError(f'Price type {price_type} is not valid, used [f{", ".join(VALID_PRICE_TYPES)}]')
    return get(f'prices/{from_currency_code}-{to_currency_code}/{price_type}').json()['data']
