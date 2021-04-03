from cryptoprices.execptions import ConfigException
from cryptoprices.util import load_notifiers_from_json_file
from cryptoprices.types import Notifier, State
import pytest


def test_load_notifiers():
    file = './res/config.test.json'

    result = load_notifiers_from_json_file(file)

    assert result == [
        Notifier(
            currency="EUR",
            crypto="BTC",
            price_type="spot",
            increment=50,
            internals=State(last_alert=None, last_price=None)
        ),
        Notifier(
            currency="USD",
            crypto="ETC",
            price_type="spot",
            increment=0.30,
            internals=State(last_alert=None, last_price=None)
        )
    ]


def test_load_notifiers_failure():
    file = './res/config.json'

    with pytest.raises(FileNotFoundError):
        load_notifiers_from_json_file(file)

    file = './res/invalid-config.json'

    with pytest.raises(ConfigException):
        load_notifiers_from_json_file(file)
