import unittest
from app.coinbase_connection import get, get_valid_currency_codes, get_price


class MyTestCase(unittest.TestCase):
    def test_get_response(self):
        self.assertEqual(get('currencies').status_code, 200)

    def test_get_currency_codes(self):
        print(get_valid_currency_codes())
        # self.assertTrue(isinstance(get_valid_currency_codes(), set))

    def test_get_price(self):
        print(get_price('EUR', 'BTC'))


if __name__ == '__main__':
    unittest.main()
