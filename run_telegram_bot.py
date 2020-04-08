from app.controller import CoinbaseBotController
from dotenv import load_dotenv
load_dotenv('.env')

c = CoinbaseBotController()

c.start()
