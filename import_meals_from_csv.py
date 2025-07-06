#!/usr/bin/env python3
"""
Script to import meals and ingredients from 'Meal Planner - Ingredients.csv' 
into the meal planner database using the current data model.
"""

import csv
import pandas as pd
from collections import defaultdict
from typing import Dict, List, Set
from meal_planner.db import DbClient
from meal_planner.models import Unit, Category

CSV_PATH = "Meal Planner - Ingredients.csv"

def normalize_unit(unit_str: str) -> str:
    """Normalize unit strings from CSV to match Unit enum values."""
    if not unit_str or unit_str.strip() == '':
        return Unit.ITEM.value
    
    unit_str = unit_str.strip().lower()
    
    # Map CSV unit variations to our Unit enum values
    unit_mapping = {
        # Weight/Mass
        'grams': Unit.GRAM.value,
        'gram': Unit.GRAM.value,
        'g': Unit.GRAM.value,
        'kg': Unit.KILOGRAM.value,
        'kilogram': Unit.KILOGRAM.value,
        'kilograms': Unit.KILOGRAM.value,
        
        # Volume - Liquid
        'ml': Unit.MILLILITRE.value,
        'millilitre': Unit.MILLILITRE.value,
        'millilitres': Unit.MILLILITRE.value,
        'l': Unit.LITRE.value,
        'litre': Unit.LITRE.value,
        'litres': Unit.LITRE.value,
        'litre(s)': Unit.LITRE.value,
        
        # Volume - Cooking
        'tsp': Unit.TEASPOON.value,
        'teaspoon': Unit.TEASPOON.value,
        'teaspoons': Unit.TEASPOON.value,
        'tbsp': Unit.TABLESPOON.value,
        'tablespoon': Unit.TABLESPOON.value,
        'tablespoons': Unit.TABLESPOON.value,
        'cup': Unit.CUP.value,
        'cups': Unit.CUP.value,
        
        # Count/Pieces
        'item(s)': Unit.ITEM.value,
        'item': Unit.ITEM.value,
        'items': Unit.ITEM.value,
        'piece': Unit.ITEM.value,
        'pieces': Unit.ITEM.value,
        'clove': Unit.CLOVE.value,
        'cloves': Unit.CLOVE.value,
        'cloves of garlic': Unit.CLOVE.value,
        
        # Length
        'cm': Unit.CENTIMETRE.value,
        'centimetre': Unit.CENTIMETRE.value,
        'centimetres': Unit.CENTIMETRE.value,
        
        # Special cooking units
        'pinch': Unit.PINCH.value,
        'pinches': Unit.PINCH.value,
        'dash': Unit.DASH.value,
        'dashes': Unit.DASH.value,
        
        # Package/Container units
        'can': Unit.CAN.value,
        'cans': Unit.CAN.value,
        'jar': Unit.JAR.value,
        'jars': Unit.JAR.value,
        'bottle': Unit.BOTTLE.value,
        'bottles': Unit.BOTTLE.value,
        'packet': Unit.PACKET.value,
        'packets': Unit.PACKET.value,
        'bag': Unit.BAG.value,
        'bags': Unit.BAG.value,
        
        # Fresh produce units
        'head': Unit.HEAD.value,
        'heads': Unit.HEAD.value,
        'bunch': Unit.BUNCH.value,
        'bunches': Unit.BUNCH.value,
        'stalk': Unit.STALK.value,
        'stalks': Unit.STALK.value,
        'sticks': Unit.STALK.value,  # Map "sticks" to stalk
        'leaf': Unit.LEAF.value,
        'leaves': Unit.LEAVES.value,
        'sheets': Unit.ITEM.value,  # Map sheets to items
        'rashers': Unit.ITEM.value,  # Map rashers to items
        'sprigs': Unit.BUNCH.value,  # Map sprigs to bunch
        'bulb': Unit.ITEM.value,  # Map bulb to item
        'punnet': Unit.PACKET.value,  # Map punnet to packet
        'nan': Unit.ITEM.value,  # Handle missing/NaN units
    }
    
    mapped_unit = unit_mapping.get(unit_str, None)
    if mapped_unit:
        return mapped_unit
    
    # If no mapping found, raise an error to handle properly
    raise ValueError(f"Unknown unit: '{unit_str}' - needs to be mapped to a Unit enum value")

def normalize_category(category_str: str) -> str:
    """Normalize category strings from CSV to match Category enum names."""
    if not category_str or category_str.strip() == '':
        return Category.NOT_SURE.name
    
    category_str = category_str.strip().lower()
    
    # Map CSV category variations to our Category enum names
    category_mapping = {
        'vegetables': Category.VEGETABLES.name,
        'bakery': Category.BAKERY.name,
        'fridge': Category.FRIDGE.name,
        'dry food': Category.DRY_FOOD.name,
        'asian': Category.ASIAN.name,
        'cans': Category.CANS.name,
        'spices': Category.SPICES.name,
        'treats': Category.TREATS.name,
        'not sure': Category.NOT_SURE.name,
        'baking': Category.BAKING.name,
        'frozen': Category.FROZEN.name,
        'organic store': Category.ORGANIC_STORE.name,
        'meat fridge': Category.MEAT_FRIDGE.name,
        'alcohol': Category.ALCOHOL.name,
        'other': Category.OTHER.name,
    }
    
    mapped_category = category_mapping.get(category_str, None)
    if mapped_category:
        return mapped_category
    
    # If no mapping found, raise an error to handle properly
    raise ValueError(f"Unknown category: '{category_str}' - needs to be mapped to a Category enum name")

