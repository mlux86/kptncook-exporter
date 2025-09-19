"""
Recipe data model for ktpncook recipes
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Ingredient:
    """Represents a recipe ingredient with quantity and unit"""
    title: str
    quantity: Optional[float] = None
    measure: Optional[str] = None
    ingredient_id: Optional[str] = None

    @classmethod
    def from_api_data(cls, data: Dict[str, Any]) -> 'Ingredient':
        """Create Ingredient from API response data"""
        unit = data.get("unit", {})
        ingredient = data.get("ingredient", {})

        # Handle different API response formats:
        # Step ingredients: {"title": "...", "unit": {...}}
        # Main ingredients: {"ingredient": {"title": "..."}, "quantity": ...}
        if "title" in data:
            # Step ingredient format
            title = data.get("title", "Unknown ingredient")
        else:
            # Main ingredient format
            title = ingredient.get("title", "Unknown ingredient")

        return cls(
            title=title,
            quantity=unit.get("quantity"),
            measure=unit.get("measure"),
            ingredient_id=data.get("ingredientId")
        )


@dataclass
class RecipeStep:
    """Represents a single recipe step"""
    title: str
    ingredients: List[Ingredient]
    image_url: Optional[str] = None
    step_number: int = 0

    @classmethod
    def from_api_data(cls, data: Dict[str, Any], step_number: int) -> 'RecipeStep':
        """Create RecipeStep from API response data"""
        # Parse ingredients for this step
        step_ingredients = []
        for ing_data in data.get("ingredients", []):
            step_ingredients.append(Ingredient.from_api_data(ing_data))

        # Get image URL
        image_url = None
        if "image" in data and "url" in data["image"]:
            image_url = data["image"]["url"]

        return cls(
            title=data.get("title", ""),
            ingredients=step_ingredients,
            image_url=image_url,
            step_number=step_number
        )


@dataclass
class Recipe:
    """Complete recipe with all details"""
    identifier: str
    title: str
    preparation_time: int
    cooking_time: int
    steps: List[RecipeStep]
    recipe_type: Optional[str] = None
    author_comment: Optional[str] = None
    all_ingredients: Optional[List[Ingredient]] = None

    @classmethod
    def from_api_data(cls, data: Dict[str, Any]) -> 'Recipe':
        """Create Recipe from API response data"""
        # Parse steps
        steps = []
        all_ingredients_set = set()

        for i, step_data in enumerate(data.get("steps", []), 1):
            step = RecipeStep.from_api_data(step_data, i)
            steps.append(step)

            # Collect all ingredients mentioned in steps
            for ingredient in step.ingredients:
                if ingredient.ingredient_id:
                    all_ingredients_set.add(ingredient.ingredient_id)

        # Parse global ingredients list
        all_ingredients = []
        for ing_data in data.get("ingredients", []):
            ingredient_obj = ing_data.get("ingredient", {})
            all_ingredients.append(Ingredient(
                title=ingredient_obj.get("title", "Unknown"),
                quantity=ing_data.get("quantity"),
                measure=ing_data.get("measure"),
                ingredient_id=ingredient_obj.get("_id", {}).get("$oid")
            ))

        return cls(
            identifier=data.get("_id", {}).get("$oid", ""),
            title=data.get("title", "Untitled Recipe"),
            preparation_time=data.get("preparationTime", 0),
            cooking_time=data.get("cookingTime", 0),
            recipe_type=data.get("rtype"),
            author_comment=data.get("authorComment"),
            steps=steps,
            all_ingredients=all_ingredients
        )

    def get_total_time(self) -> int:
        """Get total cooking + preparation time"""
        return self.preparation_time + self.cooking_time

    def get_step_images(self) -> List[str]:
        """Get all step image URLs"""
        return [step.image_url for step in self.steps if step.image_url]

    def get_all_step_ingredients(self) -> List[Ingredient]:
        """Get all ingredients used in steps"""
        ingredients = []
        for step in self.steps:
            ingredients.extend(step.ingredients)
        return ingredients