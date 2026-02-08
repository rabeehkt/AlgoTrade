"""Simple entry point for placing MIS market orders and computing P&L.

This module intentionally keeps side effects minimal so it can be imported in tests.
"""

from typing import Optional, Tuple

from kiteconnect import KiteConnect
# from kite_trading import KiteConnect

from kite_orders import KiteOrderManager

def normalize_tradingsymbol(symbol: str) -> str:
    """Return tradingsymbol without exchange prefix."""
    return symbol.split(":")[-1]


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


from config_loader import CONFIG
from orb_strategy import OrbStrategy
import time
import datetime
import logging

def run_orb_bot():
    """Run the Multi-Stock ORB strategy bot."""
    print("Starting Multi-Stock ORB Strategy Bot...")
    
    if not CONFIG.api_key or not CONFIG.access_token:
        print("ERROR: API Key or Access Token is missing in config.py.")
        return

    # Initialize Kite Client
    kite = build_kite_client(CONFIG.api_key, CONFIG.access_token)
    
    # Initialize Strategies for all symbols
    strategies = {}
    print(f"Initializing strategies for {len(CONFIG.nifty_50_symbols)} stocks...")
    for symbol in CONFIG.nifty_50_symbols:
        strategies[symbol] = OrbStrategy(kite, symbol)
        
    trades_taken_today = 0
    max_trades = CONFIG.max_trades_per_day
    
    print(f"Tracking {len(strategies)} stocks. Max Trades: {max_trades}")
    print("Waiting for market loop...")
    
    # Main Loop
    while True:
        try:
            current_time = datetime.datetime.now()
            
            # 1. Update ORB Ranges if needed (Once per day logic handled inside strategy)
            # We can do this sequentially as it only hits API if not calculated
            # To avoid hitting rate limits on startup, maybe adding a small delay or check
            
            # 2. Fetch Quotes for ALL symbols in one go
            # Kite quote takes list of symbols
            # quote_map = kite.quote(CONFIG.nifty_50_symbols) 
            # Note: kite.quote might fail if too many symbols? Limit usually 500? Nifty 50 is fine.
            try:
                quote_map = kite.quote(CONFIG.nifty_50_symbols)
            except Exception as e:
                logging.error(f"Error fetching quotes: {e}")
                time.sleep(5)
                continue
                
            potential_signals = []
            
            for symbol, strategy in strategies.items():
                if symbol not in quote_map:
                    continue
                    
                ltp = quote_map[symbol]['last_price']
                
                # Ensure ORB levels are calculated
                if not strategy.range_calculated:
                    # Attempt to calculate (will fetch history)
                    # This might be slow on first run loop
                    strategy.calculate_opening_range()
                    
                # Check for Signal
                signal = strategy.check_signal(ltp)
                if signal:
                    strength = strategy.calculate_signal_strength(ltp, signal)
                    potential_signals.append({
                        'symbol': symbol,
                        'signal': signal,
                        'strength': strength,
                        'price': ltp
                    })
            
            # 3. Rank and Execute
            if potential_signals and trades_taken_today < max_trades:
                # Sort by strength
                potential_signals.sort(key=lambda x: x['strength'], reverse=True)
                
                # Log Candidates
                print(f"\n--- Candidates at {current_time.strftime('%H:%M:%S')} ---")
                for i, sig in enumerate(potential_signals[:3]):
                     print(f"  {i+1}. {sig['symbol']} [{sig['signal']}] Strength: {sig['strength']:.4f}")

                # Execute Best Trade
                best_signal = potential_signals[0]
                symbol = best_signal['symbol']
                
                # Check if we already traded this symbol? 
                # For simplicity, assuming 1 trade per day global or per stock? 
                # Requirements said "max one trade per day" (global).
                
                print(f">>> TRIGGER BUY/SELL for {symbol} ({best_signal['signal']}) @ {best_signal['price']}")
                
                # Place Order
                try:
                    tradingsymbol = normalize_tradingsymbol(symbol)
                    order_id, avg_price = place_mis_order(
                        kite,
                        tradingsymbol,
                        CONFIG.order_size,
                        best_signal['signal']
                    )
                    print(f"Order Placed: {order_id} @ {avg_price}")
                    trades_taken_today += 1
                    
                    # Store state to manage exit? 
                    # For V1, we just place order. exit management is usually separate loop or updates.
                    # We can add a simple exit manager later.
                    
                except Exception as e:
                    logging.error(f"Order Placement Failed: {e}")

            time.sleep(10) # Poll every 10 seconds
            
        except KeyboardInterrupt:
            print("Stopping Bot...")
            break
        except Exception as e:
            logging.error(f"Error in main loop: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_orb_bot()
