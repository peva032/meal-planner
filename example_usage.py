#!/usr/bin/env python3
"""
Example usage of the DbClient for the meal planner application.
This script demonstrates how to use the database client programmatically.
"""

from db import DbClient


def main():
    # Initialize database client
    db = DbClient("example_meal_planner.db")
    
    print("🍽️ Meal Planner Database Example")
    print("=" * 40)
    
    # Add some example meals
    print("\n📝 Adding example meals...")
    
    # Meal 1: Pasta Carbonara
    pasta_ingredients = [
        ("spaghetti", 400, "g"),
        ("eggs", 4, "pieces"),
        ("bacon", 200, "g"),
        ("parmesan cheese", 100, "g"),
        ("black pepper", 1, "tsp")
    ]
    
    success = db.add_meal(
        "Pasta Carbonara",
        "Classic Italian pasta with eggs, cheese, and bacon",
        pasta_ingredients
    )
    print(f"Added Pasta Carbonara: {'✅' if success else '❌'}")
    
    # Meal 2: Caesar Salad
    salad_ingredients = [
        ("romaine lettuce", 1, "head"),
        ("parmesan cheese", 50, "g"),
        ("croutons", 1, "cup"),
        ("caesar dressing", 3, "tbsp"),
        ("anchovy fillets", 4, "pieces")
    ]
    
    success = db.add_meal(
        "Caesar Salad",
        "Fresh romaine lettuce with caesar dressing and parmesan",
        salad_ingredients
    )
    print(f"Added Caesar Salad: {'✅' if success else '❌'}")
    
    # Meal 3: Chicken Stir Fry
    stirfry_ingredients = [
        ("chicken breast", 300, "g"),
        ("bell peppers", 2, "pieces"),
        ("onion", 1, "piece"),
        ("soy sauce", 3, "tbsp"),
        ("rice", 200, "g"),
        ("garlic", 3, "cloves"),
        ("ginger", 1, "tsp")
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
