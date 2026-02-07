"""Configuration settings for AlgoTrade.

Prefer setting these values via environment variables in production.
"""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class TradingConfig:
    api_key: str = os.getenv("KITE_API_KEY", "izqxg0prkp10xfl0")
    api_secret: str = os.getenv("KITE_API_SECRET", "v1h661qjaupf2kcd8958xbt2vzla3tom")
    access_token: str = os.getenv("KITE_ACCESS_TOKEN", "hFV5Ogw60D10j9YQEGK2MCqnvsJsTxNn")
    trading_pair: str = os.getenv("TRADING_PAIR", "NSE:INFY")
    order_size: int = int(os.getenv("ORDER_SIZE", "1"))
    stop_loss: float = float(os.getenv("STOP_LOSS", "0.05"))
    take_profit: float = float(os.getenv("TAKE_PROFIT", "0.10"))
    orb_time_frame: int = int(os.getenv("ORB_TIME_FRAME", "15"))
    orb_buffer_percent: float = float(os.getenv("ORB_BUFFER_PERCENT", "0.0"))
    max_trades_per_day: int = int(os.getenv("MAX_TRADES_PER_DAY", "1"))
    
    # NIFTY 50 Symbols (Subset for demonstration/speed, can be expanded)
    nifty_50_symbols: tuple = (
        "NSE:RELIANCE", "NSE:HDFCBANK", "NSE:INFY", "NSE:ICICIBANK", "NSE:TCS", 
        "NSE:ITC", "NSE:KOTAKBANK", "NSE:LTIM", "NSE:LT", "NSE:AXISBANK",
        "NSE:SBIN", "NSE:BHARTIARTL", "NSE:BAJFINANCE", "NSE:ASIANPAINT", "NSE:MARUTI"
    )


CONFIG = TradingConfig()
