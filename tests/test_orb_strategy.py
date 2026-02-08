import unittest
from unittest.mock import MagicMock, patch
import datetime
from orb_strategy import OrbStrategy
from config import CONFIG

class TestOrbStrategy(unittest.TestCase):
    def setUp(self):
        self.kite = MagicMock()
        self.strategy = OrbStrategy(self.kite, "NSE:INFY")
        
    def test_calculate_opening_range_insufficient_time(self):
        # Mock time to be before ORB end time
        mock_now = datetime.datetime(2024, 1, 1, 9, 20) # 5 mins after open
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_now
            # Ensure other datetime attributes are preserved if needed, though mostly we just need now()
            mock_datetime.side_effect = lambda *args, **kw: datetime.datetime(*args, **kw)
            
            high, low = self.strategy.calculate_opening_range()
            self.assertIsNone(high)
            self.assertIsNone(low)

    def test_calculate_opening_range_success(self):
        # Mock time to be after ORB end time
        mock_now = datetime.datetime(2024, 1, 1, 9, 31) # 16 mins after open
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_now
            mock_datetime.side_effect = lambda *args, **kw: datetime.datetime(*args, **kw)
            
            # Mock historical data
            self.kite.historical_data.return_value = [
                {'high': 100, 'low': 90},
                {'high': 110, 'low': 95},
                {'high': 105, 'low': 92}
            ]
            
            high, low = self.strategy.calculate_opening_range()
            self.assertEqual(high, 110)
            self.assertEqual(low, 90)
            self.assertTrue(self.strategy.range_calculated)

    def test_check_signal_buy(self):
        self.strategy.range_calculated = True
        self.strategy.orb_high = 100
        self.strategy.orb_low = 90
        
        # Test Buy
        signal = self.strategy.check_signal(101)
        self.assertEqual(signal, "BUY")
        
    def test_check_signal_sell(self):
        self.strategy.range_calculated = True
        self.strategy.orb_high = 100
        self.strategy.orb_low = 90
        
        # Test Sell
        signal = self.strategy.check_signal(89)
        self.assertEqual(signal, "SELL")
        

    def test_check_signal_recalculates_for_new_date(self):
        self.strategy.range_calculated = True
        self.strategy.orb_high = 100
        self.strategy.orb_low = 90
        self.strategy.range_date = datetime.date(2024, 1, 1)

        def fake_calculate(now):
            self.strategy.orb_high = 110
            self.strategy.orb_low = 95
            self.strategy.range_calculated = True
            self.strategy.range_date = now.date()
            return 110, 95

        self.strategy.calculate_opening_range = MagicMock(side_effect=fake_calculate)

        signal = self.strategy.check_signal(111, datetime.datetime(2024, 1, 2, 9, 35))

        self.strategy.calculate_opening_range.assert_called_once()
        self.assertEqual(signal, "BUY")

    def test_check_signal_none(self):
        self.strategy.range_calculated = True
        self.strategy.orb_high = 100
        self.strategy.orb_low = 90
        
        # Test No Signal
        signal = self.strategy.check_signal(95)
        self.assertIsNone(signal)

if __name__ == '__main__':
    unittest.main()
