from typing import Union
from dataclasses import dataclass


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

