"""Simple entry point for placing MIS market orders and computing P&L.

This module intentionally keeps side effects minimal so it can be imported in tests.
"""

from typing import Optional, Tuple

from kiteconnect import KiteConnect
# from kite_trading import KiteConnect

from kite_orders import KiteOrderManager


def build_kite_client(api_key: str, access_token: str) -> KiteConnect:
    """Create an authenticated Kite client."""
    kite = KiteConnect(api_key=api_key)
    kite.set_access_token(access_token)
    return kite


def place_mis_order(
    kite: KiteConnect,
    symbol: str,
    quantity: int,
    side: str = "BUY",
    tag: Optional[str] = None,
) -> Tuple[str, float]:
    """Place an MIS market order and return order id + average price."""
    manager = KiteOrderManager(kite)
    result = manager.place_mis_market_order(
        symbol=symbol,
        quantity=quantity,
        side=side,
        tag=tag,
    )
    return result["order_id"], result["average_price"]


def calculate_pnl(entry_price: float, exit_price: float, quantity: int) -> float:
    """Compute realized P&L for a completed trade."""
    return (exit_price - entry_price) * quantity


from config import CONFIG
from orb_strategy import OrbStrategy
import time
import logging

def run_orb_bot():
    """Run the ORB strategy bot."""
    print("Starting ORB Strategy Bot...")
    
    if not CONFIG.api_key or not CONFIG.access_token:
        print("ERROR: API Key or Access Token is missing in config.py or environment variables.")
        return

    # Initialize Kite Client
    # NOTE: We now use access_token from config, NOT api_secret
    kite = build_kite_client(CONFIG.api_key, CONFIG.access_token)
    
    # Initialize Strategy
    strategy = OrbStrategy(kite, CONFIG.trading_pair)
    
    print(f"Tracking {CONFIG.trading_pair} for {CONFIG.orb_time_frame}min ORB...")
    
    # Main Loop (Simplified for demonstration)
    while True:
        try:
            # 1. Calculate Range if not done
            high, low = strategy.calculate_opening_range()
            
            if high and low:
                try:
                    # 2. Get Current Price
                    # Use kite.quote for real API
                    quote = strategy.kite.quote(CONFIG.trading_pair)
                    current_price = quote[CONFIG.trading_pair]['last_price']
                except Exception as e:
                    logging.error(f"Error fetching price: {e}")
                    current_price = None
                
                if current_price:
                    # 3. Check Signal
                    signal = strategy.check_signal(current_price)
                    
                    if signal:
                        print(f"Signal Detected: {signal} at {current_price}")
                        # Place Order Logic Here
                        # place_mis_order(kite, CONFIG.trading_pair, CONFIG.order_size, signal)
                        break # Exit after one trade for demo
            
            time.sleep(60) # Poll every minute
            
        except KeyboardInterrupt:
            print("Stopping Bot...")
            break
        except Exception as e:
            logging.error(f"Error in main loop: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_orb_bot()
