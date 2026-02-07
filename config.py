"""Configuration settings for AlgoTrade.

Prefer setting these values via environment variables in production.
"""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class TradingConfig:
    api_key: str = os.getenv("KITE_API_KEY", "")
    api_secret: str = os.getenv("KITE_API_SECRET", "")
    trading_pair: str = os.getenv("TRADING_PAIR", "NSE:INFY")
    order_size: int = int(os.getenv("ORDER_SIZE", "1"))
    stop_loss: float = float(os.getenv("STOP_LOSS", "0.05"))
    take_profit: float = float(os.getenv("TAKE_PROFIT", "0.10"))


CONFIG = TradingConfig()
