from os import environ, listdir, path

from cryptoprices.messaging.telegram import TelegramMessaging
from cryptoprices.service import create_bot_service
from cryptoprices.util import load_notifiers_from_json_file

import logging
import asyncio


async def run():
    try:
        chat_id = environ['TG_CHAT_ID']
        api_key = environ['TG_API_KEY']
    except KeyError:
        raise RuntimeError('Missing Telegram Variable')

    _path = './alerts'

    alert_files = [f for f in listdir(_path) if path.isfile(path.join(_path, f)) and f.endswith('.json')]

    alerts = list()

    for f in alert_files:
        alerts.extend(
            load_notifiers_from_json_file(path.join(_path, f))
        )

    bot = await create_bot_service(alerts, TelegramMessaging(api_token=api_key, chat_id=chat_id))
    try:
        logging.info('Bot Starting')
        logging.info('Setting Prices')
        await bot.set_prices()
        logging.info('Prices Set')
        while True:
            await asyncio.sleep(30)
            logging.info('Checking Prices')
            await bot.check_prices()
            logging.info('Prices Checked')
    finally:
        await bot.close_connections()

if __name__ == "__main__":
    asyncio.run(run())
