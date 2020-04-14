import unittest
from app.controller import CoinbaseBotController


class TestAlerts(unittest.TestCase):
    o = CoinbaseBotController('../config.json')

    def test_price_alert(self):
        self.o.price_alert = [200, 300, 400, 500]
        self.o.last_price_data = 150
        self.assertFalse(self.o.check_price_alert(170))
        self.o.last_price_data = 170
        self.assertFalse(self.o.check_price_alert(199.99))
        self.o.last_price_data = 170
        self.assertTrue(self.o.check_price_alert(210))
        self.o.last_price_data = 210
        self.assertFalse(self.o.check_price_alert(210))
        self.o.last_price_data = 210
        self.assertTrue(self.o.check_price_alert(350))
        self.o.last_price_data = 350
        self.assertTrue(self.o.check_price_alert(290))
        self.o.last_price_data = 290

    def test_price_increment(self):
        self.o.price_change_increment = [40, 100, 300]
        self.o.last_price_data = 10
        self.assertFalse(self.o.check_price_increment(45))
        self.assertTrue(self.o.check_price_increment(55))
        self.assertTrue(self.o.check_price_increment(2000))


if __name__ == '__main__':
    unittest.main()
