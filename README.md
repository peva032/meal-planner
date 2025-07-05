# Meal Planner

A simple Streamlit application for planning meals and generating shopping lists.

## Features

- **Add Meals**: Create new meals with their ingredients and quantities
- **Standardized Units**: Uses predefined metric units for consistency
- **Generate Shopping Lists**: Select multiple meals and get an aggregated shopping list
- **View Meals**: Browse all stored meals and their ingredients
- **Data Persistence**: Uses DuckDB for local data storage

## Installation

This project uses `uv` for package management. Make sure you have `uv` installed.

```bash
# Clone the repository
git clone <repository-url>
cd meal-planner

# Install dependencies (if not already done)
uv sync
```

### Installing as a Package

You can also install the meal planner as a package:

```bash
# Install in development mode
uv pip install -e .

# Or install from PyPI (when published)
pip install meal-planner
```

## Usage

### Web Application

Run the Streamlit web application:

```bash
# Using the app.py entry point
uv run streamlit run app.py

# Or using the CLI
uv run python -m meal_planner web

# Or if installed as package
meal-planner web
```

The application will be available at `http://localhost:8501`.

### Command Line Interface

The package includes a CLI with several commands:

```bash
# Show version
meal-planner version

# Run example
meal-planner example

# Start web application
meal-planner web

# Or using module syntax
python -m meal_planner version
python -m meal_planner example
python -m meal_planner web
```

## Database

The application uses DuckDB to store data locally in a file called `meal_planner.db`. This file will be created automatically when you first run the application.

## How to Use

1. **Add Meal**: 
   - Navigate to the "Add Meal" page
   - Enter a meal name and optional description
   - Add ingredients one by one with their quantities and units
   - Save the meal

2. **Generate Shopping List**:
   - Navigate to the "Generate Shopping List" page
   - Select one or more meals from the list
   - View the aggregated shopping list
   - Download the shopping list as a CSV file

3. **View Meals**:
   - Navigate to the "View Meals" page
   - Browse all stored meals and their ingredients

## Database Schema

The application uses three tables:
- `meals`: Stores meal information (id, name, description)
- `ingredients`: Stores ingredient information (id, name, unit)
- `meal_ingredients`: Links meals to ingredients with quantities

## Project Structure

```
meal-planner/
├── meal_planner/              # Main Python package
│   ├── __init__.py           # Package initialization
│   ├── __main__.py           # Module entry point
│   ├── cli.py                # Command-line interface
│   ├── db.py                 # Database client class
│   ├── units.py              # Unit enum with standardized units
│   └── streamlit_app.py      # Streamlit web application
├── app.py                    # Entry point for Streamlit app
├── example_usage.py          # Example script demonstrating usage
├── pyproject.toml            # Package configuration
├── README.md                 # This file
└── meal_planner.db           # DuckDB database (created automatically)
```

## DbClient Class

The database operations are encapsulated in the `DbClient` class in `db.py`. Key methods include:

- `add_meal(name, description, ingredients)`: Add a new meal
- `get_all_meals()`: Retrieve all meals
- `get_meal_ingredients(meal_id)`: Get ingredients for a specific meal
- `generate_shopping_list(meal_ids)`: Generate aggregated shopping list
- `delete_meal(meal_id)`: Delete a meal
- `update_meal(meal_id, name, description, ingredients)`: Update an existing meal

## Units

The application uses standardized metric units defined in the `Unit` enum:

**Weight/Mass:** gram (g), kilogram (kg)  
**Volume - Liquid:** millilitre (ml), litre (l)  
**Volume - Cooking:** teaspoon (tsp), tablespoon (tbsp), cup  
**Count:** piece, pieces, clove, cloves  
**Length:** centimetre (cm)  
**Special:** pinch, dash  
**Containers:** can, jar, bottle, packet, bag  
**Fresh Produce:** head, bunch, stalk, leaf, leaves  

## Example Usage

### Programmatic Usage

```python
from meal_planner import DbClient, Unit

# Create database client
db = DbClient("my_meals.db")

# Add a meal
ingredients = [
    ("pasta", 200, Unit.GRAM.value),
    ("tomato sauce", 1, Unit.JAR.value),
    ("garlic", 2, Unit.CLOVES.value)
]
db.add_meal("Simple Pasta", "Quick pasta dish", ingredients)

# Get all meals
meals = db.get_all_meals()
for meal_id, name, description in meals:
    print(f"{name}: {description}")

# Generate shopping list
shopping_list = db.generate_shopping_list([meal_id])
for ingredient, quantity, unit in shopping_list:
    print(f"- {ingredient}: {quantity} {unit}")
```

### Run Example Script

To see a complete example in action:

```bash
# Run the example script
uv run python example_usage.py

# Or use the CLI
meal-planner example
```

## Requirements

- Python 3.13
- Streamlit
- DuckDB
- Pandas
