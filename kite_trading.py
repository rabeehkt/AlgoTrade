"""Low-level HTTP client examples for Kite endpoints.

For production usage, prefer the official `kiteconnect` SDK + `kite_orders.py`.
"""

import logging
from typing import Any, Dict, Optional

import requests

logging.basicConfig(
    level=logging.DEBUG,
    filename="trading.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class KiteHttpClient:
    def __init__(self, api_key: str, access_token: str):
        self.api_key = api_key
        self.access_token = access_token
        self.base_url = "https://api.kite.trade"

    @property
    def _auth_headers(self) -> Dict[str, str]:
        return {"Authorization": f"Token {self.api_key}:{self.access_token}"}

    def place_mis_market_order(self, tradable_symbol: str, quantity: int) -> Optional[Dict[str, Any]]:
        try:
            order_endpoint = f"{self.base_url}/orders/mis"
            order_data = {
                "symbol": tradable_symbol,
                "quantity": quantity,
                "order_type": "market",
                "transaction_type": "BUY",
            }
            response = requests.post(order_endpoint, json=order_data, headers=self._auth_headers)
            response.raise_for_status()
            payload = response.json()
            logging.info("Order placed successfully: %s", payload)
            return payload
        except requests.exceptions.HTTPError as http_err:
            logging.error("HTTP error occurred: %s", http_err)
        except Exception as err:
            logging.error("An error occurred: %s", err)
        return None

    def get_order_details(self, order_id: str) -> Optional[Dict[str, Any]]:
        try:
            order_details_endpoint = f"{self.base_url}/orders/{order_id}"
            response = requests.get(order_details_endpoint, headers=self._auth_headers)
            response.raise_for_status()
            payload = response.json()
            logging.info("Retrieved order details: %s", payload)
            return payload
        except requests.exceptions.HTTPError as http_err:
            logging.error("HTTP error occurred: %s", http_err)
        except Exception as err:
            logging.error("An error occurred: %s", err)
        return None

    def cancel_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        try:
            cancel_endpoint = f"{self.base_url}/orders/{order_id}/cancel"
            response = requests.post(cancel_endpoint, headers=self._auth_headers)
            response.raise_for_status()
            payload = response.json()
            logging.info("Order cancelled successfully: %s", payload)
            return payload
        except requests.exceptions.HTTPError as http_err:
            logging.error("HTTP error occurred: %s", http_err)
        except Exception as err:
            logging.error("An error occurred: %s", err)
        return None

    def get_average_price(self, symbol: str) -> Optional[float]:
        try:
            average_price_endpoint = f"{self.base_url}/marketdata/{symbol}/quote"
            response = requests.get(average_price_endpoint)
            response.raise_for_status()
            data = response.json()
            average_price = data["last_price"]
            logging.info("Average price for %s: %s", symbol, average_price)
            return float(average_price)
        except requests.exceptions.HTTPError as http_err:
            logging.error("HTTP error occurred: %s", http_err)
        except Exception as err:
            logging.error("An error occurred: %s", err)
        return None


# Backward compatibility for existing imports.
KiteConnect = KiteHttpClient
