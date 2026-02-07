"""High-level trading bot facade built on top of `KiteOrderManager`."""

from kiteconnect import KiteConnect

from kite_orders import KiteOrderManager


class AlgoTradingBot:
    def __init__(self, api_key: str, access_token: str):
        self.kite = KiteConnect(api_key=api_key)
        self.kite.set_access_token(access_token)
        self.orders = KiteOrderManager(self.kite)

    def execute_mis_market_order(self, symbol: str, quantity: int, side: str = "BUY") -> dict:
        return self.orders.place_mis_market_order(symbol=symbol, quantity=quantity, side=side)

    def cancel_order(self, order_id: str) -> dict:
        return self.orders.cancel_order(order_id)

    def get_orders(self) -> list:
        return self.orders.get_all_orders()
