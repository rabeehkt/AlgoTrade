# Authentication functionality for Kite Connect

import requests

class KiteConnect:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = None

    def initialize_kite(self):
        # Initialize the Kite Connect API
        print(f'Initializing Kite Connect with API Key: {self.api_key}')
        # Additional initialization code can be added here

    def get_access_token(self, request_token):
        # Exchange the request token for an access token
        url = 'https://api.kite.trade/session/token'
        data = {'api_key': self.api_key, 'request_token': request_token, 'checksum': self._generate_checksum(request_token)}
        response = requests.post(url, data=data)
        if response.ok:
            self.access_token = response.json().get('data').get('access_token')
            print('Access token retrieved successfully')
        else:
            print('Failed to get access token:', response.json())

    def _generate_checksum(self, request_token):
        # Generate checksum for the request
        import hashlib
        hash_object = hashlib.sha256(f'{self.api_key}{request_token}{self.api_secret}'.encode())
        return hash_object.hexdigest()