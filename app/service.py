import asyncio
import aiohttp
from app.messaging.telegram import TelegramMessaging
from app.messaging.abstract import Messaging
from app.coinbase import get_price
from typing import List, Union
from math import floor
from dataclasses import dataclass
from app.execptions import CoinbaseResponseException, ResponseException
from app.util import logger

@dataclass
class State:
    last_price: float or None
    last_alert: Union[float, int] or None


@dataclass
class Notifier:
    currency: str
    crypto: str
    price_type: str
    increment: Union[float, int]
    internals: State
    chat_id: int


class BotService:
    def __init__(self, alerts: List[Notifier], messaging_client: Messaging = None):
        self._alerts = alerts
        self._session = aiohttp.ClientSession()
        self._tg = messaging_client

    async def set_prices(self):
        async def _set_price(n: Notifier):
            n.internals.last_price = await get_price(self._session, n.crypto, n.currency, n.price_type)
        await asyncio.gather(*[_set_price(a) for a in self._alerts])

    async def close_connections(self):
        await asyncio.gather(self._tg.close(), self._session.close())

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

    async def _update_notifier_price(self, n: Notifier) -> Notifier:
        try:
            current_price = await get_price(self._session, n.crypto, n.currency, n.price_type)

            nearest_increment = self.get_nearest_increment(current_price, n.increment)

            if n.internals.last_alert is None:
                n.internals.last_alert = nearest_increment
                await self._tg.send_message(
                    message=f'Bot Started\! Check if {n.crypto} changes by {self.fmt_float(n.increment)}{n.currency}',
                    chat_id=n.chat_id
                )

            if self.is_incremented(current_price, n):
                m = 'increased above' if current_price > n.internals.last_alert else 'decreased below'
                message = '\n'.join([
                    f'_{n.crypto}_ just {m} {self.fmt_float(nearest_increment)}.',
                    f'Current Price: {self.fmt_float(current_price)}{n.currency}',
                    f'Previous Price: {self.fmt_float(n.internals.last_price)}{n.currency}'
                ])
                await self._tg.send_message(
                    message=message,
                    chat_id=n.chat_id
                )
                n.internals.last_alert = nearest_increment

            n.internals.last_price = current_price
        except ResponseException as e:
            if isinstance(e, CoinbaseResponseException):
                logger.error('Could not get price data from Coinbase.', e)
            elif isinstance(e, TelegramMessaging):
                logger.error('Could not send message to telegram.', e)
        logger.debug(n)
        return n

    async def check_prices(self):
        await asyncio.gather(
            *[self._update_notifier_price(notifier) for notifier in self._alerts]
        )








