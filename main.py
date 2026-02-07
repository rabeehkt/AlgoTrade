"""Simple entry point for placing MIS market orders and computing P&L.

This module intentionally keeps side effects minimal so it can be imported in tests.
"""

from typing import Optional, Tuple

from kiteconnect import KiteConnect

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


if __name__ == "__main__":
    print(
        "AlgoTrade utilities loaded. Import this module and call "
        "build_kite_client() / place_mis_order() with valid credentials."
    )
