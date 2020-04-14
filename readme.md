

## Installation
### PIP
`pip install -r requirements.txt`

## Setting up a bot on Telegram
- [First create a bot on Telegram here](https://t.me/botfather)
- Click Start and type `/newbot`.
- Give the Bot an name like `My BTC Bot`
- Then give it a username
- Then once that is set up, click the link to the bot so you can find it. 

You will then get an API key for the bot, which can then be placed in `config.json` at the key `bot_key`.

To get the bot to post, you'll need to add it to a channel and then add the channel to the config.

## Get a Channel ID to post alerts to. 
- Create a channel using the Telegram app. 
- Send a message to the bot directly (For some reason this needs to happen for it to read messages).
- Add the bot to the channel (as admin), and send a message so you can find the chat ID.  
- Run the file ./app/util.py which will print a list of messages the bot has received, along with their IDs. 
- Get the chat ID and put it into `config.json`

## Set up price alerts
In `config.json` put the alerts you want to receive into the arrays. You need atleast one of 
either `price_alerts` or `price_increments` otherwise it won't start. 

### price_alerts
These are when the currency increases or decreases over a certain value. So if BTC hit $6000 it will send a message alerting you to that. 

### price_increments
This can be set if you want an alert everytime it goes up or down by `n` amount. So if you set an increment for $50 it will alert you if the price changes from $6000 to $6500

## Set up prices

### price_type
Coinbase has 3 different price types, `[spot, buy, sell]` choose which one the bot will read from.

### currency_code and crypto_code
Set the currencies to check here, so if you want to set alerts for Bitcoin to Euro set the below. 

### Info
All price alerts share the checking price, if an alert is triggered when it hits $3000, and an increment is set 
for $100 dollars then it will only alert you when it hits $3100. 

### Check
This is the amount of time in seconds to check Coinbase for price changes. 

## Example config.json
```json
{
  "credentials": {
    "chat_id": -12345,
    "bot_key": "TheBotIDFromTelegram"
  },
  "alerts": {
    "price_alerts": [2000, 3000, 4000, 5000],
    "price_increments": [50, 100, 200]
  },
  "prices": {
    "price_type": "spot",
    "currency_code": "EUR",
    "crypto_code":  "BTC",
    "check": 60
  }
}
```

## Running it
After you have the `config.json` set up you can run it two ways.

### Python
`python run_telegram_bot.py`

### Docker
`docker-compose up -d`
