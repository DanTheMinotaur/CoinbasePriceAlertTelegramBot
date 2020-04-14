from app.controller import TelegramCommunication
from json import loads

with open('../config.json', 'r') as f:
    api_key = loads(f.read())['credentials']['bot_key']

bot = TelegramCommunication(api_key)

chats = bot.request('GET', 'getUpdates').json()['result']

for message in chats:
    message_type = None
    message_data = None
    if 'message' in message:
        message_type = 'chat'
        message_data = message['message']
    elif 'channel_post' in message:
        message_type = 'channel'
        message_data = message['channel_post']

    print(f'Message: "{message_data["text"]}" in {message_type} has ID: {message_data["chat"]["id"]}')

