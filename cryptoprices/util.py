import json
from cryptoprices.types import Notifier, State
from typing import List
from cryptoprices.execptions import ConfigException


def load_notifiers_from_json_file(file_path: str) -> List[Notifier]:
    try:
        notifiers = list()
        with open(file_path, 'r') as j:
            data = json.load(j)
            for d in data:
                state = State(**d['internals'])
                notifier = Notifier(**d)
                notifier.internals = state
                notifiers.append(notifier)
        return notifiers
    except (TypeError, KeyError) as e:
        raise ConfigException(e)
