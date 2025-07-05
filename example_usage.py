#!/usr/bin/env python3
"""
Example usage of the DbClient for the meal planner application.
This script demonstrates how to use the database client programmatically.
"""

from db import DbClient
from units import Unit


def main():
    # Initialize database client
    db = DbClient("example_meal_planner.db")
    
    print("🍽️ Meal Planner Database Example")
    print("=" * 40)
    
    # Add some example meals
    print("\n📝 Adding example meals...")
    
    # Meal 1: Pasta Carbonara
    pasta_ingredients = [
        ("spaghetti", 400, Unit.GRAM.value),
        ("eggs", 4, Unit.PIECES.value),
        ("bacon", 200, Unit.GRAM.value),
        ("parmesan cheese", 100, Unit.GRAM.value),
        ("black pepper", 1, Unit.TEASPOON.value)
    ]
    
    success = db.add_meal(
        "Pasta Carbonara",
        "Classic Italian pasta with eggs, cheese, and bacon",
        pasta_ingredients
    )
    print(f"Added Pasta Carbonara: {'✅' if success else '❌'}")
    
    # Meal 2: Caesar Salad
    salad_ingredients = [
        ("romaine lettuce", 1, Unit.HEAD.value),
        ("parmesan cheese", 50, Unit.GRAM.value),
        ("croutons", 1, Unit.CUP.value),
        ("caesar dressing", 3, Unit.TABLESPOON.value),
        ("anchovy fillets", 4, Unit.PIECES.value)
    ]
    
    success = db.add_meal(
        "Caesar Salad",
        "Fresh romaine lettuce with caesar dressing and parmesan",
        salad_ingredients
    )
    print(f"Added Caesar Salad: {'✅' if success else '❌'}")
    
    # Meal 3: Chicken Stir Fry
    stirfry_ingredients = [
        ("chicken breast", 300, Unit.GRAM.value),
        ("bell peppers", 2, Unit.PIECES.value),
        ("onion", 1, Unit.PIECE.value),
        ("soy sauce", 3, Unit.TABLESPOON.value),
        ("rice", 200, Unit.GRAM.value),
        ("garlic", 3, Unit.CLOVES.value),
        ("ginger", 1, Unit.TEASPOON.value)
    ]
    
    success = db.add_meal(
        "Chicken Stir Fry",
        "Quick and healthy chicken stir fry with vegetables",
        stirfry_ingredients
    )
    print(f"Added Chicken Stir Fry: {'✅' if success else '❌'}")
    
    # Display all meals
    print("\n📋 All meals in database:")
    meals = db.get_all_meals()
    for meal_id, name, description in meals:
        print(f"\n🍽️ {name} (ID: {meal_id})")
        print(f"   Description: {description}")
        
        # Get ingredients for this meal
        ingredients = db.get_meal_ingredients(meal_id)
        print("   Ingredients:")
        for ingredient_name, quantity, unit in ingredients:
            print(f"   • {ingredient_name}: {quantity} {unit}")
    
    # Generate shopping list for multiple meals
    print("\n🛒 Shopping list for Pasta Carbonara + Caesar Salad:")
    meal_ids = [meal[0] for meal in meals[:2]]  # First two meals
    shopping_list = db.generate_shopping_list(meal_ids)
    
    for ingredient_name, total_quantity, unit in shopping_list:
        print(f"• {ingredient_name}: {total_quantity} {unit}")
    
    # Show all ingredients in database
    print(f"\n📦 Total unique ingredients in database: {len(db.get_all_ingredients())}")
    
    # Clean up - remove the example database
    import os
    if os.path.exists("example_meal_planner.db"):
        os.remove("example_meal_planner.db")
        print("\n🧹 Cleaned up example database")


if __name__ == "__main__":
    main()
