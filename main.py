#!/usr/bin/env python3
"""
Ktpncook Recipe Exporter

Exports all favorite recipes from ktpncook.com as PDF files.
Each PDF contains the recipe title, ingredients, steps with timing,
and step images.
"""

import os
import sys
from auth import KtpncookAuth
from api_client import KtpncookAPIClient
from image_downloader import ImageDownloader
from pdf_generator import PDFGenerator


def main():
    """Main application entry point"""
    print("Ktpncook Recipe Exporter")
    print("========================")

    # Initialize authentication
    auth = KtpncookAuth()

    print("Authenticating...")
    try:
        if auth.login_from_env():
            print("✓ Authentication successful")
        else:
            print("✗ Authentication failed")
            sys.exit(1)
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
        sys.exit(1)

    # Initialize API client
    client = KtpncookAPIClient(auth)

    # Get favorites
    print("\nRetrieving favorite recipes...")
    favorites = client.get_favorites()

    if not favorites:
        print("No favorite recipes found or failed to retrieve favorites")
        sys.exit(1)

    # Get detailed recipe information
    print("\nFetching detailed recipe information...")
    detailed_recipes = client.get_all_recipe_details(favorites)

    print(f"\n✓ Retrieved {len(detailed_recipes)} recipes successfully")

    # Download images for all recipes
    print("\nDownloading recipe images...")
    image_downloader = ImageDownloader()
    recipe_images = image_downloader.download_all_recipe_images(detailed_recipes)

    # Generate PDFs for all recipes
    print("\nGenerating PDF files...")
    export_dir = "export"
    pdf_generator = PDFGenerator(output_dir=export_dir, image_downloader=image_downloader)
    generated_pdfs = pdf_generator.generate_all_recipe_pdfs(detailed_recipes, recipe_images)

    print(f"\n🎉 Export complete!")
    print(f"Generated {len(generated_pdfs)} recipe PDFs in '{export_dir}' directory")


if __name__ == "__main__":
    main()