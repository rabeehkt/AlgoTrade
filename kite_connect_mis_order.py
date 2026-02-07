"""Backward-compatible wrappers around :mod:`kite_orders`.

Historically this module duplicated order placement logic. It now delegates to
`KiteOrderManager` so there is one source of truth.
"""

from typing import Any, Dict

from kiteconnect import KiteConnect

from kite_orders import KiteOrderManager


def place_mis_market_order(
    kite: KiteConnect,
    symbol: str,
    quantity: int,
    side: str,
    **kwargs,
) -> Dict[str, Any]:
    """Place an MIS market order and return normalized order details."""
    manager = KiteOrderManager(kite)
    return manager.place_mis_market_order(
        symbol=symbol,
        quantity=quantity,
        side=side,
        tag=kwargs.get("tag"),
        disclosed_quantity=kwargs.get("disclosed_quantity", 0),
    )


def get_order_average_price(kite: KiteConnect, order_id: str) -> float:
    """Retrieve average fill price for an existing order."""
    manager = KiteOrderManager(kite)
    return manager.get_order_average_price(order_id)
