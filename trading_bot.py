"""
Example AlgoTrade bot using Kite Connect MIS orders
"""

from kiteconnect import KiteConnect
from kite_trading import place_mis_market_order, get_order_details, cancel_order
from config import KITE_CONFIG, TRADING_CONFIG
import logging

logger = logging.getLogger(__name__)


class AlgoTradingBot:
    """Algorithmic trading bot using Kite Connect"""
    
    def __init__(self):
        """Initialize the trading bot"""
        self.kite = KiteConnect(api_key=KITE_CONFIG["api_key"])
        self.orders = {}
    
    def authenticate(self, access_token):
        """Authenticate with Kite Connect"""
        self.kite.set_access_token(access_token)
        logger.info("Authentication successful")
    
    def execute_buy_signal(self, symbol, quantity):
        """Execute a buy signal"""
        try:
            result = place_mis_market_order(
                kite=self.kite,
                symbol=symbol,
                quantity=quantity,
                side='BUY',
                tag=TRADING_CONFIG.get("tag", "algotrade")
            )
            
            self.orders[result["order_id"]] = {
                "symbol": symbol,
                "side": "BUY",
                "quantity": quantity,
                **result
            }
            
            logger.info(f"BUY order executed: {result['order_id']} @ ₹{result['average_price']:.2f}")
            return result
        
        except Exception as e:
            logger.error(f"Error executing BUY signal for {symbol}: {e}")
            raise
    
    def execute_sell_signal(self, symbol, quantity):
        """Execute a sell signal"""
        try:
            result = place_mis_market_order(
                kite=self.kite,
                symbol=symbol,
                quantity=quantity,
                side='SELL',
                tag=TRADING_CONFIG.get("tag", "algotrade")
            )
            
            self.orders[result["order_id"]] = {
                "symbol": symbol,
                "side": "SELL",
                "quantity": quantity,
                **result
            }
            
            logger.info(f"SELL order executed: {result['order_id']} @ ₹{result['average_price']:.2f}")
            return result
        
        except Exception as e:
            logger.error(f"Error executing SELL signal for {symbol}: {e}")
            raise
    
    def check_order_status(self, order_id):
        """Check status of an order"""
        try:
            details = get_order_details(self.kite, order_id)
            logger.info(f"Order {order_id}: {details['status']} @ ₹{details['average_price']:.2f}")
            return details
        except Exception as e:
            logger.error(f"Error checking order status: {e}")
            raise
    
    def cancel_pending_order(self, order_id):
        """Cancel a pending order"""
        try:
            cancel_order(self.kite, order_id)
            logger.info(f"Order {order_id} cancelled")
            return True
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            raise


# Example usage
if __name__ == "__main__":
    bot = AlgoTradingBot()
    # bot.authenticate("your_access_token")
    # result = bot.execute_buy_signal("INFY", 1)
    # print(result)