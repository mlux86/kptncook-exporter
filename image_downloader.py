"""
Image downloader for recipe step images
"""

import os
import requests
from typing import Dict, List, Optional
from urllib.parse import urlparse
from recipe import Recipe
import hashlib


class ImageDownloader:
    """Downloads and manages recipe step images"""

    def __init__(self, download_dir: str = "images"):
        """
        Initialize image downloader

        Args:
            download_dir: Directory to store downloaded images
        """
        self.download_dir = download_dir
        self.ensure_download_directory()

    def ensure_download_directory(self) -> None:
        """Create download directory if it doesn't exist"""
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
            print(f"Created image directory: {self.download_dir}")

    def get_image_filename(self, url: str, recipe_id: str, step_number: int) -> str:
        """
        Generate consistent filename for image

        Args:
            url: Image URL
            recipe_id: Recipe identifier
            step_number: Step number

        Returns:
            Local filename for the image
        """
        # Parse URL to get file extension
        parsed_url = urlparse(url)
        path = parsed_url.path
        extension = os.path.splitext(path)[1] or '.jpg'

        # Create hash of URL for uniqueness
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]

        # Format: recipeId_stepN_hash.ext
        filename = f"{recipe_id}_step{step_number:02d}_{url_hash}{extension}"
        return filename

    def download_image(self, url: str, filename: str) -> bool:
        """
        Download single image

        Args:
            url: Image URL to download
            filename: Local filename to save as

        Returns:
            True if download successful, False otherwise
        """
        filepath = os.path.join(self.download_dir, filename)

        # Skip if already exists
        if os.path.exists(filepath):
            return True

        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return True

        except requests.exceptions.RequestException as e:
            print(f"Failed to download image {url}: {e}")
            return False
        except IOError as e:
            print(f"Failed to save image {filepath}: {e}")
            return False

    def download_recipe_images(self, recipe: Recipe) -> Dict[int, str]:
        """
        Download all images for a recipe

        Args:
            recipe: Recipe object with steps and images

        Returns:
            Dictionary mapping step numbers to local image filenames
        """
        image_map = {}
        recipe_id = recipe.identifier[:12]  # Shorten for filename

        print(f"Downloading images for recipe: {recipe.title}")

        for step in recipe.steps:
            if not step.image_url:
                continue

            filename = self.get_image_filename(
                step.image_url, recipe_id, step.step_number
            )

            print(f"  Step {step.step_number}: {filename}")

            if self.download_image(step.image_url, filename):
                image_map[step.step_number] = filename
            else:
                print(f"  ✗ Failed to download step {step.step_number} image")

        print(f"  ✓ Downloaded {len(image_map)} images")
        return image_map

    def download_all_recipe_images(self, recipes: List[Recipe]) -> Dict[str, Dict[int, str]]:
        """
        Download images for multiple recipes

        Args:
            recipes: List of Recipe objects

        Returns:
            Dictionary mapping recipe IDs to their image maps
        """
        all_images = {}

        for i, recipe in enumerate(recipes, 1):
            print(f"\n[{i}/{len(recipes)}] Processing images for: {recipe.title}")
            image_map = self.download_recipe_images(recipe)
            all_images[recipe.identifier] = image_map

        total_images = sum(len(imgs) for imgs in all_images.values())
        print(f"\n✓ Downloaded {total_images} total images for {len(recipes)} recipes")

        return all_images

    def get_image_path(self, filename: str) -> str:
        """
        Get full path to downloaded image

        Args:
            filename: Image filename

        Returns:
            Full path to image file
        """
        return os.path.join(self.download_dir, filename)

    def cleanup_unused_images(self, used_filenames: List[str]) -> None:
        """
        Remove unused image files

        Args:
            used_filenames: List of filenames that should be kept
        """
        if not os.path.exists(self.download_dir):
            return

        all_files = set(os.listdir(self.download_dir))
        used_files = set(used_filenames)
        unused_files = all_files - used_files

        for filename in unused_files:
            filepath = os.path.join(self.download_dir, filename)
            try:
                os.remove(filepath)
                print(f"Removed unused image: {filename}")
            except OSError as e:
                print(f"Failed to remove {filename}: {e}")

        if unused_files:
            print(f"Cleaned up {len(unused_files)} unused images")