import asyncio

import aiohttp

from app.telegram import TelegramMessaging
from app.coinbase import get_price
from typing import List, Union
from math import floor
from dataclasses import dataclass
from app.execptions import CoinbaseResponseException


@dataclass
class State:
    last_price: float
    last_alert: Union[float, int]


@dataclass
class Notifier:
    currency: str
    crypto: str
    price_type: str
    increment: Union[float, int]
    internals: State


class BotManager:
    def __init__(self, alerts: List[Notifier]):
        self._alerts = alerts
        self._session = aiohttp.ClientSession()
        self._tg = TelegramMessaging()

    @staticmethod
    def get_nearest_increment(price: float, increment: int or float) -> float:
        return round(int(floor(price / float(increment))) * increment, 2)

    @staticmethod
    def is_incremented(current_price: float, notifier: Notifier) -> bool:
        last_alert = notifier.internals.last_alert
        return current_price >= (last_alert + notifier.increment) or current_price <= (last_alert - notifier.increment)

    async def _update_notifier_price(self, n: Notifier) -> Notifier:
        try:
            price_data = await get_price(self._session, n.crypto, n.currency, n.price_type)

            current_price = price_data['amount']

            if n.internals.last_alert is None:
                n.internals.last_alert = self.get_nearest_increment(current_price, n.increment)

            if self.is_incremented(current_price, n):
                await self._send_notification()

            n.internals.last_price = current_price
        except CoinbaseResponseException:
            print('Could not get price data from Coinbase.')

        return n

    async def _send_notification(self):
        print('Notification Sent')


    async def check_prices(self):
        await asyncio.gather(
            *[self._update_notifier_price(notifier) for notifier in self._alerts]
        )








