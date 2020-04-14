CONFIG_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "$id": "https://github.com/DanTheMinotaur/CoinbasePriceAlertTelegramBot/config_example.json",
    "type": "object",
    "title": "The Root Schema",
    "description": "The root schema comprises the entire JSON document.",
    "required": [
        "credentials",
        "alerts",
        "prices",
        "price_file"
    ],
    "properties": {
        "credentials": {
            "$id": "#/properties/credentials",
            "type": "object",
            "title": "The Credentials Schema",
            "description": "Telegram bot credentials. ",
            "default": {},
            "examples": [
                {
                    "bot_key": "ASMKJDNAKJDNKSAJNKDJsa",
                    "chat_id": -12345.0
                }
            ],
            "required": [
                "chat_id",
                "bot_key"
            ],
            "properties": {
                "chat_id": {
                    "$id": "#/properties/credentials/properties/chat_id",
                    "type": "integer",
                    "title": "The chat ID the bot is to post in. ",
                    "description": "An explanation about the purpose of this instance.",
                    "default": 0,
                    "examples": [
                        -12345
                    ]
                },
                "bot_key": {
                    "$id": "#/properties/credentials/properties/bot_key",
                    "type": "string",
                    "title": "The Auth Key for the telegram bot. ",
                    "description": "An explanation about the purpose of this instance.",
                    "default": "",
                    "examples": [
                        "ASMKJDNAKJDNKSAJNKDJsa"
                    ]
                }
            }
        },
        "alerts": {
            "$id": "#/properties/alerts",
            "type": "object",
            "title": "The Alerts Schema",
            "description": "Different alerts available. ",
            "default": {},
            "examples": [
                {
                    "price_alerts": [
                        2000.0,
                        3000.0,
                        4000.0,
                        5000.0
                    ],
                    "price_increments": [
                        50.0,
                        100.0,
                        200.0
                    ]
                }
            ],
            "anyOf": [
                {"required": ["price_alerts"]},
                {"required": ["price_increments"]}
            ],
            "properties": {
                "price_alerts": {
                    "$id": "#/properties/alerts/properties/price_alerts",
                    "type": "array",
                    "title": "The Price_alerts Schema",
                    "description": "An explanation about the purpose of this instance.",
                    "default": [],
                    "items": {
                        "$id": "#/properties/alerts/properties/price_alerts/items",
                        "type": "number",
                        "title": "Price Alert Points",
                        "description": "Sends alert if price goes over or above any of the values in array.",
                        "default": 0,
                        "examples": [
                            2000,
                            3000,
                            4000,
                            5000
                        ]
                    }
                },
                "price_increments": {
                    "$id": "#/properties/alerts/properties/price_increments",
                    "type": "array",
                    "title": "The Price_increments Schema",
                    "description": "An explanation about the purpose of this instance.",
                    "default": [],
                    "items": {
                        "$id": "#/properties/alerts/properties/price_increments/items",
                        "type": "number",
                        "title": "Price Increment Alerts",
                        "description": "Set these to alert when the selected currency increases or decreases by this amount. ",
                        "default": 0,
                        "examples": [
                            50,
                            100,
                            200
                        ]
                    }
                }
            }
        },
        "prices": {
            "$id": "#/properties/prices",
            "type": "object",
            "title": "The Prices Schema",
            "description": "Configuration for collecting price data. ",
            "default": {},
            "examples": [
                {
                    "price_type": "spot",
                    "currency_code": "EUR",
                    "check": 60.0,
                    "crypto_code": "BTC"
                }
            ],
            "required": [
                "price_type",
                "currency_code",
                "crypto_code",
                "check"
            ],
            "properties": {
                "price_type": {
                    "$id": "#/properties/prices/properties/price_type",
                    "type": "string",
                    "title": "The Price_type Schema",
                    "description": "Coinbase has 3 price types; spot, sell and buy.",
                    "default": "",
                    "examples": [
                        "spot"
                    ]
                },
                "currency_code": {
                    "$id": "#/properties/prices/properties/currency_code",
                    "type": "string",
                    "title": "The Currency_code Schema",
                    "description": "Currency code to convert from.",
                    "default": "",
                    "examples": [
                        "EUR"
                    ]
                },
                "crypto_code": {
                    "$id": "#/properties/prices/properties/crypto_code",
                    "type": "string",
                    "title": "The Crypto_code Schema",
                    "description": "The Cryptocurrency to check price against.",
                    "default": "",
                    "examples": [
                        "BTC"
                    ]
                },
                "check": {
                    "$id": "#/properties/prices/properties/check",
                    "type": ["integer", "float"],
                    "title": "The Check Schema",
                    "description": "Time for between price checks",
                    "default": 60,
                    "examples": [
                        60
                    ]
                }
            }
        }
    }
}