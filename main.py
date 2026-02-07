"""
AlgoTrade Main Module

Entry point for the algorithmic trading system.
Demonstrates usage of Kite Connect MIS market orders.
"""

from kiteconnect import KiteConnect
from kite_orders import KiteOrderManager, place_mis_market_order
from config import KITE_API_KEY
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def initialize_kite_connection(api_key: str) -> KiteConnect:
    """
    Initialize Kite Connect with API key.
    
    Args:
        api_key (str): Kite Connect API key
    
    Returns:
        KiteConnect: Authenticated Kite instance
    """
    kite = KiteConnect(api_key=api_key)
    logger.info(f"Kite Connect initialized with API key")
    return kite


def login_to_kite(kite: KiteConnect) -> None:
    """
    Generate login URL for Kite Connect authentication.
    
    Args:
        kite (KiteConnect): Kite instance
    """
    login_url = kite.login_url()
    logger.info(f"Login URL: {login_url}")
    print(f"\n📱 Open this URL to login: {login_url}\n")


def set_kite_session(kite: KiteConnect, request_token: str, secret: str) -> None:
    """
    Set Kite Connect session with authentication details.
    
    Args:
        kite (KiteConnect): Kite instance
        request_token (str): Request token from login redirect
        secret (str): API secret
    """
    try:
        data = kite.generate_session(request_token, api_secret=secret)
        kite.set_access_token(data["access_token"])
        logger.info("✓ Kite session established successfully")
    except Exception as e:
        logger.error(f"✗ Session setup failed: {e}")
        raise


def trade_example(kite: KiteConnect) -> None:
    """
    Example trading workflow using MIS market orders.
    
    Args:
        kite (KiteConnect): Authenticated Kite instance
    """
    logger.info("=" * 60)
    logger.info("AlgoTrade - MIS Market Order Example")
    logger.info("=" * 60)
    
    # Method 1: Using simple function
    try:
        logger.info("\n[Method 1] Using simple function:")
        order_id, avg_price = place_mis_market_order(
            kite=kite,
            symbol='INFY',
            quantity=1,
            side='BUY',
            tag='demo_order'
        )
        logger.info(f"✓ Order ID: {order_id}")
        logger.info(f"✓ Average Price: ₹{avg_price:.2f}")
    except Exception as e:
        logger.error(f"✗ Error in Method 1: {e}")
    
    # Method 2: Using KiteOrderManager class
    try:
        logger.info("\n[Method 2] Using KiteOrderManager class:")
        manager = KiteOrderManager(kite)
        
        result = manager.place_mis_market_order(
            symbol='RELIANCE',
            quantity=1,
            side='SELL',
            tag='algotrade_demo'
        )
        
        logger.info(f"✓ Full Order Details:")
        for key, value in result.items():
            logger.info(f"  {key}: {value}")
    except Exception as e:
        logger.error(f"✗ Error in Method 2: {e}")
    
    logger.info("\n" + "=" * 60)


if __name__ == "__main__":
    # Initialize
    kite = initialize_kite_connection(KITE_API_KEY)
    
    # Login (follow the printed URL)
    login_to_kite(kite)
    
    # After getting request_token from login redirect
    # Uncomment and set these values:
    # request_token = "your_request_token_from_redirect"
    # api_secret = "your_api_secret"
    # set_kite_session(kite, request_token, api_secret)
    
    # Run trading example
    # trade_example(kite)