"""Runtime configuration loaded from environment variables.

This module intentionally avoids embedding any live credentials in source control.
"""

from dataclasses import dataclass
import os
from typing import List


def _get_env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return int(value)


def _get_env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return float(value)


def _get_env_symbols(name: str, default: List[str]) -> List[str]:
    value = os.getenv(name)
    if value is None:
        return default

    symbols = [symbol.strip() for symbol in value.split(",") if symbol.strip()]
    return symbols or default


@dataclass(frozen=True)
class Config:
    api_key: str = os.getenv("KITE_API_KEY", "")
    api_secret: str = os.getenv("KITE_API_SECRET", "")
    access_token: str = os.getenv("KITE_ACCESS_TOKEN", "")

    trading_pair: str = os.getenv("TRADING_PAIR", "NSE:INFY")
    nifty_50_symbols: List[str] = None

    orb_time_frame: int = _get_env_int("ORB_TIME_FRAME", 15)
    orb_buffer_percent: float = _get_env_float("ORB_BUFFER_PERCENT", 0.0)

    order_size: int = _get_env_int("ORDER_SIZE", 1)
    max_trades_per_day: int = _get_env_int("MAX_TRADES_PER_DAY", 1)

    def __post_init__(self):
        if self.nifty_50_symbols is None:
            object.__setattr__(
                self,
                "nifty_50_symbols",
                _get_env_symbols("NIFTY_50_SYMBOLS", [self.trading_pair]),
            )


CONFIG = Config()