def import_meals_from_csv(csv_path: str):
    """Import meals and their ingredients from CSV file into the database."""
    print(f"Starting import from: {csv_path}")
    
    # Initialize database client
    db = DbClient()
    
    # Dictionary to group ingredients by meal
    meals_data = defaultdict(list)
    
    # Track unknown units and categories for error reporting
    unknown_units = set()
    unknown_categories = set()
    
    try:
        # Read CSV file using pandas
        print(f"Reading CSV file...")
        df = pd.read_csv(csv_path)
        print(f"Successfully read {len(df)} rows from CSV")
        print(f"Columns found: {list(df.columns)}")
        
        # Validate required columns
        required_columns = ['Meal', 'Ingredient', 'Quantity', 'Unit']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Process each row
        valid_rows = 0
        skipped_rows = 0
        
        for index, row in df.iterrows():
            try:
                # Extract and clean data from row
                meal_name = str(row.get('Meal', '')).strip()
                ingredient_name = str(row.get('Ingredient', '')).strip()
                quantity_str = str(row.get('Quantity', '')).strip()
                unit_str = str(row.get('Unit', '')).strip()
                category_str = str(row.get('Category', '')).strip()
                notes = str(row.get('Notes', '')).strip()
                
                # Skip rows with missing required data
                if not meal_name or not ingredient_name or meal_name == 'nan' or ingredient_name == 'nan':
                    print(f"Row {index + 2}: Skipping - missing meal or ingredient name")
                    skipped_rows += 1
                    continue
                
                # Parse quantity
                try:
                    if quantity_str and quantity_str != 'nan':
                        quantity = float(quantity_str)
                        if quantity <= 0:
                            print(f"Row {index + 2}: Invalid quantity {quantity} for {ingredient_name}, using 1.0")
                            quantity = 1.0
                    else:
                        print(f"Row {index + 2}: Missing quantity for {ingredient_name}, using 1.0")
                        quantity = 1.0
                except ValueError:
                    print(f"Row {index + 2}: Invalid quantity '{quantity_str}' for {ingredient_name}, using 1.0")
                    quantity = 1.0
                
                # Normalize unit
                try:
                    normalized_unit = normalize_unit(unit_str)
                except ValueError as e:
                    unknown_units.add(unit_str)
                    print(f"Row {index + 2}: {e}")
                    continue
                
                # Normalize category
                try:
                    normalized_category = normalize_category(category_str)
                except ValueError as e:
                    unknown_categories.add(category_str)
                    print(f"Row {index + 2}: {e}")
                    continue
                
                # Add ingredient to meal data
                ingredient_data = {
                    'name': ingredient_name,
                    'quantity': quantity,
                    'unit': normalized_unit,
                    'category': normalized_category,
                    'notes': notes if notes and notes != 'nan' else None
                }
                
                meals_data[meal_name].append(ingredient_data)
                valid_rows += 1
                
            except Exception as e:
                print(f"Row {index + 2}: Unexpected error - {e}")
                skipped_rows += 1
                continue
        
        print(f"\nProcessing summary:")
        print(f"  Valid rows processed: {valid_rows}")
        print(f"  Rows skipped: {skipped_rows}")
        print(f"  Unique meals found: {len(meals_data)}")
        
        # Report unknown units and categories
        if unknown_units:
            print(f"\nUnknown units found (need to be mapped): {sorted(unknown_units)}")
        if unknown_categories:
            print(f"Unknown categories found (need to be mapped): {sorted(unknown_categories)}")
        
        # If there are unknown units or categories, stop here
        if unknown_units or unknown_categories:
            print("\nPlease update the normalize_unit() and normalize_category() functions to handle the unknown values.")
            return
        
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
    
    # Insert meals into database
    print(f"\nStarting database import...")
    success_count = 0
    error_count = 0
    
    for meal_name, ingredients in meals_data.items():
        try:
            # Convert ingredient data to tuples for add_meal method
            ingredient_tuples = [
                (ing['name'], ing['quantity'], ing['unit'], ing['category'])
                for ing in ingredients
            ]
            
            # Add meal to database
            meal_id = db.add_meal(
                name=meal_name,
                description="",  # No description in CSV
                ingredients=ingredient_tuples
            )
            
            if meal_id:
                print(f"✓ Added meal: {meal_name} (ID: {meal_id}) with {len(ingredients)} ingredients")
                success_count += 1
            else:
                print(f"✗ Failed to add meal: {meal_name}")
                error_count += 1
                
        except Exception as e:
            print(f"✗ Error adding meal '{meal_name}': {e}")
            error_count += 1
    
    print(f"\nImport completed:")
    print(f"  Successfully imported: {success_count} meals")
    print(f"  Failed to import: {error_count} meals")
    print(f"  Total ingredients imported: {sum(len(ingredients) for ingredients in meals_data.values())}")

def main():
    """Main function to run the import."""
    try:
        import_meals_from_csv(CSV_PATH)
    except Exception as e:
        print(f"Import failed: {e}")
        raise

if __name__ == "__main__":
    main()
