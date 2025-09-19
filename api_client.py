"""
API client for ktpncook recipe operations
"""

import requests
from typing import List, Dict, Any, Optional
from auth import KtpncookAuth
from recipe import Recipe


class KtpncookAPIClient:
    """Client for interacting with ktpncook API"""

    MOBILE_BASE_URL = "https://mobile.kptncook.com"

    def __init__(self, auth: KtpncookAuth):
        """
        Initialize API client with authentication

        Args:
            auth: Authenticated KtpncookAuth instance
        """
        if not auth.is_authenticated():
            raise ValueError("Authentication required")
        self.auth = auth

    def get_favorites(self) -> List[str]:
        """
        Retrieve user's favorite recipe identifiers

        Returns:
            List of recipe identifiers
        """
        favorites_url = f"{self.auth.BASE_URL}/favorites"
        headers = self.auth.get_auth_headers()

        try:
            response = requests.get(favorites_url, headers=headers)
            response.raise_for_status()

            data = response.json()
            favorites = data.get("favorites", [])
            print(f"Found {len(favorites)} favorite recipes")
            return favorites

        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve favorites: {e}")
            return []

    def get_recipe_details(self, recipe_identifier: str) -> Optional[Recipe]:
        """
        Get detailed recipe information by identifier

        Args:
            recipe_identifier: Recipe identifier from favorites

        Returns:
            Recipe object or None if failed
        """
        search_url = f"{self.MOBILE_BASE_URL}/recipes/search?kptnkey={self.auth.kptn_key}&lang=de"

        headers = {
            "Content-Type": "application/json",
            **self.auth.get_auth_headers()
        }

        payload = [{"identifier": recipe_identifier}]

        try:
            response = requests.post(search_url, json=payload, headers=headers)
            response.raise_for_status()

            recipes = response.json()
            if recipes and len(recipes) > 0:
                return Recipe.from_api_data(recipes[0])
            else:
                print(f"No recipe found for identifier: {recipe_identifier}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Failed to get recipe details for {recipe_identifier}: {e}")
            return None

    def get_all_recipe_details(self, favorites: List[str]) -> List[Recipe]:
        """
        Get detailed information for all favorite recipes

        Args:
            favorites: List of recipe identifiers

        Returns:
            List of Recipe objects
        """
        detailed_recipes = []

        for i, identifier in enumerate(favorites, 1):
            print(f"Fetching details for recipe {i}/{len(favorites)}: {identifier}")
            recipe = self.get_recipe_details(identifier)

            if recipe:
                detailed_recipes.append(recipe)
            else:
                print(f"Skipping recipe {identifier} - failed to fetch details")

        return detailed_recipes