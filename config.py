"""
AlgoTrade Configuration Module

Stores API credentials, trading parameters, and system settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Kite Connect API Configuration
KITE_API_KEY = os.getenv("KITE_API_KEY", "")
KITE_API_SECRET = os.getenv("KITE_API_SECRET", "")
KITE_USER_ID = os.getenv("KITE_USER_ID", "")

# Trading Configuration
DEFAULT_EXCHANGE = "NSE"
DEFAULT_PRODUCT = "MIS"
DEFAULT_ORDER_TYPE = "MARKET"

# Order Tags for tracking
ORDER_TAGS = {
    "manual": "manual_order",
    "algo": "algo_order",
    "test": "test_order"
}

# Risk Management
MAX_POSITION_SIZE = 5  # Maximum shares per order
MAX_DAILY_LOSS = 1000  # Maximum daily loss in rupees
STOP_LOSS_PERCENT = 2  # Default stop loss percentage

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "logs/algotrade.log"