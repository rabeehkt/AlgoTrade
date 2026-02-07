import unittest
from unittest.mock import MagicMock

from kite_orders import KiteOrderManager
from main import calculate_pnl


class TestTradingFunctions(unittest.TestCase):
    def setUp(self):
        self.kite = MagicMock()
        self.manager = KiteOrderManager(self.kite)

    def test_place_buy_order_returns_order_details(self):
        self.kite.place_order.return_value = {"order_id": "OID-1"}
        self.kite.orders.return_value = [
            {
                "order_id": "OID-1",
                "average_price": 123.45,
                "status": "COMPLETE",
                "filled_quantity": 1,
                "pending_quantity": 0,
                "tradingsymbol": "INFY",
                "transaction_type": "BUY",
                "quantity": 1,
                "product": "MIS",
                "order_timestamp": "2024-01-01 09:15:00",
                "exchange_timestamp": "2024-01-01 09:15:01",
            }
        ]

        result = self.manager.place_mis_market_order("INFY", 1, "BUY")

        self.assertEqual(result["order_id"], "OID-1")
        self.assertEqual(result["average_price"], 123.45)
        self.kite.place_order.assert_called_once()

    def test_invalid_side_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.manager.place_mis_market_order("INFY", 1, "HOLD")

    def test_calculate_pnl(self):
        self.assertEqual(calculate_pnl(1500, 1550, 2), 100)


if __name__ == "__main__":
    unittest.main()
