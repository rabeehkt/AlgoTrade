"""
Kite Connect MIS Market Order Function

This module provides a function to place an MIS market order using Kite Connect API
and returns the order_id and average_price.

Requires: pip install kiteconnect
"""

from kiteconnect import KiteConnect
from typing import Dict, Tuple, Any


def place_mis_market_order(
    kite: KiteConnect,
    symbol: str,
    quantity: int,
    side: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Place an MIS (Margin Intraday Square-off) market order using Kite Connect.
    
    Args:
        kite (KiteConnect): Authenticated KiteConnect instance
        symbol (str): Trading symbol (e.g., 'INFY', 'SBIN', 'RELIANCE')
        quantity (int): Number of shares to buy/sell
        side (str): 'BUY' or 'SELL'
        **kwargs: Additional optional parameters
            - tag (str): Order tag for tracking
            - disclosed_quantity (int): Disclosed quantity
    
    Returns:
        Dict[str, Any]: Dictionary containing:
            - order_id (str): The placed order ID
            - average_price (float): Average fill price of the order
            - status (str): Order execution status
            - filled_quantity (int): Quantity filled
            - pending_quantity (int): Quantity still pending
    
    Raises:
        Exception: If order placement fails
    
    Example:
        >>> from kiteconnect import KiteConnect
        >>> kite = KiteConnect(api_key="your_api_key")
        >>> # After authentication...
        >>> result = place_mis_market_order(
        ...     kite=kite,
        ...     symbol='INFY',
        ...     quantity=1,
        ...     side='BUY'
        ... )
        >>> print(f"Order ID: {result['order_id']}")
        >>> print(f"Average Price: {result['average_price']}")
    """
    
    try:
        # Place the market order with MIS product type
        order_response = kite.place_order(
            variety="regular",
            exchange="NSE",
            tradingsymbol=symbol,
            transaction_type=side,
            quantity=quantity,
            order_type="MARKET",
            product="MIS",  # MIS - Margin Intraday Square-off
            tag=kwargs.get("tag", None),
            disclosed_quantity=kwargs.get("disclosed_quantity", 0)
        )
        
        order_id = order_response.get("order_id")
        
        if not order_id:
            raise Exception("Order placement failed: No order_id returned")
        
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
            "pending_quantity": int(order_details.get("pending_quantity", quantity)),
            "symbol": symbol,
            "side": side,
            "quantity": quantity
        }
        
        return result
    
    except Exception as e:
        raise Exception(f"Error placing MIS market order: {str(e)}")


def get_order_average_price(kite: KiteConnect, order_id: str) -> float:
    """
    Retrieve the average price for an existing order.
    
    Args:
        kite (KiteConnect): Authenticated KiteConnect instance
        order_id (str): The order ID to fetch price for
    
    Returns:
        float: Average price of the order
    
    Raises:
        Exception: If order not found
    """
    orders = kite.orders()
    
    for order in orders:
        if order.get("order_id") == order_id:
            return float(order.get("average_price", 0))
    
    raise Exception(f"Order {order_id} not found")


# Example usage
if __name__ == "__main__":
    # Initialize Kite Connect
    kite = KiteConnect(api_key="your_api_key")
    
    # Generate login URL
    login_url = kite.login_url()
    print(f"Login URL: {login_url}")
    
    # After user logs in and you get the request token
    # kite.set_session_hook(request_token, secret)
    
    # Place MIS market order
    try:
        result = place_mis_market_order(
            kite=kite,
            symbol='INFY',
            quantity=1,
            side='BUY'
        )
        
        print(f"✓ Order placed successfully!")
        print(f"  Order ID: {result['order_id']}")
        print(f"  Average Price: ₹{result['average_price']:.2f}")
        print(f"  Status: {result['status']}")
        print(f"  Filled Quantity: {result['filled_quantity']}")
        
    except Exception as e:
        print(f"✗ Error: {e}")