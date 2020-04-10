import unittest
from app.controller import CoinbaseBotController


class MyTestCase(unittest.TestCase):
    def test_schema_validation(self):
        self.assertTrue(isinstance(CoinbaseBotController.load_config('../config_example.json'), dict))


if __name__ == '__main__':
    unittest.main()
