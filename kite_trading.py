"""
Kite Connect Trading Module for AlgoTrade

This module provides functions to place MIS market orders and manage trades
using the Kite Connect API from Zerodha.

Installation: pip install kiteconnect
"""

from kiteconnect import KiteConnect
from typing import Tuple, Dict, Optional
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def place_mis_market_order(
    kite: KiteConnect,
    symbol: str,
    quantity: int,
    side: str,
    tag: Optional[str] = None
) -> Dict[str, any]:
    """
    Place an MIS (Margin Intraday Square-off) market order using Kite Connect.
    
    Args:
        kite (KiteConnect): Authenticated KiteConnect instance
        symbol (str): Trading symbol (e.g., 'INFY', 'SBIN', 'RELIANCE')
        quantity (int): Number of shares to buy/sell
        side (str): 'BUY' or 'SELL'
        tag (str, optional): Tag for order tracking
    
    Returns:
        Dict containing:
            - order_id (str): The placed order ID
            - average_price (float): Average fill price
            - status (str): Order execution status
            - filled_quantity (int): Quantity filled
            - timestamp (str): Order placement time
    
    Raises:
        ValueError: If required parameters are invalid
        Exception: If order placement fails
    
    Example:
        >>> result = place_mis_market_order(
        ...     kite=kite,
        ...     symbol='INFY',
        ...     quantity=1,
        ...     side='BUY',
        ...     tag='algo_trade'
        ... )
        >>> print(f"Order ID: {result['order_id']}")
        >>> print(f"Average Price: {result['average_price']}")
    """
    
    # Validate inputs
    if not symbol or not isinstance(symbol, str):
        raise ValueError("Invalid symbol provided")
    if quantity <= 0:
        raise ValueError("Quantity must be greater than 0")
    if side not in ['BUY', 'SELL']:
        raise ValueError("Side must be 'BUY' or 'SELL'")
    
    try:
        logger.info(f"Placing MIS market order: {side} {quantity} {symbol}")
        
        # Place the market order
        order_response = kite.place_order(
            variety="regular",
            exchange="NSE",
            tradingsymbol=symbol,
            transaction_type=side,
            quantity=quantity,
            order_type="MARKET",
            product="MIS",
            tag=tag
        )
        
        order_id = order_response.get("order_id")
        
        if not order_id:
            raise Exception("Order placement failed: No order_id returned")
        
        logger.info(f"Order placed successfully. Order ID: {order_id}")
        
        # Fetch order details to get average price
        orders = kite.orders()
        
        order_details = None
        for order in orders:
            if order.get("order_id") == order_id:
                order_details = order
                break
        
        if not order_details:
            raise Exception(f"Could not fetch details for order {order_id}")
        
        # Extract relevant information
        result = {
            "order_id": order_id,
            "average_price": float(order_details.get("average_price", 0)),
            "status": order_details.get("status"),
            "filled_quantity": int(order_details.get("filled_quantity", 0)),
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(
            f"Order {order_id}: Average Price: ₹{result['average_price']:.2f}, "
            f"Status: {result['status']}"
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Error placing MIS market order for {symbol}: {str(e)}")
        raise


def get_order_details(kite: KiteConnect, order_id: str) -> Dict[str, any]:
    """
    Retrieve detailed information about a specific order.
    
    Args:
        kite (KiteConnect): Authenticated KiteConnect instance
        order_id (str): The order ID to fetch
    
    Returns:
        Dict with order details including average_price
    
    Raises:
        Exception: If order not found
    """
    try:
        orders = kite.orders()
        
        for order in orders:
            if order.get("order_id") == order_id:
                return {
                    "order_id": order_id,
                    "average_price": float(order.get("average_price", 0)),
                    "status": order.get("status"),
                    "filled_quantity": int(order.get("filled_quantity", 0)),
                    "pending_quantity": int(order.get("pending_quantity", 0)),
                    "tradingsymbol": order.get("tradingsymbol"),
                    "transaction_type": order.get("transaction_type"),
                    "quantity": int(order.get("quantity", 0))
                }
        
        raise Exception(f"Order {order_id} not found")
    
    except Exception as e:
        logger.error(f"Error fetching order details for {order_id}: {str(e)}")
        raise


def cancel_order(kite: KiteConnect, order_id: str, variety: str = "regular") -> bool:
    """
    Cancel a pending order.
    
    Args:
        kite (KiteConnect): Authenticated KiteConnect instance
        order_id (str): The order ID to cancel
        variety (str): Order variety (default: "regular")
    
    Returns:
        bool: True if cancellation was successful
    """
    try:
        logger.info(f"Attempting to cancel order: {order_id}")
        kite.cancel_order(variety=variety, order_id=order_id)
        logger.info(f"Order {order_id} cancelled successfully")
        return True
    except Exception as e:
        logger.error(f"Error cancelling order {order_id}: {str(e)}")
        raise


def get_average_price(kite: KiteConnect, order_id: str) -> float:
    """
    Get the average price for a specific order.
    
    Args:
        kite (KiteConnect): Authenticated KiteConnect instance
        order_id (str): The order ID
    
    Returns:
        float: Average price of the order
    """
    details = get_order_details(kite, order_id)
    return details["average_price"]


# Example usage
if __name__ == "__main__":
    from kiteconnect import KiteConnect
    
    # Initialize Kite Connect
    kite = KiteConnect(api_key="your_api_key")
    
    # Generate login URL and authenticate
    # login_url = kite.login_url()
    # After user logs in and you get the request token
    # kite.set_access_token("your_access_token")
    
    # Example: Place an MIS market order
    try:
        result = place_mis_market_order(
            kite=kite,
            symbol='INFY',
            quantity=1,
            side='BUY',
            tag='algo_trade'
        )
        
        print(f"✓ Order placed successfully!")
        print(f"  Order ID: {result['order_id']}")
        print(f"  Average Price: ₹{result['average_price']:.2f}")
        print(f"  Status: {result['status']}")
        print(f"  Filled Quantity: {result['filled_quantity']}")
        
    except Exception as e:
        print(f"✗ Error: {e}")