import hvac  # HashiCorp Vault API client for Python
import threading  # Used for thread-safe singleton implementation
import os  # Allows access to environment variables
import traceback  # Captures detailed error information
from colorama import Fore, Style  # Provides colored output for logging
from pathlib import Path

"""
Module Name: vault_mgr.py
Author: Gabe McWilliams
Organization: Darkly Creative LLC
Created: 2025
License: MIT (or your preferred license)

Description:
This module provides a thread-safe singleton class for managing HashiCorp Vault authentication
using token or certificate methods. Designed for use in secure infrastructure, ML pipelines,
and backend services.

Usage:
    from vault_manager import VaultManager
    vault = VaultManager(auth_method="cert")
    secret = vault.read_secret(mount_point="kv", path="my/secret")
"""

class VaultManager:
    _instance = None  # Stores the singleton instance of VaultManager
    _lock = threading.Lock()  # Ensures thread safety when creating an instance

    def __new__(cls, *args, **kwargs):
        """Creates a new instance of VaultManager if one does not already exist."""
        with cls._lock:  # Ensures thread safety
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.__initialized = False  # Ensure initialization
        return cls._instance

    def __init__(self, auth_method="cert", debug=False):
        """Initializes the Vault client, preventing re-initialization of an existing instance."""
        if not self.__initialized:  # Ensures the instance is initialized only once
            self.auth_method = auth_method.lower()  # Determines the authentication method ('token' or 'cert')
            self.debug = debug  # Set debug mode
            self.__client = self.get_client()  # Retrieves the appropriate client
            self.__initialized = True  # Marks initialization as complete

    def get_client(self) -> hvac.Client:

        if self.debug:
            self.print_vault_env()

        """Selects and initializes the Vault client based on the authentication method."""
        if self.auth_method == "cert":  # Uses certificate-based authentication if specified

            return self.get_cert_client()
        else:  # Defaults to token-based authentication
            return self.get_token_client()

    @staticmethod
    def get_token_client() -> hvac.Client:
        """Initializes and authenticates the Vault client using token authentication."""
        try:
            # Retrieve required environment variables for authentication
            vault_addr = os.environ.get("VAULT_ADDR")
            vault_token = os.environ.get("VAULT_TOKEN")
            vault_ca_cert = os.environ.get("VAULT_CACERT")
            vault_namespace = os.environ.get("VAULT_NAMESPACE")

            # Ensure necessary credentials are available
            if not vault_addr or not vault_token:
                raise ValueError("Missing required environment variables: VAULT_ADDR and/or VAULT_TOKEN.")

            # Create a Vault client instance
            client = hvac.Client(
                url=vault_addr,
                token=vault_token,
                verify=vault_ca_cert,  # TLS verification (None disables it)
                namespace=vault_namespace  # Optional namespace for Vault Enterprise
            )

            if vault_namespace:
                client.adapter.namespace = vault_namespace  # Explicitly set the namespace

            # Check if the authentication was successful
            if not client.is_authenticated():
                raise ValueError("Vault authentication failed. Please check your VAULT_TOKEN.")

            print(
                f" * {Fore.LIGHTYELLOW_EX}Vault Client{Style.RESET_ALL} is {Fore.GREEN}[AUTHENTICATED]{Style.RESET_ALL}: {client.is_authenticated()}"
            )
            return client  # Return the authenticated client

        except Exception as e:
            # Log error details and exit the application
            print(f"{Fore.RED}* [FAILED]{Style.RESET_ALL} to initialize Vault client: {traceback.format_exc()}")
            raise SystemExit(f"Error: {e}")

    @staticmethod
    def get_cert_client() -> hvac.Client:
        """Initializes and authenticates the Vault client using certificate-based authentication."""
        try:
            # Retrieve required environment variables for certificate authentication
            vault_addr = os.environ.get("VAULT_ADDR")
            vault_ca_cert = os.environ.get("VAULT_CACERT")
            vault_namespace = os.environ.get("VAULT_NAMESPACE")

            vault_client_cert = os.environ.get("VAULT_CLIENT_CERT")
            # vault_client_cert = Path(r'D:\certs\prefect_io\prefect_io_public.crt')
            vault_client_key = os.environ.get("VAULT_CLIENT_KEY")
            # vault_client_key = Path(r'D:\certs\prefect_io\prefect_io_private.key')

            # Ensure necessary credentials are available
            if not vault_addr or not vault_client_cert or not vault_client_key:
                raise ValueError(
                    "Missing required environment variables: VAULT_ADDR, VAULT_CLIENT_CERT, or VAULT_CLIENT_KEY."
                )

            assert os.path.isfile(vault_client_cert), f"Missing: {vault_client_cert}"
            assert os.path.isfile(vault_client_key), f"Missing: {vault_client_key}"

            # Create a Vault client instance using certificate authentication
            client = hvac.Client(
                url=vault_addr,
                cert=(vault_client_cert, vault_client_key),  # TLS client certificate and key
                verify=vault_ca_cert,  # TLS verification (None disables it)
                namespace=vault_namespace  # Optional namespace for Vault Enterprise
            )

            if vault_namespace:
                client.adapter.namespace = vault_namespace  # Explicitly set the namespace

            # Authenticate using the certificate authentication method
            auth_response = client.auth.cert.login()

            # Validate the authentication response
            if "auth" not in auth_response or not auth_response["auth"]["client_token"]:
                raise ValueError("Vault authentication using cert method failed.")

            print(
                f" * {Fore.LIGHTYELLOW_EX}Vault Client{Style.RESET_ALL} is {Fore.GREEN}[AUTHENTICATED]{Style.RESET_ALL}"
            )
            return client  # Return the authenticated client

        except Exception as e:
            # Log error details and exit the application
            print(f"{Fore.RED}* [FAILED]{Style.RESET_ALL} to initialize Vault client: {traceback.format_exc()}")
            raise SystemExit(f"Error: {e}")

    def read_secret(self, mount_point: str, path: str) -> dict:
        """Reads a secret from HashiCorp Vault at the specified mount point and path."""
        resp = self.__client.secrets.kv.read_secret(mount_point=mount_point, path=f'/{path}')
        return resp['data']['data']  # Extracts and returns the secret data

    @staticmethod
    def print_vault_env():
        print("\n=========== Vault Environment Diagnostics ===========\n")

        def check_env(var):
            return "[CONFIGURED]" if os.environ.get(var) else "[NOT SET]"

        print(f'VAULT_ADDR         : {check_env("VAULT_ADDR")}')
        print(f'VAULT_CLIENT_CERT  : {check_env("VAULT_CLIENT_CERT")}')
        print(f'VAULT_CLIENT_KEY   : {check_env("VAULT_CLIENT_KEY")}')
        print(f'VAULT_CACERT       : {check_env("VAULT_CACERT")}')
        print(f'SSL_CERT_FILE      : {check_env("SSL_CERT_FILE")}')

        print("\n=====================================================\n")

        try:
            cert_path = os.environ.get("VAULT_CLIENT_CERT", None)
            key_path = os.environ.get("VAULT_CLIENT_KEY", None)

            if cert_path and os.path.isfile(cert_path):
                with open(cert_path, "r") as f:
                    first_line = f.readline().strip()
                    if "BEGIN CERTIFICATE" in first_line:
                        print("Cert Preview: public.crt found")
                    else:
                        print("Cert Preview: (header not found or invalid)")

            if key_path and os.path.isfile(key_path):
                with open(key_path, "r") as f:
                    first_line = f.readline().strip()
                    if "PRIVATE KEY" in first_line:
                        print("Key Preview: private.key found")
                    else:
                        print("Key Preview: (header not found or invalid)")

        except Exception as e:
            print(f"Error reading cert/key preview: {e}")

