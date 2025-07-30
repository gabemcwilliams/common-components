"""
MSAL Token Cache Manager with Persistent Storage
------------------------------------------------

This module provides the `MsalTokenCache` class to handle secure and reusable
OAuth2 token acquisition for Microsoft Graph API access. It uses the
`msal` and `msal-extensions` libraries to enable silent token reuse and refresh
based on persistent local storage across platforms (Windows, macOS, Linux).

Core Features:
--------------
- Uses MSAL's Device Code Flow to authenticate users
- Supports token caching with OS-specific backends:
    - Windows: DPAPI (FilePersistenceWithDataProtection)
    - macOS: Keychain
    - Linux/Other: Flat file
- Silently acquires tokens via refresh or cache reuse if available
- Decodes and displays token expiry time for audit/debugging
- Demonstrates calling the Microsoft Graph `/me` endpoint using access tokens

Use Cases:
----------
Ideal for CLI tools, admin utilities, or backend pipelines where:
- Secure Graph API access is needed without reauthenticating every run
- Local token caching avoids constant user interaction
- Tokens can be audited or rotated without secret management infrastructure

Dependencies:
-------------
- msal
- msal-extensions
- pyjwt
- requests

Author: Gabe McWilliams
"""

import msal
import jwt
import json
import sys
import requests
from datetime import datetime
from msal_extensions import *


class MsalTokenCache:
    def __init__(self, authority: str, client_id: str, client_secret: str) -> None:
        self.authority = authority
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_cache_file = "token_cache.bin"

    def msal_persistence(self) -> str:
        """Build a suitable persistence instance based on the current OS."""
        if sys.platform.startswith('win'):
            return FilePersistenceWithDataProtection(self.token_cache_file)
        if sys.platform.startswith('darwin'):
            return KeychainPersistence(self.token_cache_file, "my_service_name", "my_account_name")
        return FilePersistence(self.token_cache_file)

    def get_msal_app(self):
        persistence: str = self.msal_persistence()
        cache = PersistedTokenCache(persistence)
        return msal.PublicClientApplication(client_id=self.client_id, authority=self.authority, token_cache=cache)

    def get_accounts(self) -> list:
        app = self.get_msal_app()
        return app.get_accounts()

    def acquire_token_silent(self, scopes: list, account: str, force_refresh: bool = False) -> dict:
        app = self.get_msal_app()
        return app.acquire_token_silent_with_error(scopes=scopes, account=account, force_refresh=force_refresh)

    def initiate_device_flow(self, scopes: list):
        print("Initiating Device Code Flow...")
        app = self.get_msal_app()
        flow = app.initiate_device_flow(scopes=scopes)
        if "user_code" not in flow:
            raise ValueError("Failed to create device flow: %s" % json.dumps(flow, indent=4))
        print(flow["message"])
        return app.acquire_token_by_device_flow(flow)

    @staticmethod
    def decode_jwt_expiry(access_token: str):
        decoded_token = jwt.decode(access_token, options={"verify_signature": False})
        token_expiry = datetime.fromtimestamp(int(decoded_token['exp']))
        print(f"Token Expires at: {token_expiry}")
        return token_expiry

    @staticmethod
    def make_graph_request(resource: str, headers: dict) -> dict:
        return requests.get(resource, headers=headers).json()

    def refresh_token(self, username: str, scopes: list, graph_uri: str):
        accounts = self.get_accounts()

        for account in accounts:
            if account['username'] == username:
                print(f"Found account in MSAL Cache: {username}")
                result = self.acquire_token_silent(scopes, account)
                if not result or "access_token" not in result:
                    result = self.initiate_device_flow(scopes)
                break
        else:
            result = self.initiate_device_flow(scopes)

        if result and "access_token" in result:
            self.decode_jwt_expiry(result["access_token"])
            headers = {'Authorization': f'Bearer {result["access_token"]}', 'Content-Type': 'application/json'}
            query_results = self.make_graph_request(f"{graph_uri}/v1.0/me", headers)
            print(json.dumps(query_results, indent=2))

        return result
