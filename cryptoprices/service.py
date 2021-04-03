import asyncio
import aiohttp
from .messaging.telegram import TelegramMessaging
from .messaging.abstract import Messaging
from .coinbase import get_price
from typing import List
from math import floor
from .execptions import CoinbaseResponseException, ResponseException
import logging
from .types import Notifier


class BotService:
    def __init__(self, alerts: List[Notifier], messaging_client: Messaging = None):
        self._alerts = alerts
        self._session = aiohttp.ClientSession()
        self._messenger = messaging_client

    async def set_prices(self):
        async def _set_price(n: Notifier):
            n.internals.last_price = await get_price(self._session, n.crypto, n.currency, n.price_type)
        await asyncio.gather(*[_set_price(a) for a in self._alerts])

    async def close_connections(self):
        await asyncio.gather(self._messenger.close(), self._session.close())

    @staticmethod
    def get_nearest_increment(price: float, increment: int or float) -> float:
        return round(int(floor(price / float(increment))) * increment, 2)

    @staticmethod
    def is_incremented(current_price: float, notifier: Notifier) -> bool:
        last_alert = notifier.internals.last_alert
        return current_price >= (last_alert + notifier.increment) or current_price <= (last_alert - notifier.increment)

    @staticmethod
    def fmt_float(num: float) -> str:
        return "{:.2f}".format(num)

    async def _check_price_increment(self, n: Notifier) -> str or None:
        message = None
        try:

            current_price = await get_price(self._session, n.crypto, n.currency, n.price_type)

            nearest_increment = self.get_nearest_increment(current_price, n.increment)

            if n.internals.last_alert is None:
                n.internals.last_alert = nearest_increment

            if self.is_incremented(current_price, n):
                m = 'increased above' if current_price > n.internals.last_alert else 'decreased below'
                message = '\n'.join([
                    f'_{n.crypto.upper()}_ just {m} {self.fmt_float(nearest_increment)}{n.currency}',
                    f'Current Price: {self.fmt_float(current_price)}{n.currency}',
                    f'Previous Price: {self.fmt_float(n.internals.last_price)}{n.currency}'
                ])
                n.internals.last_alert = nearest_increment

            n.internals.last_price = current_price
        except ResponseException as e:
            if isinstance(e, CoinbaseResponseException):
                logging.error('Could not get price data from Coinbase.', e)
            elif isinstance(e, TelegramMessaging):
                logging.error('Could not send message to telegram.', e)
        logging.debug(n)
        return message

    async def check_prices(self):
        messages = await asyncio.gather(
            *[self._check_price_increment(notifier) for notifier in self._alerts]
        )
        messages = list(filter(None, list(messages)))

        if messages:
            messages = '\n'.join(messages)
            await self._messenger.send_message(messages)


async def create_bot_service(alerts: List[Notifier], messaging_client: Messaging = None) -> BotService:
    cryptos = [n.crypto for n in alerts]
    await messaging_client.send_message(f'Bot Service Started\n{", ".join(cryptos)}')
    return BotService(alerts, messaging_client)





