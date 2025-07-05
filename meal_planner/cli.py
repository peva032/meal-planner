#!/usr/bin/env python3
"""
Command-line interface for the Meal Planner application.
"""

import argparse
import sys
import subprocess
from pathlib import Path


def run_streamlit():
    """Run the Streamlit web application."""
    app_path = Path(__file__).parent / "streamlit_app.py"
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(app_path)
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit app: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nApplication stopped by user.")
        sys.exit(0)


def run_example():
    """Run the example usage script."""
    try:
        from meal_planner import DbClient, Unit
        
        print("🍽️ Meal Planner Database Example")
        print("=" * 40)
        
        # Create a temporary database
        db = DbClient("cli_example.db")
        
        # Add a sample meal
        ingredients = [
            ("pasta", 200, Unit.GRAM.value),
            ("tomato sauce", 1, Unit.JAR.value),
            ("garlic", 2, Unit.CLOVES.value)
        ]
        
        success = db.add_meal("Simple Pasta", "Quick pasta dish", ingredients)
        print(f"Added sample meal: {'✅' if success else '❌'}")
        
        # Show meals
        meals = db.get_all_meals()
        for meal_id, name, description in meals:
            print(f"\n🍽️ {name}")
            ingredients = db.get_meal_ingredients(meal_id)
            for ingredient_name, quantity, unit in ingredients:
                print(f"  • {ingredient_name}: {quantity} {unit}")
        
        # Clean up
        import os
        os.remove("cli_example.db")
        print("\n✅ Example completed successfully!")
        
    except Exception as e:
        print(f"Error running example: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Meal Planner - Plan meals and generate shopping lists",
        prog="meal-planner"
    )
    
    subparsers = parser.add_subparsers(
        dest="command", 
        help="Available commands",
        required=True
    )
    
    # Web app command
    web_parser = subparsers.add_parser(
        "web", 
        help="Start the web application"
    )
    web_parser.add_argument(
        "--port", 
        type=int, 
        default=8501,
        help="Port to run the web server on (default: 8501)"
    )
    
    # Example command
    example_parser = subparsers.add_parser(
        "example", 
        help="Run a quick example"
    )
    
    # Version command
    version_parser = subparsers.add_parser(
        "version", 
        help="Show version information"
    )
    
    args = parser.parse_args()
    
    if args.command == "web":
        print(f"Starting Meal Planner web application on port {args.port}...")
        run_streamlit()
    elif args.command == "example":
        run_example()
    elif args.command == "version":
        from meal_planner import __version__
        print(f"Meal Planner v{__version__}")


if __name__ == "__main__":
    main()
