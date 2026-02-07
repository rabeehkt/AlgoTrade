"""
Kite Connect Order Management Module

This module provides functions to place and manage orders using Kite Connect API.
Part of the AlgoTrade algorithmic trading system.
"""

from kiteconnect import KiteConnect
from typing import Dict, Tuple, Any, Optional
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger(__name__)


class KiteOrderManager:
    """
    Manager class for placing and tracking orders via Kite Connect API.
    Handles MIS market orders and provides price tracking.
    """
    
    def __init__(self, kite: KiteConnect):
        """
        Initialize the KiteOrderManager.
        
        Args:
            kite (KiteConnect): Authenticated KiteConnect instance
        """
        self.kite = kite
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def place_mis_market_order(
        self,
        symbol: str,
        quantity: int,
        side: str,
        tag: Optional[str] = None,
        disclosed_quantity: int = 0
    ) -> Dict[str, Any]:
        """
        Place an MIS (Margin Intraday Square-off) market order.
        
        Args:
            symbol (str): Trading symbol (e.g., 'INFY', 'SBIN')
            quantity (int): Number of shares to trade
            side (str): 'BUY' or 'SELL'
            tag (str, optional): Order tag for tracking
            disclosed_quantity (int, optional): Disclosed quantity
        
        Returns:
            Dict[str, Any]: Order details including order_id and average_price
        
        Raises:
            ValueError: If invalid parameters
            Exception: If order placement fails
        """
        
        # Validate inputs
        if side not in ["BUY", "SELL"]:
            raise ValueError(f"Invalid side: {side}. Must be 'BUY' or 'SELL'")
        
        if quantity <= 0:
            raise ValueError(f"Quantity must be positive, got {quantity}")
        
        try:
            self.logger.info(
                f"Placing MIS {side} order: {symbol} x{quantity}"
            )
            
            # Place the market order
            order_response = self.kite.place_order(
                variety="regular",
                exchange="NSE",
                tradingsymbol=symbol,
                transaction_type=side,
                quantity=quantity,
                order_type="MARKET",
                product="MIS",
                tag=tag,
                disclosed_quantity=disclosed_quantity
            )
            
            order_id = order_response.get("order_id")
            
            if not order_id:
                raise Exception("Order placement failed: No order_id returned")
            
            self.logger.info(f"Order placed successfully. Order ID: {order_id}")
            
            # Fetch order details with average price
            order_details = self._get_order_details(order_id)
            
            return order_details
        
        except Exception as e:
            self.logger.error(f"Error placing MIS market order: {str(e)}")
            raise
    
    def _get_order_details(self, order_id: str) -> Dict[str, Any]:
        """
        Fetch detailed information for an order.
        
        Args:
            order_id (str): The order ID
        
        Returns:
            Dict[str, Any]: Order details
        
        Raises:
            Exception: If order not found
        """
        try:
            orders = self.kite.orders()
            
            for order in orders:
                if order.get("order_id") == order_id:
                    result = {
                        "order_id": order_id,
                        "average_price": float(order.get("average_price", 0)),
                        "status": order.get("status"),
                        "filled_quantity": int(order.get("filled_quantity", 0)),
                        "pending_quantity": int(order.get("pending_quantity", 0)),
                        "symbol": order.get("tradingsymbol"),
                        "side": order.get("transaction_type"),
                        "quantity": int(order.get("quantity", 0)),
                        "product": order.get("product"),
                        "order_timestamp": order.get("order_timestamp"),
                        "exchange_timestamp": order.get("exchange_timestamp")
                    }
                    return result
            
            raise Exception(f"Order {order_id} not found")
        
        except Exception as e:
            self.logger.error(f"Error fetching order details: {str(e)}")
            raise
    
    def get_order_average_price(self, order_id: str) -> float:
        """
        Get average price for an order.
        
        Args:
            order_id (str): The order ID
        
        Returns:
            float: Average price
        """
        order_details = self._get_order_details(order_id)
        return order_details["average_price"]
    
    def get_all_orders(self) -> list:
        """Get all orders for the session."""
        try:
            return self.kite.orders()
        except Exception as e:
            self.logger.error(f"Error fetching orders: {str(e)}")
            raise
    
    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """
        Cancel a pending order.
        
        Args:
            order_id (str): The order ID to cancel
        
        Returns:
            Dict[str, Any]: Cancel response
        """
        try:
            self.logger.info(f"Cancelling order: {order_id}")
            response = self.kite.cancel_order(
                variety="regular",
                order_id=order_id
            )
            self.logger.info(f"Order cancelled: {order_id}")
            return response
        except Exception as e:
            self.logger.error(f"Error cancelling order {order_id}: {str(e)}")
            raise


# Convenience function for simple use case
def place_mis_market_order(
    kite: KiteConnect,
    symbol: str,
    quantity: int,
    side: str,
    tag: Optional[str] = None
) -> Tuple[str, float]:
    """
    Simple function to place an MIS market order and return order_id and average_price.
    
    Args:
        kite (KiteConnect): Authenticated KiteConnect instance
        symbol (str): Trading symbol
        quantity (int): Quantity to trade
        side (str): 'BUY' or 'SELL'
        tag (str, optional): Order tag
    
    Returns:
        Tuple[str, float]: (order_id, average_price)
    
    Example:
        >>> order_id, avg_price = place_mis_market_order(kite, 'INFY', 1, 'BUY')
        >>> print(f"Order ID: {order_id}, Price: ₹{avg_price:.2f}")
    """
    manager = KiteOrderManager(kite)
    result = manager.place_mis_market_order(
        symbol=symbol,
        quantity=quantity,
        side=side,
        tag=tag
    )
    return result["order_id"], result["average_price"]