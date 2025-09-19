"""
Authentication module for ktpncook API
"""

import os
import requests
from typing import Optional
from dotenv import load_dotenv


class KtpncookAuth:
    """Handles authentication with the ktpncook API"""

    BASE_URL = "https://api.production.kptncook.com"

    def __init__(self):
        """Initialize auth and load environment variables"""
        load_dotenv()
        self.access_token: Optional[str] = None
        self.kptn_key = os.getenv("KPTNCOOK_API_KEY")

        if not self.kptn_key:
            raise ValueError("KPTNCOOK_API_KEY not found in environment variables")

    def login_from_env(self) -> bool:
        """
        Authenticate using credentials from environment variables

        Returns:
            True if authentication successful, False otherwise
        """
        email = os.getenv("KPTNCOOK_EMAIL")
        password = os.getenv("KPTNCOOK_PASSWORD")

        if not email or not password:
            raise ValueError("KPTNCOOK_EMAIL and KPTNCOOK_PASSWORD must be set in environment variables")

        return self.login(email, password)

    def login(self, email: str, password: str) -> bool:
        """
        Authenticate with ktpncook API and store access token

        Args:
            email: User email
            password: User password

        Returns:
            True if authentication successful, False otherwise
        """
        login_url = f"{self.BASE_URL}/auth/login"

        headers = {
            "Content-Type": "application/json",
            "kptnkey": self.kptn_key
        }

        payload = {
            "email": email,
            "password": password
        }

        try:
            response = requests.post(login_url, json=payload, headers=headers)
            response.raise_for_status()

            data = response.json()
            self.access_token = data.get("accessToken")

            return self.access_token is not None

        except requests.exceptions.RequestException as e:
            print(f"Authentication failed: {e}")
            return False

    def get_auth_headers(self) -> dict:
        """
        Get headers with authentication token

        Returns:
            Dictionary with Token header
        """
        if not self.access_token:
            raise ValueError("Not authenticated. Call login() first.")

        return {"Token": self.access_token}

    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.access_token is not None