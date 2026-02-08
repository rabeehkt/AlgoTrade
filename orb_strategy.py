from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple
import datetime
import logging
from config_loader import CONFIG

class OrbStrategy:
    """
    Opening Range Breakout (ORB) Strategy.
    
    Concept:
        - Market direction is decided early.
        - Mark High & Low of the first N minutes (e.g., 15-30 mins).
        - Trade only when price breaks this range.
        
    Rules:
        - Break above High -> Bullish trade (BUY)
        - Break below Low -> Bearish trade (SELL)
        
    Risk Management:
        - Stop-loss: ~0.5% (or based on config)
        - Targets: Can expand significantly on trending days.
    """
    
    def __init__(self, kite_client, symbol: str):
        self.kite = kite_client
        self.symbol = symbol
        self.time_frame_minutes = CONFIG.orb_time_frame
        self.buffer_percent = CONFIG.orb_buffer_percent
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        self.orb_high = None
        self.orb_low = None
        self.range_calculated = False
        self.range_date = None


    def _reset_range_for_new_session(self, now: datetime.datetime) -> None:
        """Reset ORB range once trading moves to a new date."""
        current_date = now.date()
        if self.range_date is not None and self.range_date != current_date:
            self.orb_high = None
            self.orb_low = None
            self.range_calculated = False
            self.range_date = None

    def fetch_instrument_token(self) -> int:
        """
        Resolve symbol to instrument token.
        """
        try:
            self.logger.info(f"Fetching instrument token for {self.symbol}")
            instruments = self.kite.instruments("NSE")
            for instrument in instruments:
                if instrument['tradingsymbol'] == self.symbol.split(':')[-1]: # Handle NSE:INFY vs INFY
                    self.logger.info(f"Found token {instrument['instrument_token']} for {self.symbol}")
                    return instrument['instrument_token']
            
            self.logger.error(f"Instrument token not found for {self.symbol}")
            return None
        except Exception as e:
            self.logger.error(f"Error fetching instrument token: {e}")
            return None
        
    def fetch_historical_data(self, from_date: datetime.datetime, to_date: datetime.datetime, interval: str = "minute") -> list:
        """
        Fetch historical data for the given period.
        """
        instrument_token = self.fetch_instrument_token()
        
        try:
            return self.kite.historical_data(instrument_token, from_date, to_date, interval)
        except Exception as e:
            self.logger.error(f"Error fetching historical data: {e}")
            return []

    def calculate_opening_range(self, current_time: Optional[datetime.datetime] = None) -> Tuple[Optional[float], Optional[float]]:
        """
        Calculate the High and Low of the opening range.
        Args:
            current_time (datetime, optional): Time to use as 'now' for backtesting.
        """
        
        # Use provided time or current system time
        now = current_time if current_time else datetime.datetime.now()
        self._reset_range_for_new_session(now)
        market_start_time = now.replace(hour=9, minute=15, second=0, microsecond=0)
        
        # Ensure we are past the ORB duration
        orb_end_time = market_start_time + datetime.timedelta(minutes=self.time_frame_minutes)
        
        if now < orb_end_time:
             self.logger.info("Market has not been open long enough for ORB calculation.")
             # For testing, we might want to proceed if we can mock the time check
             # but strictly speaking, in live trading, we wait.
             return None, None

        data = self.fetch_historical_data(market_start_time, orb_end_time)
        
        if not data:
            self.logger.warning("No data fetched for opening range.")
            return None, None
            
        highs = [candle.get('high', 0) for candle in data]
        lows = [candle.get('low', float('inf')) for candle in data]
        
        if not highs or not lows:
             return None, None

        self.orb_high = max(highs)
        self.orb_low = min(lows)
        self.range_calculated = True
        self.range_date = now.date()

        self.logger.info(f"ORB Calculated: High={self.orb_high}, Low={self.orb_low}")
        return self.orb_high, self.orb_low

    def check_signal(self, current_price: float, current_time: Optional[datetime.datetime] = None) -> Optional[str]:
        """
        Check for breakout signals.
        Returns 'BUY', 'SELL', or None.
        """
        now = current_time if current_time else datetime.datetime.now()
        self._reset_range_for_new_session(now)

        if not self.range_calculated:
            self.calculate_opening_range(now)
            
        if not self.range_calculated or self.orb_high is None or self.orb_low is None:
            return None
            
        # Apply buffer if configured
        buy_trigger = self.orb_high * (1 + self.buffer_percent / 100)
        sell_trigger = self.orb_low * (1 - self.buffer_percent / 100)
        
        if current_price > buy_trigger:
            return "BUY"
        elif current_price < sell_trigger:
            return "SELL"
            
        return None

    def calculate_signal_strength(self, current_price: float, signal: str) -> float:
        """
        Calculate the strength of the breakout signal.
        Strength = abs(Current Price - FLip Level) / Range
        """
        if not self.orb_high or not self.orb_low:
            return 0.0
            
        orb_range = self.orb_high - self.orb_low
        if orb_range == 0:
            return 0.0 # Avoid division by zero
            
        level = self.orb_high if signal == "BUY" else self.orb_low
        strength = abs(current_price - level) / orb_range
        return strength
