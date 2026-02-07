"""Authentication helpers for Kite Connect session token exchange."""

import hashlib
from typing import Optional

import requests


class KiteAuthClient:
    """Client responsible for exchanging a request token for an access token."""

    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token: Optional[str] = None

    def initialize_kite(self) -> None:
        """Log initialization details (placeholder hook)."""
        print(f"Initializing Kite Connect with API Key: {self.api_key}")

    def get_access_token(self, request_token: str) -> Optional[str]:
        """Exchange the request token for an access token and return it."""
        url = "https://api.kite.trade/session/token"
        data = {
            "api_key": self.api_key,
            "request_token": request_token,
            "checksum": self._generate_checksum(request_token),
        }
        response = requests.post(url, data=data)
        if response.ok:
            self.access_token = response.json().get("data", {}).get("access_token")
            print("Access token retrieved successfully")
            return self.access_token

        print("Failed to get access token:", response.json())
        return None

    def _generate_checksum(self, request_token: str) -> str:
        payload = f"{self.api_key}{request_token}{self.api_secret}".encode()
        return hashlib.sha256(payload).hexdigest()


# Backward compatibility for existing imports.
KiteConnect = KiteAuthClient
