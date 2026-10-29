import unittest

from orders import shipping


class ShippingTest(unittest.TestCase):
    def test_standard_price(self) -> None:
        self.assertEqual(shipping("standard"), 7)
