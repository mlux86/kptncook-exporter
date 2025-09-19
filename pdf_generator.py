"""
PDF generator for recipe documents
"""

import os
from typing import Dict, List, Optional
from fractions import Fraction
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from PIL import Image as PILImage
from recipe import Recipe, Ingredient
from image_downloader import ImageDownloader


class PDFGenerator:
    """Generates PDF documents for recipes"""

    def __init__(self, output_dir: str = ".", image_downloader: Optional[ImageDownloader] = None):
        """
        Initialize PDF generator

        Args:
            output_dir: Directory to save PDF files
            image_downloader: ImageDownloader instance for getting image paths
        """
        self.output_dir = output_dir
        self.image_downloader = image_downloader or ImageDownloader()
        self.ensure_output_directory()

        # Setup styles
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()

    def ensure_output_directory(self) -> None:
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def setup_custom_styles(self) -> None:
        """Define custom paragraph styles for the PDF"""
        # Recipe title style
        self.styles.add(ParagraphStyle(
            name='RecipeTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=12,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))

        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceBefore=12,
            spaceAfter=6,
            textColor=colors.darkgreen
        ))

        # Step title style
        self.styles.add(ParagraphStyle(
            name='StepTitle',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceBefore=8,
            spaceAfter=4,
            textColor=colors.darkred
        ))

        # Ingredient style
        self.styles.add(ParagraphStyle(
            name='Ingredient',
            parent=self.styles['Normal'],
            fontSize=10,
            leftIndent=20,
            bulletIndent=10
        ))

    def format_quantity(self, quantity: float) -> str:
        """Convert decimal quantities to readable fractions when appropriate"""
        # Double the quantity for 2 portions
        doubled = quantity * 2

        # If it's a whole number, return as integer
        if doubled == int(doubled):
            return str(int(doubled))

        # Convert to fraction
        frac = Fraction(doubled).limit_denominator(16)  # Limit to simple fractions

        # If the fraction is very close to the decimal, use the fraction
        if abs(float(frac) - doubled) < 0.01:
            if frac.numerator > frac.denominator:
                # Mixed number (e.g., 1 1/2 instead of 3/2)
                whole = frac.numerator // frac.denominator
                remainder = frac.numerator % frac.denominator
                if remainder == 0:
                    return str(whole)
                else:
                    return f"{whole} {remainder}/{frac.denominator}"
            else:
                # Simple fraction (e.g., 1/2, 2/3)
                return f"{frac.numerator}/{frac.denominator}"
        else:
            # If fraction doesn't represent the decimal well, use decimal with 1 decimal place
            return f"{doubled:.1f}".rstrip('0').rstrip('.')

    def format_ingredient(self, ingredient: Ingredient) -> str:
        """Format ingredient for display (scaled for 2 portions)"""
        if ingredient.quantity and ingredient.measure:
            formatted_quantity = self.format_quantity(ingredient.quantity)
            return f"{formatted_quantity} {ingredient.measure} {ingredient.title}"
        elif ingredient.quantity:
            formatted_quantity = self.format_quantity(ingredient.quantity)
            return f"{formatted_quantity} {ingredient.title}"
        else:
            return ingredient.title

    def add_recipe_header(self, story: List, recipe: Recipe) -> None:
        """Add recipe title and basic info to the story"""
        # Recipe title
        story.append(Paragraph(recipe.title, self.styles['RecipeTitle']))
        story.append(Spacer(1, 12))

        # Recipe info table
        info_data = []
        if recipe.recipe_type:
            info_data.append(['Typ:', recipe.recipe_type])

        if recipe.preparation_time > 0:
            info_data.append(['Vorbereitungszeit:', f"{recipe.preparation_time} Minuten"])

        if recipe.cooking_time > 0:
            info_data.append(['Kochzeit:', f"{recipe.cooking_time} Minuten"])

        total_time = recipe.get_total_time()
        if total_time > 0:
            info_data.append(['Gesamtzeit:', f"{total_time} Minuten"])

        if recipe.author_comment:
            info_data.append(['Beschreibung:', recipe.author_comment])

        if recipe.identifier:
            info_data.append(['Rezept-ID:', recipe.identifier])

        if info_data:
            info_table = Table(info_data, colWidths=[1.5*inch, 4*inch])
            info_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(info_table)
            story.append(Spacer(1, 12))

    def add_ingredients_section(self, story: List, recipe: Recipe) -> None:
        """Add ingredients section to the story"""
        if not recipe.all_ingredients:
            return

        story.append(Paragraph("Zutaten (für 2 Personen)", self.styles['SectionHeader']))

        for ingredient in recipe.all_ingredients:
            bullet_text = f"• {self.format_ingredient(ingredient)}"
            story.append(Paragraph(bullet_text, self.styles['Ingredient']))

        story.append(Spacer(1, 16))

    def add_recipe_image(self, story: List, image_path: str, max_width: float = 4*inch) -> None:
        """Add an image to the story with appropriate sizing"""
        if not os.path.exists(image_path):
            return

        try:
            # Get image dimensions
            with PILImage.open(image_path) as pil_img:
                img_width, img_height = pil_img.size

            # Calculate scaled dimensions
            if img_width > max_width:
                scale_factor = max_width / img_width
                new_width = max_width
                new_height = img_height * scale_factor
            else:
                new_width = img_width
                new_height = img_height

            # Add image to story
            img = Image(image_path, width=new_width, height=new_height)
            story.append(img)
            story.append(Spacer(1, 8))

        except Exception as e:
            print(f"Warning: Could not add image {image_path}: {e}")

    def add_steps_section(self, story: List, recipe: Recipe, recipe_images: Dict[int, str]) -> None:
        """Add cooking steps section to the story"""
        if not recipe.steps:
            return

        story.append(Paragraph("Anweisungen", self.styles['SectionHeader']))

        for step in recipe.steps:
            # Step title
            step_title = f"Schritt {step.step_number}: {step.title}"
            story.append(Paragraph(step_title, self.styles['StepTitle']))

            # Step image if available
            if step.step_number in recipe_images:
                image_filename = recipe_images[step.step_number]
                image_path = self.image_downloader.get_image_path(image_filename)
                self.add_recipe_image(story, image_path)

            # Step ingredients if any
            if step.ingredients:
                story.append(Paragraph("<b>Zutaten für diesen Schritt:</b>", self.styles['Normal']))
                for ingredient in step.ingredients:
                    ingredient_text = f"• {self.format_ingredient(ingredient)}"
                    story.append(Paragraph(ingredient_text, self.styles['Ingredient']))
                story.append(Spacer(1, 6))

            story.append(Spacer(1, 12))

    def generate_recipe_filename(self, recipe: Recipe) -> str:
        """Generate safe filename for recipe PDF"""
        # Clean title for filename
        safe_title = "".join(c for c in recipe.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_')

        # Truncate if too long
        if len(safe_title) > 50:
            safe_title = safe_title[:50]

        return f"{safe_title}.pdf"

    def generate_recipe_pdf(self, recipe: Recipe, recipe_images: Dict[int, str]) -> str:
        """
        Generate PDF for a single recipe

        Args:
            recipe: Recipe object to generate PDF for
            recipe_images: Dictionary mapping step numbers to image filenames

        Returns:
            Path to generated PDF file
        """
        filename = self.generate_recipe_filename(recipe)
        filepath = os.path.join(self.output_dir, filename)

        # Create PDF document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        # Build story
        story = []

        # Add recipe header
        self.add_recipe_header(story, recipe)

        # Add ingredients section
        self.add_ingredients_section(story, recipe)

        # Add steps section
        self.add_steps_section(story, recipe, recipe_images)

        # Build PDF
        doc.build(story)

        return filepath

    def generate_all_recipe_pdfs(
        self,
        recipes: List[Recipe],
        all_recipe_images: Dict[str, Dict[int, str]]
    ) -> List[str]:
        """
        Generate PDFs for all recipes

        Args:
            recipes: List of Recipe objects
            all_recipe_images: Dictionary mapping recipe IDs to their image maps

        Returns:
            List of generated PDF file paths
        """
        generated_files = []

        for i, recipe in enumerate(recipes, 1):
            print(f"Generating PDF {i}/{len(recipes)}: {recipe.title}")

            # Get images for this recipe
            recipe_images = all_recipe_images.get(recipe.identifier, {})

            try:
                pdf_path = self.generate_recipe_pdf(recipe, recipe_images)
                generated_files.append(pdf_path)
                print(f"  ✓ Generated: {os.path.basename(pdf_path)}")

            except Exception as e:
                print(f"  ✗ Failed to generate PDF for {recipe.title}: {e}")

        print(f"\n✓ Generated {len(generated_files)} PDFs successfully")
        return generated_files